# Style Tests — Style 质量测试

## 1. 结构校验（CI 必跑）

```bash
python3 tests/scripts/style-lint.py
```

通过标准：
- ERRORS = 0（必填字段 / ID 唯一 / Fingerprint 8 维 / DNA 0-10 范围）
- catalog ACTIVE 的 Style 必须有 yaml 定义
- WARNING（数量低于生产规格）应逐步清零

## 2. Schema 校验（第 64 节）

每个 Style yaml 对照 `schemas/style.schema.yaml`：
- Style ID unique / Version 合法（SemVer）
- MUST ≥5 / MUST_NOT ≥5
- Fingerprint 完整 / DNA 完整
- Positive / Negative anchor 非空
- Confusion rules 存在 / Benchmark 存在

## 3. 5 类 Benchmark 场景（第 35 节）

每个 Style 至少跑：
1. Portrait（人物）
2. Still Life（静物）
3. Architecture / Environment（建筑/环境）
4. Nature（自然）
5. Complex Multi-object Scene（复杂场景）

场景定义见 `evaluation/benchmarks/benchmarks.yaml`。

## 4. 新增 Style 前置检查（第 20 节）

新增前必须回答：
1. 是否存在新的 Shape Language？
2. 是否存在新的 Rendering Method？
3. 是否存在新的 Line Language？
4. 是否存在新的 Material/Pigment behavior？
5. 与已有 Style 的 DNA 距离是否足够？
6. 是否仅仅是 Palette / Lighting / Era 差异？（是 → 用 Attribute，不建 Style）

## 5. 生产规格达标清单（第 8 节）

| 模块 | 最低要求 |
|---|---|
| Summary / Detailed | 100–200 / 300–800 字 |
| Fingerprint | 8 维完整 |
| DNA | 11 个数值 |
| MUST / SHOULD / MAY / MUST NOT | ≥5 / ≥5 / ≥3 / ≥8 |
| Positive / Negative Anchor | 50–150 / 30–100 词 |
| Confusion / Correction | ≥2 / ≥5 |
| Test Prompts / References | ≥5 / ≥3 |
