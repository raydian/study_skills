---
name: visual-intent-analyzer
description: Use when a task needs to determine the appropriate visual expression for content — extracting visual intent (domain, visual role, mood, information density, narrative mode) from text, page, chapter, or topic semantics before any image generation.
agent_created: true
---

# Visual Intent Analyzer

从内容/主题/页面语义中提取 **Visual Intent**——"应该采用什么视觉表达"，而不选择具体 Style。

## 触发条件

触发：

- 用户给出内容（文章/章节/诗句/知识点/脚本），要求设计画面或配图；
- 需要判断视觉角色（概念解释 / 叙事 / 装饰…）；
- 进入自动风格模式的第一步。

不触发：

- 用户已明确提供 Visual Intent 数据（直接跳过，进入 selector）；
- 用户只问"这个 Style 好不好"。

## 输入

```yaml
content: "..."            # 内容本体（必填）
usage: book_video         # 用途：book / book_video / video / poster / social / product / education / branding
audience: "..."           # 目标受众（可空，如 高中学生 / 职场人士）
project_context: "..."    # 项目上下文（可空，如书名、系列名）
```

## 输出（写入 visual_request.visual_intent）

```yaml
domain: history           # 内容域：history / science / literature / business / psychology / education / fiction ...
content_type: nonfiction  # nonfiction / fiction / poetry / data / procedure / argument
visual_role: conceptual_explanation
  # 可选：conceptual_explanation / narrative_scene / decorative / data_viz / metaphor / portrait / product_show
mood:
  - reflective            # 情绪标签（见 attributes/mood/ 词汇表）
  - intellectual
information_density: medium   # low / medium / high（决定细节密度需求）
narrative_mode: symbolic     # symbolic / literal / abstract / documentary / persuasive
realism_need: medium         # low / medium / high
abstraction_need: medium     # low / medium / high
```

## 决策流程

1. **读内容**：识别主题、时代背景、情绪基调、信息层级（概念/叙事/数据）。
2. **判定 domain** 与 content_type（参考 strategies/ 内容域策略）。
3. **判定 visual_role**：内容在页面中承担什么角色——解释概念（conceptual_explanation）、讲故事（narrative_scene）、表达抽象关系（metaphor/symbolic）？
4. **提取 mood**：从用词、情绪、文体推断，最多 3 个，来自 mood 词表。
5. **估信息密度**：内容需要画面承载多少信息细节（纯概念低密度 vs 地图/流程高密度）。
6. **定 narrative_mode**：内容以何种方式表达——写实陈述、象征隐喻、抽象、纪实、说服。
7. 写入 envelope 的 `visual_intent` 节点，**不要**选择 Style、不写 Prompt。

## 关键约束

- 只输出意图，**不越权**选择 Style / 编译 Prompt / 生成图片。
- mood 使用 `attributes/mood/` 词表，不用自由词。
- realism_need 与 abstraction_need 供 selector 排序使用；二者可同时非极端。
- 单图与多图项目的意图一致（多图由 identity-manager 接管）。

## 质量自检

- [ ] domain / content_type 有明确值
- [ ] visual_role 与内容角色匹配（解释类内容误判为装饰即失败）
- [ ] mood ≤3 个且来自词表
- [ ] narrative_mode 有依据
