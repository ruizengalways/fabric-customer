"""Translate Framework-bounded Spark capture inputs into Fabric ExecutionData."""

from __future__ import annotations

import base64
import json
from typing import Mapping

from fabric_data_framework.adapters.fabric.capture_transports import FabricSparkJobDefinitionBinding
from fabric_data_framework.adapters.fabric.contracts import FabricCaptureRequest


def spark_execution_data(
    request: FabricCaptureRequest,
    binding: FabricSparkJobDefinitionBinding,
) -> Mapping[str, object]:
    del binding  # the Spark item definition already owns the exact default Lakehouse
    payload = {
        "dataset_id": request.dataset_id,
        "source_lower_bound": request.source_lower_bound,
        "source_upper_bound": request.source_upper_bound,
        "parameters": dict(request.parameters),
    }
    encoded = base64.urlsafe_b64encode(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).decode("ascii")
    return {"commandLineArguments": f"--payload-b64 {encoded}"}


__all__ = ["spark_execution_data"]
