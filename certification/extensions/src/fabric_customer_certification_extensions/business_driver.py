"""Deterministic fixture preparation for representative certification paths.

The driver may reset bounded certification tables and a pipeline-control row. It never
observes provider success and never returns readiness PASS/FAIL.
"""

from __future__ import annotations

from typing import Any

from fabric_data_framework.evidence.business_path_driver import (
    BusinessPathDriverReceipt,
    BusinessPathDriverRequest,
)

from . import _database_url, _replace_fixture_rows, _runtime_json, _set_pipeline_control


def drive_business_path(request: BusinessPathDriverRequest) -> BusinessPathDriverReceipt:
    runtime = _runtime_json("BUSINESS_PATH_DRIVER_RUNTIME_JSON")
    database_url = _database_url(runtime)
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
