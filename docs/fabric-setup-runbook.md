# Fabric setup runbook

## 1. Build the simulator wheel

```bash
python -m pip install build
python -m build --wheel
```

Upload `dist/fabric_customer_reference-0.2.0-py3-none-any.whl` to a Fabric Environment and publish the Environment.

## 2. Lakehouse source feed

Create/choose a dedicated source Lakehouse, attach it to a Fabric Notebook, copy `fabric/notebooks/source_simulator.py` into the notebook and run with:

```python
DAY = 1
RESET = True
REPLAY_DAY = None
```

The default path is `/lakehouse/default/Files/fabric-customer`.

For Day 2, change `DAY = 2` and `RESET = True`. The materializer deterministically reconstructs Day 1 and Day 2, so reruns do not depend on hidden notebook state. Continue through Day 7 the same way.

## 3. Pipeline / Copy Activity

Create a Fabric Data Factory Pipeline with a Notebook activity for the source simulator. If the implementation under test expects a separate landing area, add Copy Activity from `Files/fabric-customer/source_systems/...` into that landing location. Keep the source simulator and implementation landing paths separate.

Pipeline/Copy must move source bytes only. It must not import a downstream framework or call framework metadata/runtime APIs.

## 4. Optional source Warehouse

Run `fabric/sql/source_warehouse_seed.sql` in a dedicated Fabric Warehouse. Populate it from generated current-state truth or use it as the source side of Copy Activity. The SQL file creates only source-system shape; it does not create framework control-plane tables.

## 5. Eventstream

For streaming experiments, publish records from the generated `source_systems/crm/cdc/day_XX/customer_events.jsonl` into the chosen Eventstream input. Preserve `event_id`, order and duplicates; otherwise the scenario no longer represents the canonical delivery.

## Validation

After each source day, inspect the matching `expected/*/day_XX` files. These are the source/business oracle. Fabric execution of a downstream framework is a separate concern.
