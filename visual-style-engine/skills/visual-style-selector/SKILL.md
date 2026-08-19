---
name: visual-style-selector
description: Use when a visual style must be chosen for generated images — when style is set to auto, when the user asks what style fits their content, or when a Visual Intent needs to be ranked against candidate styles in the library.
agent_created: true
---

# Visual Style Selector

根据 Visual Intent 选择 Style / Preset / Style Strategy。**不靠 LLM 直觉硬选**，采用"语义提取 + 可解释评分"。

## 触发条件

触发：

- `style=auto`；
- 用户问"适合什么画风 / 用什么风格好"；
- 有 visual_intent，需要落 Style。

不触发：

- 用户已明确指定 Style ID 且无需推荐（直接去 style-library）；
- 用户只在讨论风格理论。

## 输入

```yaml
visual_intent: {}     # intent-analyzer 输出（domain/visual_role/mood/密度/叙事模式）
project_context: {}   # 可空。已有 Visual Identity / Strategy
medium: "16:9"        # 媒介与画幅
```

## 输出（写入 visual_request.style）

```yaml
candidates:
  - style: IL03
    score: 0.92
  - style: CI08
    score: 0.84

selected:
  style: IL03
  version: 1.2.0
  confidence: 0.92

reason:
  - conceptual explanation
  - symbolic representation
  - adult knowledge content
```

## 评分公式（默认权重）

```text
Score = ContentMatch×0.25 + VisualRoleMatch×0.20 + NarrativeMatch×0.15
      + MoodMatch×0.10 + AudienceMatch×0.08 + MediumMatch×0.07
      + IdentityMatch×0.10 + ConsistencyRisk×0.05
```

权重允许被 `strategies/<domain>/` 覆盖（如文学类 mood_weight: high）。

## 决策流程

1. 加载相关 `strategies/<domain>/strategy.yaml`（若有），获取 primary/secondary/avoid 白黑名单。
2. 读取 `style-library/` 候选分类的 catalog.yaml，构建候选池。
3. 对每个候选计算 8 项得分（对照该 Style 的 visual_intent 标签、compatibility、DNA 与意图的吻合度）。
4. 排除：非 ACTIVE 状态、在 strategy avoid 名单、incompatible。
5. 取 top 3 输出 candidates + selected + reason。
6. 若命中已有 Project Visual Identity：IdentityMatch 加权，保持主 Style 优先，变化场景从 secondary_styles 白名单内选。

## 关键约束

- 只选 Style，**不修改 Spec、不编译 Prompt**。
- 必须有可解释 reason（可追溯），禁止只输出 ID 无理由。
- 不确定时列出 top 3 让用户确认，confidence < 0.7 时标注"建议人工确认"。
- 候选与选中须来自 `style-library/` 的 ACTIVE 定义；找不到匹配时返回最接近的 Style 并附差异说明，或建议用 Attribute 组合微调。

## 质量自检

- [ ] candidates 有分数且可解释
- [ ] 没有把 Attribute（palette/lighting）当 Style 选
- [ ] 没有把 Era 当 Style 选（年代视觉成为主语言时除外）
- [ ] reason 与 visual_intent 逐条对应
