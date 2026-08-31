"""Bounded customer-owned extensions for exact Fabric release certification.

These extensions deliberately do not decide release PASS. They either read actual
runtime/provider state, perform bounded certification-fixture mutations, or delegate a
real ambiguous-COMMIT fault to an external controller. Secret-bearing runtime values
are read from process environment only and are never returned in retained evidence.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from datetime import date, datetime
from decimal import Decimal
import hashlib
import json
import os
import re
from typing import Any
from urllib import request as urllib_request

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection

from fabric_data_framework.adapters.fabric.capture_transports import (
    FabricCaptureObservation,
    FabricSparkJobDefinitionBinding,
)
from fabric_data_framework.adapters.fabric.contracts import FabricCaptureRequest
from fabric_data_framework.adapters.fabric.rest import FabricJobInstance
from fabric_data_framework.evidence.business_path_driver import (
    BusinessPathDriverReceipt,
    BusinessPathDriverRequest,
)
from fabric_data_framework.evidence.business_path_evidence import (
    BusinessPathObservationRequest,
    BusinessPathStateObservation,
)
from fabric_data_framework.recovery.fabric_warehouse import FabricWarehouseMutationEvidence
from fabric_data_framework.recovery.target_probe import TargetCommitProbeEvidence
from fabric_data_framework.recovery.warehouse_fault_injection import (
    FabricWarehouseCommitFaultArmEvidence,
    FabricWarehouseCommitFaultInjector,
    FabricWarehouseCommitFaultRequest,
    FabricWarehouseCommitFaultVerification,
)
from fabric_data_framework.contracts.target_operation import TargetOperationIntent


_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,127}$")
_QUALIFIED = re.compile(
    r"^(?P<schema>[A-Za-z_][A-Za-z0-9_]{0,127})\."
    r"(?P<table>[A-Za-z_][A-Za-z0-9_]{0,127})$"
)


def _quote_identifier(value: str) -> str:
    if _IDENTIFIER.fullmatch(value) is None:
        raise ValueError(f"unsafe certification SQL identifier: {value!r}")
    return f"[{value}]"


def _quote_table(value: str) -> str:
    match = _QUALIFIED.fullmatch(value)
    if match is None:
        raise ValueError(
            "certification table must use exact schema.table identifier syntax"
        )
    return (
        f"{_quote_identifier(match.group('schema'))}."
        f"{_quote_identifier(match.group('table'))}"
    )


def _json_value(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, bytes):
        return value.hex()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _canonical_rows(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    normalized = [
        {str(key): _json_value(value) for key, value in sorted(row.items())}
        for row in rows
    ]
    return sorted(
        normalized,
        key=lambda item: json.dumps(
            item,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ),
    )


def _semantic_hash(rows: list[Mapping[str, Any]]) -> str:
    encoded = json.dumps(
        _canonical_rows(rows),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _runtime_json(env_var: str) -> dict[str, Any]:
    raw = os.environ.get(env_var, "").strip()
    if not raw:
        raise RuntimeError(f"required certification runtime environment is missing: {env_var}")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{env_var} must contain valid JSON") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{env_var} must contain a JSON object")
    return value


def _database_url(runtime: Mapping[str, Any]) -> str:
    value = runtime.get("database_url")
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("certification runtime JSON requires database_url")
    return value


def _select_all(database_url: str, table_name: str) -> list[dict[str, Any]]:
    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT * FROM {_quote_table(table_name)}"))
            return [dict(row._mapping) for row in result]
    finally:
        engine.dispose()


def observe_capture(
    request: FabricCaptureRequest,
    job: FabricJobInstance,
) -> FabricCaptureObservation:
    """Observe actual landing rows after a completed Fabric Copy/Spark job.

    The approved framework workflow already exposes ``WAREHOUSE_DATABASE_URL`` only as
    runtime secret material. This observer reads the configured landing table and uses
    the observed rows as the capture-count fact. It never trusts source-controlled
    expected row counts.
    """

    database_url = os.environ.get("WAREHOUSE_DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError("WAREHOUSE_DATABASE_URL is required for capture observation")
    rows = _select_all(database_url, request.landing_reference)
    count = len(rows)
    complete_snapshot = None
    if request.capture_strategy.value in {"FULL", "SNAPSHOT"}:
        complete_snapshot = True
    return FabricCaptureObservation(
        rows_read=count,
        rows_written=count,
        landing_reference=request.landing_reference,
        source_reference=request.source_reference,
        source_lower_bound=request.source_lower_bound,
        source_upper_bound=request.source_upper_bound,
        snapshot_id=request.snapshot_id,
        complete_snapshot=complete_snapshot,
        schema_version="certification-v1",
        diagnostics={
            "observation_kind": "warehouse_landing_query",
            "job_instance_id": str(job.job_instance_id),
        },
    )


def spark_execution_data(
    request: FabricCaptureRequest,
    binding: FabricSparkJobDefinitionBinding,
) -> Mapping[str, object]:
    """Pass the exact framework-frozen bounds into the Spark job invocation."""

    payload: dict[str, object] = {
        "dataset_id": request.dataset_id,
        "workspace_id": str(binding.workspace_id),
        "source_lower_bound": request.source_lower_bound,
        "source_upper_bound": request.source_upper_bound,
    }
    for key, value in request.parameters.items():
        if key in payload:
            raise ValueError(f"Spark execution parameter collides with reserved key: {key}")
        payload[key] = value
    return payload


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
    parameters = ", ".join(f":p{index}" for index in range(len(columns)))
    statement = text(f"INSERT INTO {table} ({quoted}) VALUES ({parameters})")
    for row in rows:
        connection.execute(
            statement,
            {f"p{index}": row[column] for index, column in enumerate(columns)},
        )


def warehouse_mutation(
    connection: Connection,
    intent: TargetOperationIntent,
    payload: Mapping[str, Any],
) -> FabricWarehouseMutationEvidence:
    """Replace rows only in the explicitly named certification target table.

    The supplied connection belongs to the framework transaction. This extension never
    commits, writes framework markers, mutates the control-plane journal, or decides
    whether the operation passed.
    """

    table_name = payload.get("table")
    rows = payload.get("rows")
    if not isinstance(table_name, str) or not isinstance(rows, list):
        raise ValueError("Warehouse certification mutation requires table and rows")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError("Warehouse certification mutation rows must be JSON objects")
    _replace_rows(connection, table_name, rows)
    return FabricWarehouseMutationEvidence(
        query_label=f"certification:{intent.dataset_id}",
        detail="bounded customer certification target mutation executed",
    )


class _ExternalFaultController(FabricWarehouseCommitFaultInjector):
    def __init__(self, *, controller_url: str, token_env_var: str | None) -> None:
        if not controller_url.startswith("https://") or ".invalid" in controller_url:
            raise RuntimeError(
                "real Warehouse fault controller requires a configured HTTPS endpoint"
            )
        self._base = controller_url.rstrip("/")
        self._token_env_var = token_env_var

    def _post(self, action: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self._token_env_var is not None:
            token = os.environ.get(self._token_env_var, "").strip()
            if not token:
                raise RuntimeError(
                    f"real Warehouse fault controller token is missing: {self._token_env_var}"
                )
            headers["Authorization"] = f"Bearer {token}"
        req = urllib_request.Request(
            f"{self._base}/{action}",
            data=body,
            headers=headers,
            method="POST",
        )
        with urllib_request.urlopen(req, timeout=30) as response:  # noqa: S310
            raw = response.read()
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise RuntimeError("Warehouse fault controller returned non-object JSON")
        return value

    @staticmethod
    def _request_payload(request: FabricWarehouseCommitFaultRequest) -> dict[str, Any]:
        return {
            "operation_key": request.operation_key,
            "dataset_id": request.dataset_id,
            "dataset_run_id": str(request.dataset_run_id),
            "attempt": request.attempt,
            "target_reference": request.target_reference,
            "phase": request.phase.value,
        }

    def arm(
        self,
        request: FabricWarehouseCommitFaultRequest,
    ) -> FabricWarehouseCommitFaultArmEvidence:
        value = self._post("arm", self._request_payload(request))
        return FabricWarehouseCommitFaultArmEvidence(
            armed=value.get("armed") is True,
            phase=request.phase,
            evidence_reference=value.get("evidence_reference"),
            provider_fault_id=value.get("provider_fault_id"),
            detail=value.get("detail"),
        )

    def disarm(self, request: FabricWarehouseCommitFaultRequest) -> None:
        value = self._post("disarm", self._request_payload(request))
        if value.get("disarmed") is not True:
            raise RuntimeError("Warehouse fault controller did not confirm disarm")

    def verify(
        self,
        request: FabricWarehouseCommitFaultRequest,
        *,
        observed_exception_type: str | None,
        probe_evidence: TargetCommitProbeEvidence,
    ) -> FabricWarehouseCommitFaultVerification:
        payload = self._request_payload(request)
        payload.update(
            {
                "observed_exception_type": observed_exception_type,
                "probe_resolution": probe_evidence.resolution.value,
            }
        )
        value = self._post("verify", payload)
        return FabricWarehouseCommitFaultVerification(
            triggered=value.get("triggered") is True,
            phase=request.phase,
            evidence_reference=value.get("evidence_reference"),
            provider_fault_id=value.get("provider_fault_id"),
            detail=value.get("detail"),
        )


def warehouse_fault_injector(
    _engine: object,
    _request: FabricWarehouseCommitFaultRequest,
    payload: Mapping[str, Any],
) -> FabricWarehouseCommitFaultInjector:
    """Build a fail-closed external real-fault controller.

    The customer must supply a real HTTPS controller endpoint. The repository ships an
    ``example.invalid`` placeholder, which deliberately prevents live certification
    until enterprise fault infrastructure is configured.
    """

    controller_url = payload.get("controller_url")
    token_env_var = payload.get("token_env_var")
    if not isinstance(controller_url, str):
        raise RuntimeError("Warehouse fault payload requires controller_url")
    if token_env_var is not None and not isinstance(token_env_var, str):
        raise RuntimeError("Warehouse fault token_env_var must be a string when supplied")
    return _ExternalFaultController(
        controller_url=controller_url,
        token_env_var=token_env_var,
    )


def _replace_fixture_rows(
    database_url: str,
    *,
    table_name: str,
    rows: list[Mapping[str, Any]],
) -> None:
    engine = create_engine(database_url)
    try:
        with engine.begin() as connection:
            _replace_rows(connection, table_name, rows)
    finally:
        engine.dispose()


def _set_pipeline_control(
    database_url: str,
    *,
    table_name: str,
    dataset_id: str,
    failure_mode: str,
) -> None:
    table = _quote_table(table_name)
    engine = create_engine(database_url)
    try:
        with engine.begin() as connection:
            connection.execute(
                text(f"DELETE FROM {table} WHERE [dataset_id] = :dataset_id"),
                {"dataset_id": dataset_id},
            )
            connection.execute(
                text(
                    f"INSERT INTO {table} ([dataset_id], [failure_mode]) "
                    "VALUES (:dataset_id, :failure_mode)"
                ),
                {"dataset_id": dataset_id, "failure_mode": failure_mode},
            )
    finally:
        engine.dispose()


def drive_business_path(request: BusinessPathDriverRequest) -> BusinessPathDriverReceipt:
    """Prepare source fixture/control rows without deciding PASS."""

    runtime = _runtime_json("BUSINESS_PATH_DRIVER_RUNTIME_JSON")
    database_url = _database_url(runtime)
    parameters = request.parameters
    source_table = parameters.get("source_table")
    control_table = parameters.get("control_table")
    actions = parameters.get("actions")
    if not isinstance(source_table, str) or not isinstance(actions, dict):
        raise ValueError("business path driver requires source_table and actions")
    action = actions.get(request.phase.value)
    if not isinstance(action, dict):
        raise ValueError(f"business path driver has no action for {request.phase.value}")
    rows = action.get("rows", [])
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError("business path driver action rows must be JSON objects")
    _replace_fixture_rows(database_url, table_name=source_table, rows=rows)

    failure_mode = action.get("failure_mode", "SUCCESS")
    if control_table is not None:
        if not isinstance(control_table, str) or not isinstance(failure_mode, str):
            raise ValueError("business path control table/failure mode are invalid")
        _set_pipeline_control(
            database_url,
            table_name=control_table,
            dataset_id=request.dataset_id,
            failure_mode=failure_mode,
        )

    return BusinessPathDriverReceipt(
        gate_id=request.gate_id,
        dataset_id=request.dataset_id,
        scenario_hash=request.scenario_hash,
        phase=request.phase,
        evidence_references=(
            f"certification-driver:{request.dataset_id}:{request.phase.value.lower()}",
        ),
    )


def _select_rows(
    connection: Connection,
    spec: Mapping[str, Any],
) -> list[dict[str, Any]]:
    table_name = spec.get("table")
    columns = spec.get("columns")
    where = spec.get("where", {})
    if not isinstance(table_name, str):
        raise ValueError("business path observation table must be a string")
    if not isinstance(columns, list) or not columns or not all(
        isinstance(column, str) for column in columns
    ):
        raise ValueError("business path observation columns must be a non-empty string list")
    if not isinstance(where, dict):
        raise ValueError("business path observation where must be an object")
    selected = ", ".join(_quote_identifier(column) for column in columns)
    statement = f"SELECT {selected} FROM {_quote_table(table_name)}"
    parameters: dict[str, Any] = {}
    if where:
        predicates: list[str] = []
        for index, (column, value) in enumerate(sorted(where.items())):
            name = f"w{index}"
            predicates.append(f"{_quote_identifier(str(column))} = :{name}")
            parameters[name] = value
        statement += " WHERE " + " AND ".join(predicates)
    result = connection.execute(text(statement), parameters)
    return [dict(row._mapping) for row in result]


def _one_current_per_key(
    rows: list[Mapping[str, Any]],
    *,
    business_keys: list[str],
    current_flag: str,
) -> bool:
    counts: defaultdict[tuple[Any, ...], int] = defaultdict(int)
    all_keys: set[tuple[Any, ...]] = set()
    for row in rows:
        key = tuple(row[column] for column in business_keys)
        all_keys.add(key)
        if bool(row[current_flag]):
            counts[key] += 1
    return bool(all_keys) and all(counts[key] == 1 for key in all_keys)


def observe_business_path(
    request: BusinessPathObservationRequest,
) -> BusinessPathStateObservation:
    """Read actual target/progress/history rows and return semantic facts only."""

    runtime = _runtime_json("BUSINESS_PATH_OBSERVER_RUNTIME_JSON")
    database_url = _database_url(runtime)
    target_spec = request.parameters.get("target")
    progress_spec = request.parameters.get("progress")
    history_spec = request.parameters.get("history")
    if not isinstance(target_spec, dict) or not isinstance(progress_spec, dict):
        raise ValueError("business path observer requires target and progress specs")

    engine = create_engine(database_url)
    try:
        with engine.connect() as connection:
            target_rows = _select_rows(connection, target_spec)
            progress_rows = _select_rows(connection, progress_spec)
            history_rows: list[dict[str, Any]] | None = None
            current_ok: bool | None = None
            if history_spec is not None:
                if not isinstance(history_spec, dict):
                    raise ValueError("business path history spec must be an object")
                history_rows = _select_rows(connection, history_spec)
                business_keys = history_spec.get("business_key_columns")
                current_flag = history_spec.get("current_flag_column")
                if not isinstance(business_keys, list) or not all(
                    isinstance(column, str) for column in business_keys
                ) or not isinstance(current_flag, str):
                    raise ValueError(
                        "business path history spec requires business_key_columns/current_flag_column"
                    )
                current_ok = _one_current_per_key(
                    history_rows,
                    business_keys=business_keys,
                    current_flag=current_flag,
                )
    finally:
        engine.dispose()

    references = [
        f"certification-observer:{request.dataset_id}:{request.phase.value.lower()}:target",
        f"certification-observer:{request.dataset_id}:{request.phase.value.lower()}:progress",
    ]
    if history_rows is not None:
        references.append(
            f"certification-observer:{request.dataset_id}:{request.phase.value.lower()}:history"
        )
    return BusinessPathStateObservation(
        dataset_id=request.dataset_id,
        phase=request.phase,
        target_semantic_sha256=_semantic_hash(target_rows),
        target_row_count=len(target_rows),
        progress_semantic_sha256=_semantic_hash(progress_rows),
        history_semantic_sha256=(
            _semantic_hash(history_rows) if history_rows is not None else None
        ),
        one_current_row_per_business_key=current_ok,
        evidence_references=tuple(references),
    )


def forbidden_noop_apply(*_args: Any, **_kwargs: Any) -> None:
    """Never execute during capture-only certification.

    The Spark DatasetConfig uses a CUSTOM apply engine solely to force a dedicated
    capture-only execution unit. If this callable is ever reached, certification is
    executing the wrong lifecycle stage and must fail closed.
    """

    raise RuntimeError("certification capture-only package must never execute apply")


__all__ = [
    "drive_business_path",
    "forbidden_noop_apply",
    "observe_business_path",
    "observe_capture",
    "spark_execution_data",
    "warehouse_fault_injector",
    "warehouse_mutation",
]
