"""Exact source/artifact identity and isolated certification build helpers."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
CERT_ROOT = REPO_ROOT / "certification"
CUSTOMER_REPOSITORY = "ruizengalways/fabric-customer"
FRAMEWORK_PIN = CERT_ROOT / "framework-executable.json"


class BootstrapError(RuntimeError):
    pass


def _run(
    command: list[str],
    *,
    label: str,
    cwd: Path = REPO_ROOT,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            check=True,
            text=True,
            capture_output=capture,
        )
    except FileNotFoundError as exc:
        raise BootstrapError(f"{label} executable was not found") from exc
    except subprocess.CalledProcessError as exc:
        raise BootstrapError(f"{label} failed with exit code {exc.returncode}") from exc


def _json_command(command: list[str], *, label: str) -> object:
    completed = _run(command, label=label, capture=True)
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise BootstrapError(f"{label} returned invalid JSON") from exc


def _gh_api(path: str, *, label: str) -> object:
    return _json_command(["gh", "api", path], label=label)


def _az_token(resource: str) -> str:
    completed = _run(
        [
            "az",
            "account",
            "get-access-token",
            "--resource",
            resource,
            "--query",
            "accessToken",
            "-o",
            "tsv",
        ],
        label=f"Azure CLI token for {urlparse(resource).netloc or resource}",
        capture=True,
    )
    token = completed.stdout.strip()
    if not token or "\n" in token or "\r" in token:
        raise BootstrapError("Azure CLI returned an empty or malformed access token")
    return token


def _git(*args: str) -> str:
    completed = _run(["git", *args], label="git", capture=True)
    return completed.stdout.strip()


def _require_exact_customer_main() -> str:
    if _git("status", "--porcelain", "--untracked-files=all"):
        raise BootstrapError("Customer source must be clean before certification bootstrap")
    branch = _git("branch", "--show-current")
    if branch != "main":
        raise BootstrapError("certification bootstrap must run from the Customer main branch")
    sha = _git("rev-parse", "HEAD")
    remote = _gh_api(f"repos/{CUSTOMER_REPOSITORY}/branches/main", label="Customer main lookup")
    if not isinstance(remote, dict) or not isinstance(remote.get("commit"), dict):
        raise BootstrapError("Customer main lookup returned an unsupported response")
    remote_sha = remote["commit"].get("sha")
    if remote_sha != sha:
        raise BootstrapError(
            "local Customer HEAD is not the current GitHub main SHA; pull main before bootstrap"
        )
    return sha


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_framework_pin() -> dict[str, object]:
    value = json.loads(FRAMEWORK_PIN.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise BootstrapError("framework-executable.json has unsupported schema_version")
    required = {
        "framework_repository",
        "framework_version",
        "candidate_git_sha",
        "main_ci_run_id",
        "required_main_ci_jobs",
        "artifact_id",
        "artifact_name",
        "wheel_filename",
        "wheel_sha256",
    }
    missing = sorted(required - set(value))
    if missing:
        raise BootstrapError("framework-executable.json is incomplete: " + ", ".join(missing))
    return value


def _verify_and_download_framework(pin: dict[str, object], output: Path) -> dict[str, object]:
    repository = str(pin["framework_repository"])
    run_id = int(pin["main_ci_run_id"])
    candidate_sha = str(pin["candidate_git_sha"])
    run = _gh_api(f"repos/{repository}/actions/runs/{run_id}", label="Framework main CI lookup")
    if not isinstance(run, dict):
        raise BootstrapError("Framework main CI lookup returned an unsupported response")
    if (
        run.get("head_sha") != candidate_sha
        or run.get("head_branch") != "main"
        or run.get("event") != "push"
        or run.get("conclusion") != "success"
    ):
        raise BootstrapError("Framework executable pin is not backed by the expected successful main CI run")

    jobs = _gh_api(
        f"repos/{repository}/actions/runs/{run_id}/jobs?per_page=100",
        label="Framework main CI jobs lookup",
    )
    if not isinstance(jobs, dict) or not isinstance(jobs.get("jobs"), list):
        raise BootstrapError("Framework main CI jobs lookup returned an unsupported response")
    observed = {
        str(item.get("name")): item.get("conclusion")
        for item in jobs["jobs"]
        if isinstance(item, dict)
    }
    for required in pin["required_main_ci_jobs"]:  # type: ignore[index]
        if observed.get(str(required)) != "success":
            raise BootstrapError(f"required Framework main CI job is not successful: {required}")

    artifact_id = int(pin["artifact_id"])
    artifact = _gh_api(
        f"repos/{repository}/actions/artifacts/{artifact_id}",
        label="Framework artifact metadata lookup",
    )
    if not isinstance(artifact, dict):
        raise BootstrapError("Framework artifact metadata lookup returned an unsupported response")
    if artifact.get("name") != pin["artifact_name"] or artifact.get("expired") is True:
        raise BootstrapError("Framework artifact name/retention no longer matches the executable pin")
    workflow_run = artifact.get("workflow_run")
    if isinstance(workflow_run, dict) and int(workflow_run.get("id", -1)) != run_id:
        raise BootstrapError("Framework artifact belongs to a different workflow run")
    expected_zip_digest = pin.get("artifact_zip_digest")
    observed_zip_digest = artifact.get("digest")
    if expected_zip_digest and observed_zip_digest and observed_zip_digest != expected_zip_digest:
        raise BootstrapError("Framework artifact ZIP digest does not match the executable pin")

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    _run(
        [
            "gh",
            "run",
            "download",
            str(run_id),
            "--repo",
            repository,
            "--name",
            str(pin["artifact_name"]),
            "--dir",
            str(output),
        ],
        label="Framework artifact download",
    )

    candidate_path = output / "CANDIDATE.json"
    sums_path = output / "SHA256SUMS"
    wheel_path = output / str(pin["wheel_filename"])
    for path in (candidate_path, sums_path, wheel_path):
        if not path.is_file():
            raise BootstrapError(f"Framework artifact is missing required file: {path.name}")
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    if not isinstance(candidate, dict):
        raise BootstrapError("Framework CANDIDATE.json must be an object")
    expected_candidate = {
        "candidate_git_sha": candidate_sha,
        "workflow_run_id": run_id,
        "framework_version": str(pin["framework_version"]),
        "wheel_filename": str(pin["wheel_filename"]),
        "wheel_sha256": str(pin["wheel_sha256"]),
    }
    for key, expected in expected_candidate.items():
        if candidate.get(key) != expected:
            raise BootstrapError(f"Framework CANDIDATE.json mismatch for {key}")
    if _sha256(wheel_path) != pin["wheel_sha256"]:
        raise BootstrapError("Framework wheel bytes do not match pinned SHA256")
    sums = sums_path.read_text(encoding="utf-8")
    if str(pin["wheel_sha256"]) not in sums or str(pin["wheel_filename"]) not in sums:
        raise BootstrapError("Framework SHA256SUMS does not bind the pinned wheel")
    shutil.copy2(FRAMEWORK_PIN, output / FRAMEWORK_PIN.name)
    return {
        "candidate_git_sha": candidate_sha,
        "framework_version": pin["framework_version"],
        "main_ci_run_id": run_id,
        "artifact_id": artifact_id,
        "artifact_name": pin["artifact_name"],
        "wheel_filename": pin["wheel_filename"],
        "wheel_sha256": pin["wheel_sha256"],
        "artifact_zip_digest": observed_zip_digest or expected_zip_digest,
        "wheel_path": str(wheel_path),
    }


def _venv_python(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _prepare_certification_venv(build_root: Path, framework_wheel: Path) -> tuple[Path, Path]:
    venv = build_root / ".venv"
    _run([sys.executable, "-m", "venv", str(venv)], label="create certification venv")
    python = _venv_python(venv)
    _run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "build",
            "pyodbc",
            str(framework_wheel),
        ],
        label="install exact Framework bootstrap runtime",
    )
    extension_dist = build_root / "extension-dist"
    extension_dist.mkdir(parents=True, exist_ok=True)
    _run(
        [
            str(python),
            "-m",
            "build",
            "--wheel",
            str(CERT_ROOT / "extensions"),
            "--outdir",
            str(extension_dist),
        ],
        label="build Customer certification extension",
    )
    wheels = sorted(extension_dist.glob("*.whl"))
    if len(wheels) != 1:
        raise BootstrapError("Customer certification extension build must produce exactly one wheel")
    return python, wheels[0]
