---
name: image-prompt-compiler
description: Use when a Visual Spec exists and must be converted into a model-ready prompt — assembling subject, scene, style lock, attributes, and negative lock into a canonical prompt structure before model adaptation.
agent_created: true
---

# Image Prompt Compiler

把 Visual Spec 编译为**模型无关的 Canonical Prompt**。不直接拼字符串——先生成 Prompt AST，再按固定结构输出。

## 触发条件

触发：

- 已有 Style / Visual Spec（含 identity），需要模型 Prompt；
- 自动风格链路中 compiler 环节。

不触发：

- 用户只在讨论风格理论；
- 还没有 Style 确定（先去 selector）。

## 流水线

```text
Visual Spec（style + attributes + identity + scene）
   → Prompt AST（结构化中间表示）
   → Locked Blocks（拆分可变/半锁定/强锁定）
   → Model-independent Canonical Prompt
```

## Prompt AST（参考 schemas/visual-request.schema.yaml generation 节点）

```yaml
subject:
  main: lone person
  action: standing
  attributes: []
scene:
  environment: enormous modern city
  time: overcast day
style:
  id: IL03
  version: 1.2.0
attributes:
  palette: PAL_MUTED_BLUE_GRAY
  lighting: LIGHT_OVERCAST_SOFT
  composition: CMP_EXTREME_NEGATIVE_SPACE
  mood: [lonely, introspective]
locks:
  style: true
  palette: true
negative:
  inherit_style_negative: true
```

## 固定结构

```text
[SUBJECT] [SCENE] [STYLE LOCK] [VISUAL ATTRIBUTES] [COMPOSITION] [RENDERING REQUIREMENTS] [NEGATIVE STYLE LOCK]
```

### 锁定分级

| 级别 | 元素 | 行为 |
|---|---|---|
| 可变 | subject / scene / action | 按任务变化 |
| 半锁定 | palette / lighting / composition / mood | 受限变化（来自 attributes，identity 锁定者不可改） |
| 强锁定 | shape / line / rendering / shading / texture / style negative | 来自 Style 定义，**禁止改写语义** |

## 决策流程

1. 加载 Style Spec（style-library），提取 fingerprint → 强锁定块、canonical_prompt → 正向锚点、negative_anchor。
2. 合并 Attributes（palette/lighting/composition/mood），转成半锁定块。
3. 叠加 Identity（若存在）：identity 锁定维度优先级 > 单图 attributes。
4. 组装 AST → 检查冲突（见下）。
5. 按固定结构输出 Canonical Prompt + Negative Prompt（模型无关）。

## 冲突处理

冲突顺序：Safety > Identity > Explicit Style Lock > Explicit user scene > Attributes > Model defaults。

冲突输出：

```yaml
conflict:
  type: style_violation
  feature: realistic skin pores
```

可选：保留 Style 移除冲突属性；或用户明确要求时切换 Style。

## Prompt 长度治理（第 56 节）

- Core Anchor（强锁定）：不可省；
- Support Anchor：模型能力允许时使用；
- Scene Description：按任务变化；
- Negative Lock：只保留真正会导致风格漂移的核心负向约束。

禁止为"更稳定"堆叠同义词。

## 输出（写入 visual_request.generation）

```yaml
prompt_ast: {}
canonical_prompt: ""
negative_prompt: ""
locks: {style: true, palette: true}
conflicts: []
```

## 质量自检

- [ ] 强锁定块来自 Style 定义原文，未被改写
- [ ] negative 继承 Style negative（inherit_style_negative）
- [ ] identity 锁定维度未被单图属性覆盖
- [ ] Prompt 长度合理，无同义词堆叠
