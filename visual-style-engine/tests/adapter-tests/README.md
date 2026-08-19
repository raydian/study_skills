# Adapter Tests — Adapter 质量测试

## Adapter Lint（第 66 节）

每个 adapter 输出前检查：

- [ ] 未删除 Style 的 MUST
- [ ] 未引入 Style 的 MUST NOT 特征
- [ ] 未改变 Style 核心定义（DNA/Fingerprint/Rules）
- [ ] 未使用已废弃模型参数
- [ ] Prompt 包含完整 Style Lock（强锁定块语义一致）
- [ ] 模型不支持的能力走了 fallback（第 54 节），未硬生成

## Cross-model Benchmark（第 36 节）

同一 Canonical Spec 跑 4 个模型（Seedream / GPT Image / Flux / Midjourney）：

```text
| Style | Seedream | GPT Image | Flux | MJ | Cross-model |
```

验收：
- 单模型 ≥80、Cross-model ≥80（Core 20 ≥85）
- 低于阈值优先调整 Adapter，**不先修改 Canonical Style**

## 模型句式对比用例

| 模型 | 检查点 |
|---|---|
| seedream | 长 Prompt 完整保留；参考图多图 |
| gpt-image | 句子化；负向为文字排除 |
| flux | 关键词精简；正向锚定 |
| midjourney | --no 参数；--ar/--style raw；参考图 --iw |
| sdxl | 独立 negative prompt；quality tags；LoRA 合规 |

## 回归（第 67 节）

Style 更新后自动重跑：Style Benchmark + Adapter Benchmark + Project Sample Benchmark。
重点关注：Style 的"优化"不能让旧场景变差。
