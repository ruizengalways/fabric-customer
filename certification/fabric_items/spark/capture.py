"""Framework-bounded Spark capture for the repository-owned certification item."""

import argparse
import base64
from datetime import datetime
import json

from pyspark.sql import functions as F


def _decode_payload(value: str) -> dict[str, object]:
    padding = "=" * (-len(value) % 4)
    raw = base64.urlsafe_b64decode((value + padding).encode("ascii"))
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("certification Spark payload must be an object")
    return payload


parser = argparse.ArgumentParser()
parser.add_argument("--payload-b64", required=True)
args = parser.parse_args()
payload = _decode_payload(args.payload_b64)

if payload.get("dataset_id") != "cert.spark":
    raise ValueError("Spark certification job only accepts dataset_id=cert.spark")
parameters = payload.get("parameters") or {}
if not isinstance(parameters, dict) or parameters.get("certification_mode") != "bounded":
    raise ValueError("Spark certification_mode must be bounded")

lower = payload.get("source_lower_bound")
upper = payload.get("source_upper_bound")
source = spark.table("dbo.cert_spark_source")
if lower is not None:
    source = source.where(F.col("modified_at") > F.to_timestamp(F.lit(str(lower))))
if upper is not None:
    source = source.where(F.col("modified_at") <= F.to_timestamp(F.lit(str(upper))))

source.write.mode("overwrite").saveAsTable("dbo.cert_spark_landing")
rows_written = source.count()
marker = spark.createDataFrame(
    [
        (
            str(payload["dataset_id"]),
            None if lower is None else str(lower),
            None if upper is None else str(upper),
            int(rows_written),
            datetime.utcnow(),
        )
    ],
    "dataset_id string, source_lower_bound string, source_upper_bound string, rows_written long, completed_at timestamp",
)
marker.write.mode("overwrite").saveAsTable("dbo.cert_spark_run_marker")
print(f"certification Spark capture wrote rows={rows_written}")
