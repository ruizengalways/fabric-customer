"""Build a credential-free exact customer certification input artifact.

This script runs only after an exact 0.4 framework candidate wheel has been verified and
installed. It binds customer/domain release identity, the framework wheel identity,
physical non-secret item IDs, source-controlled recipes and the exact extension wheel.
It never executes Fabric and never creates readiness PASS evidence.
"""

from __future__ import annotations

import argparse
from importlib.metadata import version as installed_version
import json
from pathlib import Path
import re
import shutil

from fabric_data_framework.contracts.environment import EnvironmentName
from fabric_data_framework.control_plane.certification import ControlPlaneExternalEvidence
from fabric_data_framework.deployment.delivery import (
    artifact_sha256,
    build_release_manifest,
    load_dataset_configs,
    write_json_model,
)
from fabric_data_framework.evidence.approved_capture_runner import load_approved_capture_run_config
from fabric_data_framework.evidence.approved_warehouse_fault_runner import (
    load_approved_warehouse_fault_drill_config,
)
from fabric_data_framework.evidence.approved_warehouse_runner import (
    load_approved_warehouse_run_config,
)
from fabric_data_framework.evidence.business_path_driver import (
    load_approved_business_path_driver_config,
)
from fabric_data_framework.evidence.business_path_evidence import (
    load_approved_business_path_scenario,
)
from fabric_data_framework.evidence.business_path_plan import (
    load_approved_business_path_certification_plan,
    resolve_business_path_plan_file,
)
from fabric_data_framework.evidence.integration_runner import (
    ApprovedIntegrationRunnerConfig,
    IntegrationCheckPhysicalBinding,
)


_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_SHA64 = re.compile(r"^[0-9a-f]{64}$")
_DOMAIN = "customer-certification"
_EXTENSION_WHEEL = "fabric_customer_certification_extensions-0.4.0.dev0-py3-none-any.whl"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("certification/project"))
    parser.add_argument("--extension-wheel", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--customer-git-sha", required=True)
    parser.add_argument("--candidate-git-sha", required=True)
    parser.add_argument("--candidate-wheel-sha256", required=True)
    parser.add_argument("--framework-version", required=True)
    parser.add_argument("--environment", choices=("DEV", "UAT", "PROD"), required=True)
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--item-read-id", required=True)
    parser.add_argument("--pipeline-item-id", required=True)
    parser.add_argument("--copy-job-id", required=True)
    parser.add_argument("--spark-job-id", required=True)
    parser.add_argument(
        "--control-plane-profile",
        choices=("fabric_sql_database_v1", "azure_sql_database_v1"),
        required=True,
    )
    return parser


def _require_identity(args: argparse.Namespace) -> None:
    for label in ("customer_git_sha", "candidate_git_sha"):
        if _SHA40.fullmatch(getattr(args, label)) is None:
            raise ValueError(f"{label} must be a 40-character lowercase git SHA")
    if _SHA64.fullmatch(args.candidate_wheel_sha256) is None:
        raise ValueError("candidate_wheel_sha256 must be lowercase SHA256")
    observed = installed_version("fabric-data-framework")
    if observed != args.framework_version:
        raise ValueError(
            f"installed framework version {observed!r} != requested {args.framework_version!r}"
        )
    if args.extension_wheel.name != _EXTENSION_WHEEL:
        raise ValueError(
            f"certification extension wheel must be {_EXTENSION_WHEEL!r}; "
            f"observed={args.extension_wheel.name!r}"
        )


def _artifact_inputs(project_root: Path, extension_wheel: Path) -> dict[str, Path]:
    cert_root = project_root / "config" / "certification"
    files = sorted(path for path in cert_root.rglob("*") if path.is_file())
    if not files:
        raise ValueError("certification project contains no certification artifacts")
    result: dict[str, Path] = {}
    for path in files:
        name = path.name
        if name in result:
            raise ValueError(f"duplicate certification artifact basename: {name}")
        result[name] = path
    if extension_wheel.name in result:
        raise ValueError("extension wheel name collides with source-controlled artifact")
    result[extension_wheel.name] = extension_wheel
    return result


def _validate_release_inputs(project_root: Path, manifest, extension_wheel: Path) -> tuple[bool, list[str]]:
    dataset_ids = {item.dataset_id for item in load_dataset_configs(project_root / "config/datasets")}
    cert_root = project_root / "config/certification"

    plan_path = cert_root / "business-path-plan.json"
    plan = load_approved_business_path_certification_plan(plan_path, release_manifest=manifest)
    if len(plan.entries) != 5:
        raise ValueError("certification plan must contain exactly five business-path gates")
    for entry in plan.entries:
        scenario_path = resolve_business_path_plan_file(project_root, entry.scenario_path)
        driver_path = resolve_business_path_plan_file(project_root, entry.driver_config_path)
        scenario = load_approved_business_path_scenario(scenario_path, release_manifest=manifest)
        if scenario.dataset_id not in dataset_ids:
            raise ValueError(f"business-path dataset absent from exact bundle: {scenario.dataset_id}")
        load_approved_business_path_driver_config(
            driver_path,
            release_manifest=manifest,
            expected_scenario_hash=scenario.scenario_hash,
        )

    integration = cert_root / "integration"
    copy_config = load_approved_capture_run_config(integration / "copy-run.json")
    spark_config = load_approved_capture_run_config(integration / "spark-run.json")
    warehouse_config = load_approved_warehouse_run_config(integration / "warehouse-run.json")
    fault_config = load_approved_warehouse_fault_drill_config(
        integration / "warehouse-fault-run.json"
    )
    if copy_config.check_id != "fabric.copy" or spark_config.check_id != "fabric.spark":
        raise ValueError("capture certification recipes own the wrong check IDs")
    if warehouse_config.check_id != "warehouse.commit":
        raise ValueError("Warehouse certification recipe owns the wrong check ID")
    if fault_config.check_id != "warehouse.ambiguous_commit":
        raise ValueError("Warehouse fault recipe owns the wrong check ID")
    for selected in (
        copy_config.dataset_id,
        spark_config.dataset_id,
        warehouse_config.dataset_id,
        fault_config.dataset_id,
    ):
        if selected not in dataset_ids:
            raise ValueError(f"integration recipe dataset absent from exact bundle: {selected}")
    for artifact_name in (
        copy_config.extension_artifact_name,
        spark_config.extension_artifact_name,
        warehouse_config.extension_artifact_name,
        fault_config.mutation_extension_artifact_name,
        fault_config.fault_injector_artifact_name,
    ):
        if artifact_name != extension_wheel.name:
            raise ValueError("certification recipe extension wheel identity mismatch")
        if artifact_name not in manifest.artifact_sha256:
            raise ValueError("certification extension wheel is absent from release manifest")

    external = ControlPlaneExternalEvidence.from_json_file(
        integration / "control-plane-external-evidence.json"
    )
    blockers: list[str] = []
    if not external.complete:
        blockers.append("control_plane_external_evidence_incomplete")
    controller = fault_config.fault_payload.get("controller_url")
    if not isinstance(controller, str) or ".invalid" in controller:
        blockers.append("warehouse_real_fault_controller_not_configured")
    return not blockers, blockers


def main() -> int:
    args = _parser().parse_args()
    _require_identity(args)
    project_root = args.project_root.resolve()
    if not project_root.is_dir():
        raise ValueError(f"project root does not exist: {project_root}")
    if not args.extension_wheel.is_file():
        raise ValueError(f"extension wheel does not exist: {args.extension_wheel}")

    configs = load_dataset_configs(project_root / "config/datasets")
    artifacts = _artifact_inputs(project_root, args.extension_wheel)
    manifest = build_release_manifest(
        domain=_DOMAIN,
        domain_release_version="0.4.0-certification",
        domain_git_sha=args.customer_git_sha,
        framework_version=args.framework_version,
        configs=configs,
        config_schema_version=max(item.config_schema_version for item in configs),
        fabric_item_manifest_version="certification-v1",
        build_id=f"candidate:{args.candidate_git_sha}:customer:{args.customer_git_sha}",
        artifacts=artifacts,
    )
    live_ready, blockers = _validate_release_inputs(project_root, manifest, args.extension_wheel)

    runner = ApprovedIntegrationRunnerConfig(
        environment=EnvironmentName(args.environment),
        domain=_DOMAIN,
        framework_version=args.framework_version,
        release_hash=manifest.bundle.release_hash,
        framework_artifact_sha256=args.candidate_wheel_sha256,
        fabric_access_token_env_var="FABRIC_ACCESS_TOKEN",
        control_plane_database_url_env_var="CONTROL_PLANE_DATABASE_URL",
        warehouse_database_url_env_var="WAREHOUSE_DATABASE_URL",
        warehouse_admin_database_url_env_var="WAREHOUSE_ADMIN_DATABASE_URL",
        control_plane_profile=args.control_plane_profile,
        bindings=(
            IntegrationCheckPhysicalBinding(
                check_id="fabric.item.read",
                workspace_id=args.workspace_id,
                item_id=args.item_read_id,
            ),
            IntegrationCheckPhysicalBinding(
                check_id="fabric.pipeline",
                workspace_id=args.workspace_id,
                item_id=args.pipeline_item_id,
                dataset_id="cert.full_replace",
            ),
            IntegrationCheckPhysicalBinding(
                check_id="fabric.copy",
                workspace_id=args.workspace_id,
                item_id=args.copy_job_id,
            ),
            IntegrationCheckPhysicalBinding(
                check_id="fabric.spark",
                workspace_id=args.workspace_id,
                item_id=args.spark_job_id,
            ),
        ),
    )

    output = args.output.resolve()
    if output.exists():
        shutil.rmtree(output)
    (output / "dist").mkdir(parents=True)
    shutil.copytree(project_root, output / "project")
    shutil.copy2(args.extension_wheel, output / "dist" / args.extension_wheel.name)
    write_json_model(manifest, output / "release-manifest.json")
    write_json_model(runner, output / "runner-config.json")
    input_manifest = {
        "input_schema_version": 1,
        "candidate_git_sha": args.candidate_git_sha,
        "candidate_wheel_sha256": args.candidate_wheel_sha256,
        "customer_git_sha": args.customer_git_sha,
        "framework_version": args.framework_version,
        "domain": manifest.domain,
        "domain_release_hash": manifest.bundle.release_hash,
        "config_bundle_hash": manifest.bundle.config_bundle_hash,
        "extension_wheel_filename": args.extension_wheel.name,
        "extension_wheel_sha256": artifact_sha256(args.extension_wheel),
        "live_prerequisites_configured": live_ready,
        "live_prerequisite_blockers": blockers,
    }
    (output / "INPUTS.json").write_text(
        json.dumps(input_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "built exact customer certification inputs "
        f"datasets={len(configs)} domain_release_hash={manifest.bundle.release_hash} "
        f"live_prerequisites_configured={str(live_ready).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
