"""Read-only semantic observer for representative live certification paths.

The observer consumes the same exact runner-declared ``WAREHOUSE_DATABASE_URL`` used
by the approved Warehouse/capture stages. It reads bounded certification fixture state
and returns semantic facts only; Framework code remains the sole PASS/FAIL evaluator.
"""

from __future__ import annotations

import os
from typing import Any

from sqlalchemy import create_engine

from fabric_data_framework.evidence.business_path_evidence import (
    BusinessPathObservationRequest,
    BusinessPathStateObservation,
)

from . import _one_current_per_key, _select_rows, _semantic_hash


def _warehouse_database_url() -> str:
    value = os.environ.get("WAREHOUSE_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("WAREHOUSE_DATABASE_URL is required for business-path observer")
    return value


def observe_business_path(
    request: BusinessPathObservationRequest,
) -> BusinessPathStateObservation:
    """Read actual target/progress/history rows and return semantic facts only."""

    target_spec = request.parameters.get("target")
    progress_spec = request.parameters.get("progress")
    history_spec = request.parameters.get("history")
    if not isinstance(target_spec, dict) or not isinstance(progress_spec, dict):
        raise ValueError("business path observer requires target and progress specs")

    engine = create_engine(_warehouse_database_url())
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
                if (
                    not isinstance(business_keys, list)
                    or not all(isinstance(column, str) for column in business_keys)
                    or not isinstance(current_flag, str)
                ):
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


__all__ = ["observe_business_path"]
