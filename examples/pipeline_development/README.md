# Fabric Pipeline Development Examples

这部分是正常业务 Pipeline 的 reference implementation，不是 Framework certification fixture。

目标是让新项目可以直接看懂：一个 parent Fabric Pipeline 如何用一个 bounded ForEach / reusable child 执行很多 DatasetConfig，同时做到 table fault isolation、fail-at-end、DQ/quarantine 和可恢复运行。

## 0. 版本边界

Customer production dependency 仍然必须保持：

```text
fabric-data-framework==0.3.0
```

下面 `framework_0_4/` 的 execution-group policy 是 Framework 0.4 development contract 的**前向 reference**。在 immutable v0.4.0 发布并获准迁移之前：

- 不把这些文件移动到 production runtime config；
- 不修改 `pyproject.toml` production pin；
- 可以用于设计评审、项目模板、静态 CI contract 和下一版准备。

## 1. 一个 100-table domain 推荐怎么拆 parent Pipelines

不是一张表一个 Pipeline，也不是 100 张表全部塞进一个超大顺序 Pipeline。按运行语义和 SLA 分 execution group：

```text
health_full_refresh     50 FULL -> REPLACE
health_scd2             20 WATERMARK -> SCD2
health_scd1             20 WATERMARK -> SCD1
health_debezium         10 CDC -> UPSERT
```

每个 group 对应一个薄 parent Pipeline：

```text
select work for execution_group
-> bounded ForEach
-> reusable child / framework dataset execution
-> every dataset writes durable semantic outcome
-> wait until all runnable work is terminal
-> aggregate
-> parent SUCCESS / FAILED
```

## 2. 为什么默认 FAIL_AT_END

例如 SCD2 group 有 20 张表：

```text
customer          PASS
contact           FAIL
address           PASS
customer_balance  BLOCKED  # depends on contact
segment           PASS
...
```

Framework 不因为 `contact` 失败就取消其他独立表。最后 parent 仍然 `FAILED`。

这样同时满足：

- bulkhead / fault isolation；
- 最大化批次有用产出；
- 不把数据不完整伪装成 SUCCESS；
- dependency-aware blocking；
- 可精确重跑受影响 scope。

## 3. Execution-group examples

```text
framework_0_4/execution-groups/
  health_full_refresh.json
  health_scd2.json
```

两个例子都使用：

```text
failure_policy = FAIL_AT_END
```

但 DQ/quarantine 默认和个别 table override 不同。

### Full replace

适合 authoritative full snapshot tables。通常要特别重视：

- incomplete snapshot destructive guard；
- source/target reconciliation；
- DQ quarantine budget；
- 不因为一张表 snapshot 不完整而停止其他独立 full tables。

### SCD2

适合 WATERMARK + history tables。通常要特别重视：

- event ordering / tie breaker；
- SCD2 invariant reconciliation；
- watermark 只在 target + reconciliation gate PASS 后推进；
- quarantine threshold breach 不推进 state；
- replay retained bad rows after data/rule fix。

## 4. Pipeline 不应该自己实现哪些东西

Parent Fabric Pipeline 不应该复制：

```text
SCD2 SQL
watermark update
DQ rule engine
quarantine persistence
blind retry loop
unknown commit guess
per-table error table custom logic
```

这些属于 Framework HOW。

Domain repo 负责：

```text
which datasets
which execution group
business DQ rules
source/target mapping
criticality/dependencies
quarantine policy/budget
non-secret environment bindings
```

## 5. 故障后怎么修

主 runbook：

```text
docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md
```

Framework 侧更完整的语义说明：

```text
fabric-data-framework/docs/human/PIPELINE_OPERATIONS_AND_RECOVERY.md
```

安全原则：

```text
transient + explicitly retryable -> bounded RETRY
DQ threshold -> fix data/rule then REPLAY
reconciliation fail -> investigate first
dependency blocked -> recover upstream first
unknown commit -> reconcile before retry
bounded gap -> BACKFILL
authoritative reset only -> FULL_REBUILD
```

不要把“整批再跑一遍”当默认 incident response。
