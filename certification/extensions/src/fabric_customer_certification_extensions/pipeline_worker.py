"""Customer-owned physical executor for the reusable certification Fabric Pipeline.

The Framework owns remote correlation, exact config/plan validation and durable
DatasetRunAudit persistence.  This module owns only bounded mutations against the
explicitly provisioned certification Warehouse fixture tables.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection

from fabric_data_framework.apply.scd1 import SCD1ApplyPolicy, apply_scd1
from fabric_data_framework.apply.scd2 import (
    IS_CURRENT,
    RECORD_HASH,
    SOURCE_DATASET_RUN_ID,
    VALID_FROM,
    VALID_TO,
    apply_scd2,
)
from fabric_data_framework.apply.replace import ReplaceGuardPolicy, plan_replace
from fabric_data_framework.capture.full import FullSnapshotEvidence, capture_full_snapshot
from fabric_data_framework.contracts.audit import MutationCounts, RowAccounting
from fabric_data_framework.data_plane.staging import stage_rows
from fabric_data_framework.execution.pipeline_child import (
    FabricPipelineChildRequest,
    FabricPipelineChildResult,
)
from fabric_data_framework.metadata.config import DatasetConfig, DatasetStatus
from fabric_data_framework.quality.full_refresh import reconcile_full_replace


_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,127}$")
_QUALIFIED = re.compile(
    r"^(?P<schema>[A-Za-z_][A-Za-z0-9_]{0,127})\."
    r"(?P<table>[A-Za-z_][A-Za-z0-9_]{0,127})$"
)
_CONFIG_ENV = "CERTIFICATION_PIPELINE_WORKER_CONFIG_PATH"
_DEFAULT_CONFIG = (
    "/lakehouse/default/Files/framework_cert/customer-inputs/project/config/"
    "certification/pipeline-worker.json"
)


def _quote_identifier(value: str) -> str:
    if _IDENTIFIER.fullmatch(value) is None:
        raise ValueError(f"unsafe certification SQL identifier: {value!r}")
    return f"[{value}]"


def _quote_table(value: str) -> str:
    match = _QUALIFIED.fullmatch(value)
    if match is None:
        raise ValueError("certification table must use exact schema.table syntax")
    return (
        f"{_quote_identifier(match.group('schema'))}."
        f"{_quote_identifier(match.group('table'))}"
    )


def _load_worker_config() -> dict[str, Any]:
    path = Path(os.environ.get(_CONFIG_ENV, _DEFAULT_CONFIG))
    if not path.is_file():
        raise RuntimeError(f"certification Pipeline worker config is absent: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise RuntimeError("certification Pipeline worker config schema_version must be 1")
    datasets = value.get("datasets")
    if not isinstance(datasets, dict) or not datasets:
        raise RuntimeError("certification Pipeline worker config requires datasets")
    return value


def _database_url(worker_config: Mapping[str, Any]) -> str:
    env_var = worker_config.get("warehouse_database_url_env_var")
    if not isinstance(env_var, str) or not env_var:
        raise RuntimeError("Pipeline worker config requires warehouse_database_url_env_var")
    value = os.environ.get(env_var, "").strip()
    if not value:
        raise RuntimeError(f"required certification Warehouse runtime is missing: {env_var}")
    return value


def _select_all(connection: Connection, table_name: str) -> list[dict[str, Any]]:
    result = connection.execute(text(f"SELECT * FROM {_quote_table(table_name)}"))
    return [dict(row._mapping) for row in result]


def _replace_rows(
    connection: Connection,
    table_name: str,
    rows: list[Mapping[str, Any]],
) -> None:
    table = _quote_table(table_name)
    connection.execute(text(f"DELETE FROM {table}"))
    if not rows:
        return
    columns = tuple(rows[0].keys())
    if not columns or any(tuple(row.keys()) != columns for row in rows):
        raise ValueError("certification fixture rows require identical ordered columns")
    quoted = ", ".join(_quote_identifier(str(column)) for column in columns)
    params = ", ".join(f":p{index}" for index in range(len(columns)))
    statement = text(f"INSERT INTO {table} ({quoted}) VALUES ({params})")
    for row in rows:
        connection.execute(
            statement,
            {f"p{index}": row[column] for index, column in enumerate(columns)},
        )


def _failure_mode(
    connection: Connection,
    control_table: str,
    dataset_id: str,
) -> str | None:
    row = connection.execute(
        text(
            f"SELECT [failure_mode] FROM {_quote_table(control_table)} "
            "WHERE [dataset_id] = :dataset_id"
        ),
        {"dataset_id": dataset_id},
    ).first()
    return None if row is None else str(row[0])


def _progress_checkpoint(
    connection: Connection,
    progress_table: str,
    dataset_id: str,
) -> str | None:
    row = connection.execute(
        text(
            f"SELECT [checkpoint] FROM {_quote_table(progress_table)} "
            "WHERE [dataset_id] = :dataset_id"
        ),
        {"dataset_id": dataset_id},
    ).first()
    return None if row is None else str(row[0])


def _set_progress(
    connection: Connection,
    progress_table: str,
    dataset_id: str,
    checkpoint: str,
) -> None:
    table = _quote_table(progress_table)
    connection.execute(
        text(f"DELETE FROM {table} WHERE [dataset_id] = :dataset_id"),
        {"dataset_id": dataset_id},
    )
    connection.execute(
        text(
            f"INSERT INTO {table} ([dataset_id], [checkpoint]) "
            "VALUES (:dataset_id, :checkpoint)"
        ),
        {"dataset_id": dataset_id, "checkpoint": checkpoint},
    )


def _as_naive_utc(value: Any) -> datetime:
    if isinstance(value, datetime):
        observed = value
    elif isinstance(value, str):
        observed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        raise TypeError(f"expected datetime-compatible value, observed={type(value).__name__}")
    if observed.tzinfo is not None:
        observed = observed.astimezone(timezone.utc).replace(tzinfo=None)
    return observed


def _tracked_hash(row: Mapping[str, Any], tracked_columns: tuple[str, ...]) -> str:
    payload = {column: row.get(column) for column in tracked_columns}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


def _project_id_value(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [{"id": row["id"], "value": row["value"]} for row in rows]


def _validate_physical_binding(
    config: DatasetConfig,
    worker_dataset: Mapping[str, Any],
) -> None:
    source_table = worker_dataset.get("source_table")
    target_table = worker_dataset.get("target_table")
    if source_table != config.source.object:
        raise ValueError("Pipeline worker source table does not match exact DatasetConfig")
    if not isinstance(target_table, str) or target_table.split(".")[-1] != config.target.object:
        raise ValueError("Pipeline worker target table does not match exact DatasetConfig")


def _integration_smoke() -> FabricPipelineChildResult:
    # The integration Pipeline gate proves real provider invocation + exact durable
    # Framework correlation before business fixtures are intentionally armed.
    return FabricPipelineChildResult(
        status=DatasetStatus.SUCCEEDED,
        row_accounting=RowAccounting(rows_read=0, rows_accepted=0),
        mutations=MutationCounts(),
    )


def _full_replace(
    connection: Connection,
    *,
    request: FabricPipelineChildRequest,
    config: DatasetConfig,
    worker_dataset: Mapping[str, Any],
    progress_table: str,
    force_reconciliation_failure: bool,
) -> FabricPipelineChildResult:
    source_table = str(worker_dataset["source_table"])
    target_table = str(worker_dataset["target_table"])
    checkpoint = str(worker_dataset["success_checkpoint"])
    source = _project_id_value(_select_all(connection, source_table))
    current = _project_id_value(_select_all(connection, target_table))
    evidence = FullSnapshotEvidence(
        snapshot_id=checkpoint,
        complete=True,
        source_row_count=len(source),
        boundary_ref=f"certification:{request.dataset_id}:{checkpoint}",
    )
    capture = capture_full_snapshot(source, evidence=evidence)
    staged = stage_rows(capture.rows, dataset_run_id=request.framework_dataset_run_id)
    plan = plan_replace(
        current,
        staged,
        evidence=evidence,
        policy=ReplaceGuardPolicy(),
    )
    accounting = RowAccounting(rows_read=len(source), rows_accepted=len(source))
    reconciliation = reconcile_full_replace(
        dataset_run_id=request.framework_dataset_run_id,
        dataset_id=request.dataset_id,
        policy_name=config.reconciliation.policy_name,
        accounting=accounting,
        candidate_row_count=plan.candidate_count,
        evidence=evidence,
        force_fail=force_reconciliation_failure,
    )
    if reconciliation.blocks_state_advance and reconciliation.status.value != "PASS":
        return FabricPipelineChildResult(
            status=DatasetStatus.FAILED,
            row_accounting=accounting,
            error_code="RECONCILIATION_FAILED",
            error_message="required certification reconciliation gate failed",
            retryable=False,
        )
    _replace_rows(connection, target_table, list(plan.rows))
    _set_progress(connection, progress_table, request.dataset_id, checkpoint)
    return FabricPipelineChildResult(
        status=DatasetStatus.SUCCEEDED,
        row_accounting=accounting,
        mutations=plan.mutations,
    )


def _watermark_scd1(
    connection: Connection,
    *,
    request: FabricPipelineChildRequest,
    config: DatasetConfig,
    worker_dataset: Mapping[str, Any],
    progress_table: str,
) -> FabricPipelineChildResult:
    source_table = str(worker_dataset["source_table"])
    target_table = str(worker_dataset["target_table"])
    watermark_column = str(worker_dataset["watermark_column"])
    checkpoint = _progress_checkpoint(connection, progress_table, request.dataset_id)
    if checkpoint is None:
        raise RuntimeError("WATERMARK SCD1 certification requires baseline progress")
    before = _as_naive_utc(checkpoint)
    source_rows = _select_all(connection, source_table)
    delta = [row for row in source_rows if _as_naive_utc(row[watermark_column]) > before]
    incoming = _project_id_value(delta)
    current = _project_id_value(_select_all(connection, target_table))
    result = apply_scd1(
        current,
        incoming,
        merge_key=config.load.merge_key,
        policy=SCD1ApplyPolicy(allow_unordered_updates=True),
    )
    _replace_rows(connection, target_table, list(result.rows))
    if delta:
        _set_progress(
            connection,
            progress_table,
            request.dataset_id,
            str(worker_dataset["success_checkpoint"]),
        )
    accounting = RowAccounting(rows_read=len(delta), rows_accepted=len(delta))
    return FabricPipelineChildResult(
        status=DatasetStatus.SUCCEEDED,
        row_accounting=accounting,
        mutations=result.mutations,
    )


def _watermark_scd2(
    connection: Connection,
    *,
    request: FabricPipelineChildRequest,
    config: DatasetConfig,
    worker_dataset: Mapping[str, Any],
    progress_table: str,
) -> FabricPipelineChildResult:
    source_table = str(worker_dataset["source_table"])
    target_table = str(worker_dataset["target_table"])
    history_table = str(worker_dataset["history_table"])
    watermark_column = str(worker_dataset["watermark_column"])
    checkpoint = _progress_checkpoint(connection, progress_table, request.dataset_id)
    if checkpoint is None:
        raise RuntimeError("WATERMARK SCD2 certification requires baseline progress")
    before = _as_naive_utc(checkpoint)
    source_rows = _select_all(connection, source_table)
    delta = [row for row in source_rows if _as_naive_utc(row[watermark_column]) > before]
    incoming: list[dict[str, Any]] = []
    for raw in delta:
        row = {"id": raw["id"], "value": raw["value"], watermark_column: _as_naive_utc(raw[watermark_column])}
        incoming.append(row)

    physical_history = _select_all(connection, history_table)
    framework_history: list[dict[str, Any]] = []
    for raw in physical_history:
        base = {"id": raw["id"], "value": raw["value"]}
        framework_history.append(
            {
                **base,
                watermark_column: before,
                VALID_FROM: before,
                VALID_TO: None,
                IS_CURRENT: bool(raw["is_current"]),
                RECORD_HASH: _tracked_hash(base, config.load.tracked_columns),
                SOURCE_DATASET_RUN_ID: "certification-baseline",
            }
        )
    result = apply_scd2(
        framework_history,
        incoming,
        business_key=config.load.business_key,
        tracked_columns=config.load.tracked_columns,
        effective_time_column=watermark_column,
        dataset_run_id=request.framework_dataset_run_id,
    )
    projected_history = [
        {"id": row["id"], "value": row["value"], "is_current": bool(row[IS_CURRENT])}
        for row in result.rows
    ]
    projected_current = [
        {"id": row["id"], "value": row["value"]}
        for row in result.rows
        if row[IS_CURRENT] is True
    ]
    _replace_rows(connection, history_table, projected_history)
    _replace_rows(connection, target_table, projected_current)
    if delta:
        _set_progress(
            connection,
            progress_table,
            request.dataset_id,
            str(worker_dataset["success_checkpoint"]),
        )
    accounting = RowAccounting(rows_read=len(delta), rows_accepted=len(delta))
    return FabricPipelineChildResult(
        status=DatasetStatus.SUCCEEDED,
        row_accounting=accounting,
        mutations=result.mutations,
    )


def execute_certification_dataset(
    request: FabricPipelineChildRequest,
    config: DatasetConfig,
    _repository: object,
) -> FabricPipelineChildResult:
    """Execute one exact certification dataset against dedicated Warehouse fixtures.

    No matching control row means the caller is the earlier integration smoke gate.  In
    that mode the worker deliberately proves invocation/correlation without mutating
    business-path state.  Business-path drivers explicitly arm the dataset by writing
    one control row before calling this same reusable Pipeline.
    """

    worker_config = _load_worker_config()
    datasets = worker_config["datasets"]
    worker_dataset = datasets.get(request.dataset_id)
    if not isinstance(worker_dataset, dict):
        raise ValueError(f"unsupported certification Pipeline dataset: {request.dataset_id}")
    _validate_physical_binding(config, worker_dataset)
    control_table = worker_config.get("control_table")
    progress_table = worker_config.get("progress_table")
    if not isinstance(control_table, str) or not isinstance(progress_table, str):
        raise RuntimeError("Pipeline worker config requires control_table and progress_table")

    engine = create_engine(_database_url(worker_config))
    try:
        with engine.begin() as connection:
            mode = _failure_mode(connection, control_table, request.dataset_id)
            if mode is None:
                return _integration_smoke()
            if mode == "CERTIFICATION_RETRYABLE_FAILURE":
                return FabricPipelineChildResult(
                    status=DatasetStatus.FAILED,
                    row_accounting=RowAccounting(rows_read=0, rows_accepted=0),
                    error_code="CERTIFICATION_RETRYABLE_FAILURE",
                    error_message="bounded certification retryable failure requested",
                    retryable=True,
                )
            if mode not in {"SUCCESS", "RECONCILIATION_FAILED"}:
                raise RuntimeError(f"unsupported certification failure_mode: {mode}")

            strategy = worker_dataset.get("strategy")
            if strategy == "FULL_REPLACE":
                return _full_replace(
                    connection,
                    request=request,
                    config=config,
                    worker_dataset=worker_dataset,
                    progress_table=progress_table,
                    force_reconciliation_failure=(mode == "RECONCILIATION_FAILED"),
                )
            if mode != "SUCCESS":
                raise RuntimeError(
                    "RECONCILIATION_FAILED is supported only for FULL_REPLACE certification"
                )
            if strategy == "WATERMARK_SCD1":
                return _watermark_scd1(
                    connection,
                    request=request,
                    config=config,
                    worker_dataset=worker_dataset,
                    progress_table=progress_table,
                )
            if strategy == "WATERMARK_SCD2":
                return _watermark_scd2(
                    connection,
                    request=request,
                    config=config,
                    worker_dataset=worker_dataset,
                    progress_table=progress_table,
                )
            raise RuntimeError(f"unsupported certification Pipeline strategy: {strategy}")
    finally:
        engine.dispose()


__all__ = ["execute_certification_dataset"]
