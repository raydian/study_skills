---
name: visual-identity-manager
description: Use when a project needs many images, pages, or scenes to share a consistent visual language — establishing and enforcing project-level Visual Identity with style, palette, texture, and mood locks.
agent_created: true
---

# Visual Identity Manager

项目级视觉身份管理。一本书、一条知识视频、一个系列文章、一个品牌、一门课程、一个社交栏目，一旦需要多图，就应建立 Visual Identity。

## 触发条件

触发：

- 项目需要多张图片 / 多页面 / 多场景保持统一视觉语言；
- 已有 Visual Identity，需要为某张图取约束；
- 用户指定"这本书/这个视频/这个系列用什么风格统一"。

不触发：

- 单张一次性图片（直接走 selector → compiler）；
- 用户只要某张图换个风格。

## 负责

```yaml
project_id: book_sapiens_001

primary_style:
  id: IL03
  version: 1.2.0

secondary_styles:        # 白名单：变化场景只能用这些
  - {id: CI08, version: 1.0.0}
  - {id: PR04, version: 1.0.0}

palette: PAL_MUTED_EARTH
texture: TEX_FINE_GRAIN

mood:
  base: [intellectual, reflective]
  range: [poetic, documentary]

era: null                # 如 ERA_TANG_DYNASTY

style_lock:
  shape: high
  line: high
  palette: medium
  texture: high
  composition: medium

references:
  project: [REF_PROJECT_01, REF_PROJECT_02]

style_distribution:      # 可选。风格分布
  IL03: 0.60
  CI08: 0.25
  PR04: 0.15
```

## 决策流程

1. **确认主 Style**：由用户指定或 selector 推荐（单图选择在项目语境下应服从 Identity）。
2. **定白名单**：secondary_styles 数量 2–5，且与主 Style 的 confusion 风险低。
3. **锁 Palette / Texture / Mood Range / Era**：mood 只允许在范围内变化。
4. **定 style_lock 强度**：shape/line 通常 high（强锁定），palette/composition medium（允许受限变化）。
5. **登记 references**：项目参考图（approved 优先）。
6. **分布控制**（长内容项目）：style_distribution 约束各 Style 出现比例。
7. 输出 identity 节点；之后每次生成，compiler 必须以 identity 为最高 Style Lock。

## 关键约束

- Identity 一经建立即成为**冲突解决优先级 #2**（仅低于安全/系统约束）。
- 不允许脱离 Identity 随意换 Style；用户明确要求例外时记录冲突并确认。
- 人物项目（第 51 节）：character_identity（face/hair/clothing…）与 style_identity 分离——换画风不改人物身份，换人物不漂风格。
- 版本锁定：primary_style.version 必须记录，保证可复现。
- 自定义 Style 默认 scope=project，不污染公共库（第 53 节）。

## 输出（写入 visual_request.identity）

```yaml
project_id, primary_style{id,version}, secondary_styles[], palette,
texture, mood{base,range}, era, style_lock{}, references[], allowed_variations[], forbidden_styles[]
```

## 质量自检

- [ ] primary_style 有版本锁定
- [ ] secondary_styles 与 primary 不高度混淆
- [ ] style_lock 明确（shape/line high）
- [ ] 参考图已 approved
- [ ] 长内容项目有 style_distribution
