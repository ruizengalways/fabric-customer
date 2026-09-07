# Fabric Pipeline orchestration

Use a Fabric Data Factory Pipeline when you want the simulator to look like a production customer source feed. Create a Notebook activity that runs `fabric/notebooks/source_simulator.py`, then optionally use Copy Activity to copy the generated source files to a separate landing Lakehouse or to read from `source_crm.customer` in the source Warehouse.

The repo does not commit an unverified Pipeline JSON schema. Fabric item definitions change independently of this simulator; the exact manual setup is documented in `docs/fabric-setup-runbook.md`. The invariant is that Pipeline/Copy moves source data only and never invokes downstream framework APIs.
