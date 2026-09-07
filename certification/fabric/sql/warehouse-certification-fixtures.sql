/*
  Dedicated DEV/UAT certification Warehouse fixtures only.

  DO NOT run this script against a shared or production Warehouse.  The tables are
  intentionally disposable and are mutated by the exact Customer certification bundle.
*/

IF OBJECT_ID('dbo.cert_pipeline_control', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.cert_pipeline_control (
        dataset_id VARCHAR(256) NOT NULL,
        failure_mode VARCHAR(128) NOT NULL
    );
END;

IF OBJECT_ID('dbo.cert_progress', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.cert_progress (
        dataset_id VARCHAR(256) NOT NULL,
        checkpoint VARCHAR(256) NOT NULL
    );
END;

IF OBJECT_ID('dbo.cert_full_source', 'U') IS NULL
    CREATE TABLE dbo.cert_full_source (id BIGINT NOT NULL, value VARCHAR(256) NULL);
IF OBJECT_ID('dbo.cert_full_target', 'U') IS NULL
    CREATE TABLE dbo.cert_full_target (id BIGINT NOT NULL, value VARCHAR(256) NULL);

IF OBJECT_ID('dbo.cert_scd1_source', 'U') IS NULL
    CREATE TABLE dbo.cert_scd1_source (
        id BIGINT NOT NULL,
        value VARCHAR(256) NULL,
        modified_at DATETIME2 NOT NULL
    );
IF OBJECT_ID('dbo.cert_scd1_target', 'U') IS NULL
    CREATE TABLE dbo.cert_scd1_target (id BIGINT NOT NULL, value VARCHAR(256) NULL);

IF OBJECT_ID('dbo.cert_scd2_source', 'U') IS NULL
    CREATE TABLE dbo.cert_scd2_source (
        id BIGINT NOT NULL,
        value VARCHAR(256) NULL,
        modified_at DATETIME2 NOT NULL
    );
IF OBJECT_ID('dbo.cert_scd2_current', 'U') IS NULL
    CREATE TABLE dbo.cert_scd2_current (id BIGINT NOT NULL, value VARCHAR(256) NULL);
IF OBJECT_ID('dbo.cert_scd2_history', 'U') IS NULL
    CREATE TABLE dbo.cert_scd2_history (
        id BIGINT NOT NULL,
        value VARCHAR(256) NULL,
        is_current BIT NOT NULL
    );

IF OBJECT_ID('dbo.cert_retry_source', 'U') IS NULL
    CREATE TABLE dbo.cert_retry_source (id BIGINT NOT NULL, value VARCHAR(256) NULL);
IF OBJECT_ID('dbo.cert_retry_target', 'U') IS NULL
    CREATE TABLE dbo.cert_retry_target (id BIGINT NOT NULL, value VARCHAR(256) NULL);

IF OBJECT_ID('dbo.cert_recon_source', 'U') IS NULL
    CREATE TABLE dbo.cert_recon_source (id BIGINT NOT NULL, value VARCHAR(256) NULL);
IF OBJECT_ID('dbo.cert_recon_target', 'U') IS NULL
    CREATE TABLE dbo.cert_recon_target (id BIGINT NOT NULL, value VARCHAR(256) NULL);

/* Integration Copy/Spark landing observers use these tables. */
IF OBJECT_ID('dbo.cert_copy_landing', 'U') IS NULL
    CREATE TABLE dbo.cert_copy_landing (id BIGINT NULL, value VARCHAR(256) NULL);
IF OBJECT_ID('dbo.cert_spark_landing', 'U') IS NULL
    CREATE TABLE dbo.cert_spark_landing (id BIGINT NULL, value VARCHAR(256) NULL);

/* Normal/ambiguous Warehouse certification target and markers remain dedicated. */
IF OBJECT_ID('dbo.cert_warehouse_target', 'U') IS NULL
    CREATE TABLE dbo.cert_warehouse_target (id BIGINT NULL, value VARCHAR(256) NULL);
IF OBJECT_ID('dbo.framework_operation_marker', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.framework_operation_marker (
        operation_key VARCHAR(128) NOT NULL,
        phase VARCHAR(64) NOT NULL,
        updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );
END;
