---
name: style-reference-manager
description: Use when reference images are needed to enhance visual consistency — selecting canonical references for a style, curating project references, or validating that reference images represent the style's visual language rather than specific subjects.
agent_created: true
---

# Style Reference Manager

管理参考图，增强生成一致性：Style canonical references、project references、line/palette/texture/composition references。

## 触发条件

触发：

- 需要为生成挑选参考图（风格参考 / 线条参考 / 色板参考…）；
- 需要校验已有参考图是否合格；
- 项目建立/更新参考集。

不触发：

- 生成图片本身（那是 generator 的事）。

## 参考图角色（第 31.2 节）

```yaml
references:
  overall_style: []   # 整体风格参考（3–6 张 / Core Style）
  line: []
  palette: []
  texture: []
  composition: []
  character: []
```

## 每个 Style 最低参考图（第 31.1 节）

必选 subject 类型：portrait / still_life / environment。
推荐增加：architecture / complex-scene / abstract。

## 元数据（schemas/reference.schema.yaml）

```yaml
id: REF_IL03_01
source: "..."
license: "..."
style_id: IL03
style_version: 1.2.0
role: overall_style
subject: environment
approved: true
created_at: "2026-08-17"
```

## 决策流程

1. 读取 Style 的 reference_policy（minimum_reference_count、reference_types）。
2. 检查现有 references：覆盖 subject 类型？approved 数量足够？
3. 缺口 → 生成/采集候选参考图（用该 Style 的 benchmark 场景生成，或人工挑选）。
4. 校验质量（见下），打 metadata，标记 approved（人工）。
5. 输出参考清单到 envelope 的 references 节点。

## 参考图质量检查（第 48 节）

- 是否覆盖不同 Subject（不能只有人物）？
- 是否过度依赖某个具体内容（参考的是视觉语言，不是固定内容）？
- 是否包含错误 Style 特征？
- 色彩是否代表 Style 而非单一 Preset？
- 是否存在过强角色 Identity（应避免固定人物）？

## 关键约束

- 参考"视觉语言"，不参考"固定人物/内容"；
- 未 approved 的参考图不用于正式生成；
- 项目参考（project scope）与公共库（library scope）分开存放：`references/projects/` vs `references/styles/`。

## 输出（写入 visual_request.references）

```yaml
- id: REF_PROJECT_01
  role: overall_style
  approved: true
```

## 质量自检

- [ ] 参考图覆盖 ≥3 种 subject 类型
- [ ] 无过强角色 Identity / 无错误 Style 特征
- [ ] metadata 完整（license / style_id / version / role / approved）
- [ ] 未 approved 的未混入生成清单
