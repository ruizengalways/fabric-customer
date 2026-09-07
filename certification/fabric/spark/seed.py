"""Setup-only Spark job for certification Lakehouse source tables.

This job prepares deterministic source data. Its completion is never certification
PASS evidence.
"""

from datetime import datetime, timezone

from pyspark.sql import Row


spark.sql("CREATE SCHEMA IF NOT EXISTS dbo")

copy_rows = [
    Row(id=1, value="copy-a", modified_at=datetime(2026, 8, 29, 0, 0, tzinfo=timezone.utc)),
    Row(id=2, value="copy-b", modified_at=datetime(2026, 8, 30, 0, 0, tzinfo=timezone.utc)),
    Row(id=3, value="copy-c", modified_at=datetime(2026, 8, 31, 0, 0, tzinfo=timezone.utc)),
]
spark.createDataFrame(copy_rows).write.mode("overwrite").saveAsTable("dbo.cert_copy_source")

spark_rows = [
    Row(id=1, value="spark-a", modified_at=datetime(2026, 8, 29, 0, 0, tzinfo=timezone.utc)),
    Row(id=2, value="spark-b", modified_at=datetime(2026, 8, 30, 0, 0, tzinfo=timezone.utc)),
    Row(id=3, value="spark-c", modified_at=datetime(2026, 8, 31, 0, 0, tzinfo=timezone.utc)),
    Row(id=4, value="spark-future", modified_at=datetime(2026, 9, 1, 0, 0, tzinfo=timezone.utc)),
]
spark.createDataFrame(spark_rows).write.mode("overwrite").saveAsTable("dbo.cert_spark_source")

for table in ("dbo.cert_copy_landing", "dbo.cert_spark_landing", "dbo.cert_spark_run_marker"):
    spark.sql(f"DROP TABLE IF EXISTS {table}")

print("certification provider source seed completed; setup_only=true")
