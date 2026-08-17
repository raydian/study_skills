# Identity 指南

## 什么时候需要 Identity

| 场景 | 需要 |
|---|---|
| 单张封面/单图 | 否 |
| 一本书（多章节配图） | 是 |
| 一条知识视频（多帧插画） | 是 |
| 系列文章 / 专栏 | 是 |
| 品牌 / 课程 / 栏目 | 是 |
| 社交媒体日常单图 | 视品牌需要 |

## 书的 Identity 设计（第 49 节）

```yaml
primary_style: IL03
allowed_secondary: [CI08, PR04]
palette_lock: PAL_MUTED_EARTH
texture_lock: TEX_FINE_GRAIN
style_distribution: {IL03: 0.60, CI08: 0.25, PR04: 0.15}
```

一本书：主 Style 统一，场景 Style 有限变化，Palette/Texture 统一，Mood 在范围内变化。

## 人物项目（第 51 节）

```yaml
character_identity:   # 与 Style 分离
  face: ...
  hair: ...
  age_range: ...
  body: ...
  clothing: ...

style_identity:       # 可单独变化
  style: ...
  palette: ...
  rendering: ...
```

## 海报（第 50 节）

海报额外分析 typography area / title safe area / negative space / reading order / copy amount。Prompt 只生成视觉底图时明确要求 `leave clean negative space for typography`；大量文字后置排版。

## 自定义 Style（第 52/53 节）

- Derived Style：`extends: DR07` + overrides（仅 allowed_variations 内）。
- Custom Style：参考图 → Extract → Normalize → Remove subject-specific → Fingerprint → Rules → Test → Save。
- 默认 scope=project；人工确认 + Benchmark 后才可升级 scope=library。
