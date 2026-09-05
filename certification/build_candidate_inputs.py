"""Build a credential-free exact customer certification input artifact.

This script runs only after an exact 0.4 framework candidate wheel has been verified and
installed. It binds customer/domain release identity, the framework wheel identity,
physical non-secret item IDs, source-controlled recipes and the exact extension wheel.
It never executes Fabric and never creates readiness PASS evidence.

Physical item identities may be supplied explicitly for backwards compatibility or via
a verified ``fabric-bindings.json`` produced by ``resolve_fabric_bindings.py``. The
verified file is preferred for real environments because it avoids hand-copying UUIDs
and preserves the exact read-only Fabric API verification provenance.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from importlib.metadata import version as installed_version
import json
from pathlib import Path
import re
import shutil
from typing import Mapping
from uuid import UUID

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

from review_binding import load_control_plane_review_binding


_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_SHA64 = re.compile(r"^[0-9a-f]{64}$")
_DOMAIN = "customer-certification"
_EXTENSION_WHEEL = "fabric_customer_certification_extensions-0.4.0.dev0-py3-none-any.whl"


@dataclass(frozen=True)
class _PhysicalBindings:
    workspace_id: str
    item_read_id: str
    pipeline_item_id: str
    copy_job_id: str
    spark_job_id: str
    source: str
    source_sha256: str | None = None


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
    parser.add_argument(
        "--fabric-bindings",
        type=Path,
        help="Verified fabric-bindings.json from resolve_fabric_bindings.py. Preferred for real Fabric.",
    )
    parser.add_argument("--workspace-id")
    parser.add_argument("--item-read-id")
    parser.add_argument("--pipeline-item-id")
    parser.add_argument("--copy-job-id")
    parser.add_argument("--spark-job-id")
    parser.add_argument(
        "--control-plane-profile",
        choices=("fabric_sql_database_v1", "azure_sql_database_v1"),
        required=True,
    )
    return parser


def _uuid(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a UUID")
    try:
        return str(UUID(value))
    except ValueError as exc:
        raise ValueError(f"{label} must be a UUID") from exc


def _mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def _verified_binding_item(
    root: Mapping[str, object],
    key: str,
    *,
    expected_type: str | None,
) -> str:
    item = _mapping(root.get(key), f"fabric bindings {key}")
    if expected_type is not None and item.get("type") != expected_type:
        raise ValueError(
            f"fabric bindings {key} type mismatch: expected={expected_type!r} observed={item.get('type')!r}"
        )
    if expected_type is None:
        observed_type = item.get("type")
        if not isinstance(observed_type, str) or not observed_type:
            raise ValueError("fabric bindings item_read must retain the exact Fabric item type")
    display_name = item.get("display_name")
    if not isinstance(display_name, str) or not display_name:
        raise ValueError(f"fabric bindings {key} must retain the exact display name")
    return _uuid(item.get("id"), f"fabric bindings {key} id")


def _require_optional_match(explicit: str | None, resolved: str, label: str) -> None:
    if explicit is None:
        return
    if _uuid(explicit, label) != resolved:
        raise ValueError(f"explicit {label} conflicts with verified fabric-bindings.json")


def _load_verified_fabric_bindings(
    path: Path,
    *,
    environment: str,
    explicit_workspace_id: str | None,
    explicit_item_read_id: str | None,
    explicit_pipeline_item_id: str | None,
    explicit_copy_job_id: str | None,
    explicit_spark_job_id: str | None,
) -> _PhysicalBindings:
    if not path.is_file():
        raise ValueError(f"fabric bindings file does not exist: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("fabric bindings file is not valid JSON") from exc
    root = _mapping(value, "fabric bindings")
    if root.get("schema_version") != 1:
        raise ValueError("unsupported fabric bindings schema_version")
    if root.get("verification_status") != "VERIFIED":
        raise ValueError("fabric bindings must have verification_status=VERIFIED")
    if root.get("environment") != environment:
        raise ValueError("fabric bindings environment does not match requested environment")
    if root.get("contains_secret_values") is not False:
        raise ValueError("fabric bindings must declare contains_secret_values=false")
    if root.get("certification_result") != "NOT_RUN":
        raise ValueError(
            "fabric bindings must remain a binding-only record with certification_result=NOT_RUN"
        )
    deployment_hash = root.get("deployment_result_sha256")
    if not isinstance(deployment_hash, str) or _SHA64.fullmatch(deployment_hash) is None:
        raise ValueError("fabric bindings deployment_result_sha256 must be lowercase SHA256")

    workspace_id = _uuid(root.get("workspace_id"), "fabric bindings workspace_id")
    item_read_id = _verified_binding_item(root, "item_read", expected_type=None)
    pipeline_item_id = _verified_binding_item(root, "pipeline", expected_type="DataPipeline")
    copy_job_id = _verified_binding_item(root, "copy_job", expected_type="CopyJob")
    spark_job_id = _verified_binding_item(
        root,
        "spark_job",
        expected_type="SparkJobDefinition",
    )
    # Notebook is not consumed by the IntegrationRunner, but requiring it here preserves
    # the deployment -> exact child Pipeline identity chain in the retained binding file.
    _verified_binding_item(root, "notebook", expected_type="Notebook")

    _require_optional_match(explicit_workspace_id, workspace_id, "workspace_id")
    _require_optional_match(explicit_item_read_id, item_read_id, "item_read_id")
    _require_optional_match(explicit_pipeline_item_id, pipeline_item_id, "pipeline_item_id")
    _require_optional_match(explicit_copy_job_id, copy_job_id, "copy_job_id")
    _require_optional_match(explicit_spark_job_id, spark_job_id, "spark_job_id")

    return _PhysicalBindings(
        workspace_id=workspace_id,
        item_read_id=item_read_id,
        pipeline_item_id=pipeline_item_id,
        copy_job_id=copy_job_id,
        spark_job_id=spark_job_id,
        source="verified_fabric_bindings",
        source_sha256=artifact_sha256(path),
    )


def _resolve_physical_bindings(args: argparse.Namespace) -> _PhysicalBindings:
    if args.fabric_bindings is not None:
        return _load_verified_fabric_bindings(
            args.fabric_bindings,
            environment=args.environment,
            explicit_workspace_id=args.workspace_id,
            explicit_item_read_id=args.item_read_id,
            explicit_pipeline_item_id=args.pipeline_item_id,
            explicit_copy_job_id=args.copy_job_id,
            explicit_spark_job_id=args.spark_job_id,
        )

    values = {
        "workspace_id": args.workspace_id,
        "item_read_id": args.item_read_id,
        "pipeline_item_id": args.pipeline_item_id,
        "copy_job_id": args.copy_job_id,
        "spark_job_id": args.spark_job_id,
    }
    missing = [name for name, value in values.items() if value is None]
    if missing:
        raise ValueError(
            "explicit physical bindings are incomplete; provide --fabric-bindings or all of: "
            "--workspace-id --item-read-id --pipeline-item-id --copy-job-id --spark-job-id; "
            f"missing={missing}"
        )
    return _PhysicalBindings(
        workspace_id=_uuid(args.workspace_id, "workspace_id"),
        item_read_id=_uuid(args.item_read_id, "item_read_id"),
        pipeline_item_id=_uuid(args.pipeline_item_id, "pipeline_item_id"),
        copy_job_id=_uuid(args.copy_job_id, "copy_job_id"),
        spark_job_id=_uuid(args.spark_job_id, "spark_job_id"),
        source="explicit_cli",
    )


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


def _validate_release_inputs(
    project_root: Path,
    manifest,
    extension_wheel: Path,
    *,
    environment: str,
    control_plane_profile: str,
) -> tuple[bool, list[str]]:
    dataset_ids = {item.dataset_id for item in load_dataset_configs(project_root / "config/datasets")}
    cert_root = project_root / "config" / "certification"

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
    review_binding = load_control_plane_review_binding(
        integration / "control-plane-external-evidence-review.json"
    )
    blockers: list[str] = []
    if not external.complete:
        blockers.append("control_plane_external_evidence_incomplete")
    elif not review_binding.matches(
        environment=environment,
        control_plane_profile=control_plane_profile,
    ):
        blockers.append("control_plane_external_evidence_not_review_bound")
    controller = fault_config.fault_payload.get("controller_url")
    if not isinstance(controller, str) or ".invalid" in controller:
        blockers.append("warehouse_real_fault_controller_not_configured")
    return not blockers, blockers


def main() -> int:
    args = _parser().parse_args()
    _require_identity(args)
    physical = _resolve_physical_bindings(args)
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
    live_ready, blockers = _validate_release_inputs(
        project_root,
        manifest,
        args.extension_wheel,
        environment=args.environment,
        control_plane_profile=args.control_plane_profile,
    )

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
                workspace_id=physical.workspace_id,
                item_id=physical.item_read_id,
            ),
            IntegrationCheckPhysicalBinding(
                check_id="fabric.pipeline",
                workspace_id=physical.workspace_id,
                item_id=physical.pipeline_item_id,
                dataset_id="cert.full_replace",
            ),
            IntegrationCheckPhysicalBinding(
                check_id="fabric.copy",
                workspace_id=physical.workspace_id,
                item_id=physical.copy_job_id,
            ),
            IntegrationCheckPhysicalBinding(
                check_id="fabric.spark",
                workspace_id=physical.workspace_id,
                item_id=physical.spark_job_id,
            ),
        ),
    )

    output = args.output.resolve()
    if output.exists():
        shutil.rmtree(output)
    (output / "dist").mkdir(parents=True)
    shutil.copytree(project_root, output / "project")
    shutil.copy2(args.extension_wheel, output / "dist" / args.extension_wheel.name)
    if args.fabric_bindings is not None:
        shutil.copy2(args.fabric_bindings, output / "fabric-bindings.json")
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
        "physical_binding_source": physical.source,
        "fabric_bindings_sha256": physical.source_sha256,
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
        f"physical_binding_source={physical.source} "
        f"live_prerequisites_configured={str(live_ready).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
