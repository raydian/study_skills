---
name: image-model-adapter
description: Use when a canonical prompt must be compiled for a specific image generation model — translating the model-independent visual spec into the phrasing, ordering, and parameters that Seedream, GPT Image, Flux, Midjourney, or SDXL understand best.
agent_created: true
---

# Image Model Adapter

将 **Canonical Visual Spec → 特定模型最容易理解的表达方式**。模型差异在此吸收，Style 核心定义不可改变。

## 触发条件

触发：

- 已有 Canonical Prompt，需要发往具体模型（seedream / gpt-image / flux / midjourney / sdxl）；
- 需要模型参数（aspect ratio、quality、style ref、seed 等）。

不触发：

- 还没有 Canonical Prompt（先去 compiler）；
- 用户只在讨论模型能力。

## 责任边界

**允许**：

- 改变句式（关键词列表 ↔ 自然语言）；
- 改变关键词排序；
- 英文关键词转成自然语言；
- 根据模型删减无效词；
- 添加模型特有参数（如 MJ 的 `--ar 16:9`、`--style raw`）。

**不允许**：

- 修改 Style DNA；
- 删除 MUST；
- 引入 MUST NOT 特征；
- 将 Style A 翻译为 Style B。

## Adapter 文件（adapters/<model>/）

```text
adapters/
├── seedream/       seedream.md + 旗舰 Style 适配示例
├── gpt-image/      gpt-image.md
├── flux/           flux.md
├── midjourney/     midjourney.md
└── sdxl/           sdxl.md
```

每个模型文件描述：`prompt_behavior`（natural_language / keyword_density / long_prompt_tolerance）、`capabilities`（reference_image / negative_prompt / typography / image_editing）、`compile_rules`（subject/scene/style/attributes/negative/reference 的句式与排序）、`fallback_rules`、`unsupported_features`。

## 决策流程

1. 读取 `adapters/<model>/<model>.md` 的 compile_rules 与 capabilities。
2. 按模型句式规则重写 Canonical Prompt 各块（保持强锁定语义不变）。
3. 处理能力差异：模型不支持的属性 → fallback（如复杂文字 → 无字图 + 后置排版，不硬生成）。
4. 追加模型参数（画幅/质量/风格引用等）。
5. 输出最终 prompt + negative_prompt + parameters，写入 generation 节点（含 adapter 版本）。

## 模型速查

| 模型 | 句式偏好 | 负向支持 | 参考图 | 备注 |
|---|---|---|---|---|
| Seedream | 自然语言描述 + 中密度关键词 | 中 | 支持（可多图） | 长 Prompt 容忍度高 |
| GPT Image | 自然语言描述 | 弱（用文字排除） | 支持 | 不适合关键词堆叠 |
| Flux | 关键词 + 简短短语 | 弱 | 部分 | 简洁有效 |
| Midjourney | 短语 + 参数后缀 | 强（--no） | 强（image prompt） | 有 --ar/--style 等 |
| SDXL | 正向短语 + 负向短语分离 | 强（negative prompt） | 中（IP-Adapter） | 可用 LoRA/embedding |

## 质量自检

- [ ] 强锁定语义与 Canonical 一致（Adapter Lint 通过）
- [ ] 未删除 MUST / 未引入 MUST NOT
- [ ] 模型不支持的能力走了 fallback，而非硬生成
- [ ] 输出了 adapter 版本（可追溯）
