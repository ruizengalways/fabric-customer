"""Deterministic fixture preparation for representative certification paths.

The driver may reset bounded certification tables and a pipeline-control row. It never
observes provider success and never returns readiness PASS/FAIL.

Runtime SQL selection follows the exact Customer runner contract directly:
``WAREHOUSE_DATABASE_URL`` is supplied only at runtime by the Framework one-call
certification scope. No second JSON-wrapped secret channel is required.
"""

from __future__ import annotations

import os

from fabric_data_framework.evidence.business_path_driver import (
    BusinessPathDriverReceipt,
    BusinessPathDriverRequest,
)

from . import _replace_fixture_rows, _set_pipeline_control


def _warehouse_database_url() -> str:
    value = os.environ.get("WAREHOUSE_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("WAREHOUSE_DATABASE_URL is required for business-path driver")
    return value


def drive_business_path(request: BusinessPathDriverRequest) -> BusinessPathDriverReceipt:
    database_url = _warehouse_database_url()
    actions = request.parameters.get("actions")
    control_table = request.parameters.get("control_table")
    if not isinstance(actions, dict):
        raise ValueError("business path driver requires actions")
    action = actions.get(request.phase.value)
    if not isinstance(action, dict):
        raise ValueError(f"business path driver has no action for {request.phase.value}")

    replacements = action.get("replacements", [])
    if not isinstance(replacements, list):
        raise ValueError("business path replacements must be a list")
    for replacement in replacements:
        if not isinstance(replacement, dict):
            raise ValueError("business path replacement must be an object")
        table = replacement.get("table")
        rows = replacement.get("rows")
        if not isinstance(table, str) or not isinstance(rows, list):
            raise ValueError("business path replacement requires table and rows")
        if not all(isinstance(row, dict) for row in rows):
            raise ValueError("business path replacement rows must be JSON objects")
        _replace_fixture_rows(database_url, table_name=table, rows=rows)

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


__all__ = ["drive_business_path"]
