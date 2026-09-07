-- Optional Fabric Warehouse source-system fixture. This is source truth only.
IF SCHEMA_ID('source_crm') IS NULL EXEC('CREATE SCHEMA source_crm');

IF OBJECT_ID('source_crm.customer', 'U') IS NULL
BEGIN
    CREATE TABLE source_crm.customer (
        customer_id varchar(20) NOT NULL,
        name varchar(200) NOT NULL,
        address varchar(200) NULL,
        segment varchar(50) NULL,
        email varchar(320) NULL,
        modified_at datetime2 NOT NULL,
        preferred_language varchar(20) NULL
    );
END;
