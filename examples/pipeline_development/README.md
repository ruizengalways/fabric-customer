# Fabric Pipeline Development Examples

这部分是正常业务 Pipeline 的 reference implementation，不是 Framework certification fixture。

目标是让新项目直接看懂：一个 parent Fabric Pipeline 如何用 bounded ForEach / reusable child 执行很多 DatasetConfig，同时做到 table fault isolation、fail-at-end、DQ/quarantine、dependency-aware blocking 和可审计恢复。

## 0. 版本边界

Customer production dependency 仍然必须保持：

```text
fabric-data-framework==0.3.0
```

下面 `framework_0_4/` 的 execution-group policy 是 Framework 0.4 development contract 的**前向 reference**。在 immutable v0.4.0 发布并获准迁移之前：

- 不把这些文件移动到 production runtime config；
- 不修改 `pyproject.toml` production pin；
- 可以用于设计评审、项目模板、静态 CI contract 和下一版准备。

当前 0.4 compatibility baseline 是 Framework PR #107 / main SHA：

```text
4c8ad9994f3800e901c146b919f85454d78f080e
```

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
-> bounded parallel dispatch
-> reusable child / framework dataset execution
-> every dataset writes durable semantic outcome
-> failed dependencies become BLOCKED
-> wait until all runnable work is terminal
-> aggregate
-> parent SUCCESS / FAILED
```

## 2. 为什么默认 FAIL_AT_END

例如 SCD2 group 有 20 张表：

```text
history_001       PASS
history_002       FAIL
history_003       PASS
history_004       BLOCKED  # only if it depends on history_002
history_005       PASS
...
```

Framework 不因为一张表失败就取消其他独立表。最后 parent 仍然 `FAILED`。

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
  health_scd1.json
  health_debezium.json
```

四个例子都使用：

```text
failure_policy = FAIL_AT_END
```

并且都把 DQ/quarantine 默认值放在 group policy，把真正的例外放在 per-dataset override。

### FULL -> REPLACE

适合 authoritative full snapshot tables。重点：

- incomplete snapshot destructive guard；
- source/target reconciliation；
- DQ quarantine budget；
- 一张表坏掉不停止其他独立 full tables。

### WATERMARK -> SCD2

适合 history tables。重点：

- event ordering / tie breaker；
- SCD2 invariant reconciliation；
- watermark 只在 target + reconciliation gate PASS 后推进；
- quarantine threshold breach 不推进 state；
- 修数据/规则后 replay retained bad rows。

### WATERMARK -> SCD1

适合 current-state tables。重点：

- watermark + tie-breaker/overlap；
- deterministic merge key；
- accepted/quarantined/accounting reconciliation；
- retry 时不重复推进 state。

### Debezium CDC -> UPSERT

适合有 ordered CDC log 的表。重点：

- Framework 不和 Debezium/external connector 争抢 checkpoint ownership；
- event ordering/dedupe identity 保持稳定；
- connector lag/log retention 是 RPO 风险；
- 丢失的 log range 不能用普通 retry 假装补回来。

## 4. Pipeline 不应该自己实现哪些东西

Parent Fabric Pipeline 不应该复制：

```text
SCD1/SCD2 SQL
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

## 5. Source-controlled precedence

Framework 0.4 policy precedence 固定为：

```text
DatasetConfig
-> execution-group quality defaults
-> execution-group per-dataset patch
-> audited RuntimeOverride
```

不要在 Fabric UI 维护另一套看不见的长期 default。Execution-group policy 一旦成为正式 runtime input，其 exact bytes 必须进入 release/config identity。

## 6. 故障后怎么修

Customer 主 runbook：

```text
docs/runbooks/OPERATE_MULTI_TABLE_PIPELINES.md
```

Framework 侧完整语义说明：

```text
fabric-data-framework/docs/human/PIPELINE_OPERATIONS_AND_RECOVERY.md
```

安全原则：

```text
transient + explicitly retryable -> bounded RETRY
DQ threshold -> fix data/rule then REPLAY
reconciliation fail -> investigate first
dependency blocked -> recover upstream first
UNKNOWN_COMMIT -> reconcile before retry
bounded gap -> BACKFILL
authoritative reset only -> FULL_REBUILD
```

不要把“整批 blind retry”当默认 incident response。

## 7. 新项目落地顺序

```text
fabric-framework project-init <repo> --domain <domain>
-> DatasetConfig + semantic selections
-> execution_group assignment
-> fabric-framework project-validate <repo>
-> source-controlled execution-group policy（等 v0.4 正式允许生产使用后）
-> CI
-> DEV/UAT failure/recovery validation
-> PROD promotion
```

100-table fixture 仍然是 onboarding/config scale proof，不是 runtime performance benchmark。实际 `max_concurrency` 必须根据 source throttling、Fabric capacity、Spark/Warehouse queueing 和业务 SLA 在 DEV/UAT 量测后调整。
