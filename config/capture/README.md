# Capture semantic selections

`semantic-selections.json` records the source/capture/Bronze/history truth claim for every source-controlled `DatasetConfig` in this domain.

The file is validated by the framework `project-validate` contract in the 0.4-next compatibility lane. Every dataset must have exactly one selection; unknown or missing dataset IDs fail closed.

These selections are semantic declarations, not credentials and not provider runtime evidence. A successful project validation does not prove that a Fabric workspace, source connection, Debezium topic, Pipeline, Spark job, Lakehouse or Warehouse has executed successfully.
