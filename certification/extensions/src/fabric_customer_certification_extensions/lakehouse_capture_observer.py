"""Post-run observer for repository-owned Copy/Spark landing tables in Lakehouse.

The observer reads real landing state from the active Fabric Spark session. For the
Framework-bounded Spark check it also reads a run marker written by the Spark job so
requested bounds are not merely echoed back from source-controlled configuration.
"""

from __future__ import annotations

from fabric_data_framework.adapters.fabric.capture_transports import FabricCaptureObservation
from fabric_data_framework.adapters.fabric.contracts import FabricCaptureRequest
from fabric_data_framework.adapters.fabric.rest import FabricJobInstance
from fabric_data_framework.metadata.config import ExecutionEngine


def _spark_session():
    try:
        from pyspark.sql import SparkSession
    except Exception as exc:  # pragma: no cover - Fabric runtime dependency
        raise RuntimeError("Lakehouse capture observation requires pyspark") from exc
    session = SparkSession.getActiveSession()
    if session is None:
        raise RuntimeError("Lakehouse capture observation requires an active SparkSession")
    return session


def observe_capture(
    request: FabricCaptureRequest,
    job: FabricJobInstance,
) -> FabricCaptureObservation:
    spark = _spark_session()
    landing = spark.table(request.landing_reference)
    count = int(landing.count())
    lower = request.source_lower_bound
    upper = request.source_upper_bound
    diagnostics: dict[str, object] = {
        "observation_kind": "lakehouse_table_count",
        "job_instance_id": str(job.job_instance_id),
    }

    if request.execution_engine is ExecutionEngine.SPARK:
        marker_rows = (
            spark.table("dbo.cert_spark_run_marker")
            .where("dataset_id = 'cert.spark'")
            .collect()
        )
        if len(marker_rows) != 1:
            raise RuntimeError(
                "Spark certification requires exactly one dbo.cert_spark_run_marker row"
            )
        marker = marker_rows[0].asDict(recursive=True)
        if int(marker["rows_written"]) != count:
            raise RuntimeError("Spark run marker row count does not match landing table")
        lower = marker.get("source_lower_bound")
        upper = marker.get("source_upper_bound")
        diagnostics["bounds_observation_kind"] = "spark_run_marker"

    return FabricCaptureObservation(
        rows_read=count,
        rows_written=count,
        landing_reference=request.landing_reference,
        source_reference=request.source_reference,
        source_lower_bound=lower,
        source_upper_bound=upper,
        schema_version="certification-lakehouse-v1",
        diagnostics=diagnostics,
    )


__all__ = ["observe_capture"]
