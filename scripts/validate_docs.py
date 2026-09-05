"""Dependency-free consistency checks for canonical Customer documentation.

The goal is not prose linting. This gate prevents version pins, framework-next SHA,
project commands, proof labels, enterprise topology, and known stale implementation
states from silently drifting across the files engineers use to bootstrap a new domain.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]

CANONICAL_DOCS = {
    "README": ROOT / "README.md",
    "BLUEPRINT": ROOT / "docs" / "PROJECT_BLUEPRINT.md",
    "STATUS": ROOT / "docs" / "CURRENT_STATUS.md",
    "RUNBOOK": ROOT / "docs" / "runbooks" / "BUILD_NEW_DOMAIN_PROJECT.md",
    "EXAMPLE": ROOT / "examples" / "enterprise_100_table" / "README.md",
}
TOPOLOGY_DOC = ROOT / "docs" / "runbooks" / "ENTERPRISE_ENVIRONMENT_TOPOLOGY.md"

FORBIDDEN_STALE_PHRASES = (
    "pending branch CI/merge",
    "CI/PR VALIDATION REQUIRED BEFORE MERGE",
    "intended CI gate for this change",
)


def _released_framework_version() -> str:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = pyproject["project"].get("dependencies", [])
    matches = [
        re.fullmatch(r"fabric-data-framework==([0-9]+\.[0-9]+\.[0-9]+)", item)
        for item in dependencies
    ]
    versions = [match.group(1) for match in matches if match is not None]
    if len(versions) != 1:
        raise ValueError(f"expected one exact framework dependency, found {dependencies!r}")
    return versions[0]


def _framework_next_sha() -> str:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    match = re.search(r"^\s*FRAMEWORK_NEXT_SHA:\s*([0-9a-f]{40})\s*$", workflow, re.MULTILINE)
    if match is None:
        raise ValueError("ci.yml must declare an exact 40-character FRAMEWORK_NEXT_SHA")
    return match.group(1)


def _require(text: str, needle: str, *, label: str) -> None:
    if needle not in text:
        raise ValueError(f"{label} is missing required documentation token {needle!r}")


def main() -> int:
    version = _released_framework_version()
    next_sha = _framework_next_sha()
    texts = {
        label: path.read_text(encoding="utf-8")
        for label, path in CANONICAL_DOCS.items()
    }
    topology = TOPOLOGY_DOC.read_text(encoding="utf-8")

    for label, text in texts.items():
        _require(text, version, label=label)
        _require(text, "100", label=label)
        for stale in FORBIDDEN_STALE_PHRASES:
            if stale in text:
                raise ValueError(f"{label} contains stale implementation state {stale!r}")

    for label in ("README", "BLUEPRINT", "STATUS", "RUNBOOK"):
        _require(texts[label], next_sha, label=label)

    for label in ("README", "BLUEPRINT", "STATUS", "RUNBOOK", "EXAMPLE"):
        _require(texts[label], "project-validate", label=label)

    for label in ("README", "BLUEPRINT", "RUNBOOK", "EXAMPLE"):
        _require(texts[label], "project-init", label=label)

    for label in ("README", "BLUEPRINT", "STATUS", "RUNBOOK", "EXAMPLE"):
        _require(texts[label], "Debezium", label=label)

    # Enterprise environment topology is a distinct operational contract. It is kept
    # outside the legacy five-document count so older checkpoint evidence remains
    # stable, but its required architecture tokens are still CI-enforced.
    for label, text in (
        ("README", texts["README"]),
        ("BLUEPRINT", texts["BLUEPRINT"]),
        ("TOPOLOGY", topology),
    ):
        _require(text, "fabric_sql_database_v1", label=label)
        _require(text, "DEV", label=label)
        _require(text, "UAT", label=label)
        _require(text, "PROD", label=label)
        _require(text, "Lakehouse", label=label)
        _require(text, "Warehouse", label=label)

    _require(topology, "Fabric SQL Database", label="TOPOLOGY")
    _require(topology, "Warehouse is optional", label="TOPOLOGY")
    _require(topology, "Why not Lakehouse control tables", label="TOPOLOGY")
    _require(topology, "Never promote DEV runtime rows", label="TOPOLOGY")

    if not (ROOT / "fabric-project.json").is_file():
        raise ValueError("fabric-project.json is required by the documented project contract")
    if not (ROOT / "config" / "capture" / "semantic-selections.json").is_file():
        raise ValueError(
            "config/capture/semantic-selections.json is required by the documented project contract"
        )

    print(
        "validated canonical docs "
        f"released_framework={version} framework_next_sha={next_sha} "
        f"documents={len(texts)} stale_phrases={len(FORBIDDEN_STALE_PHRASES)} "
        "enterprise_topology=validated"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, tomllib.TOMLDecodeError) as exc:
        print(f"documentation validation failed: {exc}", file=sys.stderr)
        raise SystemExit(2)
