---
name: visual-style-engine
description: Use when a task requires generating images or visual content with consistent, reproducible visual styles — choosing a style from content semantics, locking a project-wide visual identity across many images, compiling style specs into model-specific prompts, adapting prompts for Seedream/GPT Image/Flux/Midjourney/SDXL, or evaluating generated images for style consistency. Covers book illustrations, knowledge videos, posters, social media, product and education visuals.
agent_created: true
---

# AI Visual Style Engine

**Style 不是一个词，而是一份可执行的视觉规范。**

本技能提供一套模型无关的视觉风格引擎：定义风格 → 选择风格 → 锁定风格 → 编译为模型 Prompt → 参考图增强 → 一致性评估 → 自动纠偏。支撑图书精读、知识视频、文章配图、海报、社交、产品、教育等上层应用的多图统一视觉 Identity。

引擎根目录：`study_skills/visual-style-engine/`（下文所有相对路径均基于此）。

## 1. 何时使用本技能

触发：

- 需要为内容/文章/章节/视频页面生成一张或多张图片，且需要选择或保持一种视觉风格；
- 用户说 `style=auto`、问"适合什么画风"、提供内容让设计画面；
- 一个项目需要多张图片保持统一视觉语言（书、系列文章、视频、品牌、课程、栏目）；
- 已有 Visual Spec，需要编译成某个生图模型的 Prompt；
- 已有生成结果，需要做风格一致性 QA 或纠偏。

不触发：

- 纯讨论风格理论（只回答概念问题，不调用生成链路）；
- 需要精确排版/文字/图表数据渲染——交给 SVG / HTML / Remotion / 后期，本引擎的 Prompt 只负责视觉底图；
- 用户只想要单张一次性灵感图、无一致性要求时，可跳过 Identity 环节。

## 2. 核心原则（不可违反）

1. **Style 与 Prompt 分离**：`style-library/` 只存模型无关的视觉语义，不存模型参数。
2. **Style 与 Attribute 分离**：颜色/光影/构图/情绪是 Attribute，不因这些差异新建 Style。
3. **Canonical Spec 与 Model Adapter 分离**：模型差异由 `adapters/` 吸收，不重写 Style。
4. **项目多图必须有 Visual Identity**：Style Lock / Palette Lock / Texture Lock。
5. **Prompt 必须包含 Style Lock**：immutable（渲染方法/形状语言/线条语言/阴影政策/纹理政策）不可被改写；controlled（palette/lighting/composition/mood）可受限变化；free（subject/scene/action）自由。
6. **参考图是一致性的增强层**，参考的是"视觉语言"，不是固定人物或内容。
7. **生成之后必须评估**：维度级评分（shape/line/color/shading/lighting/texture/composition/detail），PASS / CORRECT / REGENERATE。
8. **新增 Style 必须经过检查**（第 20 节规则）：新 Shape Language？新 Rendering Method？新 Line Language？新 Material 行为？DNA 距离足够？若只是 Palette/Lighting/Era 差异 → 用 Attribute，不建 Style。

## 3. 协作链

### 3.1 自动风格模式（默认）

```text
User Content
   ↓
visual-intent-analyzer     内容 → Visual Intent（domain/visual_role/mood/密度/叙事模式）
   ↓
visual-style-selector      Intent → 候选 Style 排序 → 选中 Style + 原因
   ↓
visual-style-library       读取 Style Spec / DNA / Fingerprint / Rules
   ↓
visual-identity-manager    项目多图时建立 Visual Identity（可跳过单图）
   ↓
image-prompt-compiler       Visual Spec → Prompt AST → Locked Blocks → Canonical Prompt
   ↓
image-model-adapter         按模型编译（seedream/gpt-image/flux/midjourney/sdxl）
   ↓
(Image Generator)
   ↓
image-style-evaluator       维度评分 → PASS / CORRECT / REGENERATE（纠偏后重走 Compiler）
```

### 3.2 用户指定 Style

用户指定 Style ID（如 VE01）时，跳过 selector，直接 `visual-style-library → identity → compiler → adapter`。

### 3.3 用户提供参考图

参考图 → 提取视觉特征 → 匹配已知 Style 或生成 Custom Style（scope=project，人工确认 + Benchmark 后才可升级 library）→ Project Visual Identity。

## 4. 模块导航（按需加载对应子 Skill）

| 模块 | SKILL.md | 职责 |
|---|---|---|
| intent analyzer | `skills/visual-intent-analyzer/SKILL.md` | 从内容提取 Visual Intent |
| style selector | `skills/visual-style-selector/SKILL.md` | 候选 → 评分 → 选中 + 可解释原因 |
| style library | `skills/visual-style-library/SKILL.md` | 读/解释/比较 Style Spec、DNA、Fingerprint |
| identity manager | `skills/visual-identity-manager/SKILL.md` | 项目级 Style/Palette/Texture Lock |
| prompt compiler | `skills/image-prompt-compiler/SKILL.md` | Spec → AST → Canonical Prompt |
| model adapter | `skills/image-model-adapter/SKILL.md` | Canonical → 模型 Prompt |
| reference manager | `skills/style-reference-manager/SKILL.md` | 参考图选择与元数据 |
| style evaluator | `skills/image-style-evaluator/SKILL.md` | 维度评分、纠偏触发 |

## 5. 数据目录速查

```text
schemas/           7 个 Schema（style / attribute / preset / identity / reference / evaluation / visual-request）
style-library/     base/ 父类 + 16 个一级分类 + catalog.yaml + Core Style yaml
attributes/        palette / lighting / composition / camera / texture / material / line / shape / mood / era
presets/           Style + Attribute 稳定组合
strategies/        内容域策略（book / video / education / poster / social / branding / product）
adapters/          模型适配（seedream / gpt-image / flux / midjourney / sdxl）
references/        参考图索引（styles / projects）
evaluation/        profiles / confusion-matrix / correction-rules / benchmarks
tests/             skill-tests / style-tests / adapter-tests / regression
```

## 6. 统一协议（Envelope）

所有模块之间传递 `visual_request`（见 `schemas/visual-request.schema.yaml`）。每个 Skill 只修改自己负责的节点：intent-analyzer 写 `visual_intent`；selector 写 `style`；compiler 写 `generation`；evaluator 写 `evaluation`。禁止越权修改其他节点。

## 7. 冲突解决顺序

```text
Safety / system constraints
> Project Visual Identity
> Explicit Style Lock
> Explicit user scene requirements
> Attributes
> Model defaults
```

冲突时必须输出 `conflict: {type, feature}`，可选"保留 Style 移除冲突属性"或"用户明确要求时切换 Style"。

## 8. 版本与可复现

- Style / Adapter / Compiler / Preset 全部 SemVer。
- 项目生成记录保存 `{style_id, style_version, adapter, adapter_version, preset_id, compiler_version, references}`，保证 Style Library 更新后旧项目可复现（见 `schemas/visual-request.schema.yaml` 的 generation 节点）。

## 9. 快速开始（5 步）

1. 读 `schemas/visual-request.schema.yaml` 建 envelope。
2. 调用 `visual-intent-analyzer` 提取意图。
3. 有项目上下文（多图）→ `visual-identity-manager`；否则直接选 Style。
4. `image-prompt-compiler` → `image-model-adapter` 编译 Prompt。
5. 生成后 `image-style-evaluator` 评分；<80 分或命中 hard_fail 时按 correction rules 纠偏重试。
