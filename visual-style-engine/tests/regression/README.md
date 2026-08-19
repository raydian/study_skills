# Regression Tests — 回归测试

## 目的

Style / Adapter / Compiler 更新后，确保"优化"不使旧场景变差（第 67 节）。

## 三层回归

1. **Style Benchmark**：Core Style 的 5 类场景复跑，SSR 不下降；
2. **Adapter Benchmark**：跨模型一致性复测，CMCS 不下降；
3. **Project Sample Benchmark**：抽样项目图复评，PICS 不下降。

## 观测数据（第 46 节）

每次生成记录：

```yaml
request_id:
project_id:
style_id:
style_version:
preset_id:
adapter: {model, version}
compiled_prompt_hash:
reference_ids: []
generation_model:
evaluation_score:
corrections: []
retry_count:
```

## 质量指标（第 47 节）

- SSR — Style Success Rate：通过 QA 的生成次数 / 总生成次数
- CMCS — Cross Model Consistency Score：跨模型一致性
- PICS — Project Identity Consistency Score：项目多图一致性（20 张 ≥85）
- FDR — First-pass Design Rate：首轮通过率
- CRR — Correction Recovery Rate：纠偏恢复率

## 规则

- Style 生命周期变更（第 69 节）必须伴随回归：DRAFT→SPEC_READY 需 Benchmark；ACTIVE 更新需全量回归。
- 版本规则（第 43 节）：PATCH 词序 / MINOR 约束 / MAJOR DNA——MAJOR 变更必须人工评审。
