# Prompt AST 与 Lock 参考

## 锁定要素清单（第 26/27 节）

### 强锁定（immutable）— 来自 Style

- rendering_method
- shape_language
- line_language
- shading_policy
- texture_policy
- style_negative（负向锁）

### 半锁定（controlled）— 来自 Attributes / Identity

- palette（identity 锁定时高优先）
- lighting
- composition
- mood

### 自由（free）— 来自场景

- subject / object / environment / action

## 组装示例

Canonical Prompt（VE01 风格 + 田园场景）：

```text
[SUBJECT] a lone farmer standing in a vast field
[SCENE] an enormous geometric grid of farmland, distant granary, overcast day
[STYLE LOCK] minimal vector illustration, clean flat 2D visual language,
large simplified organic and geometric shapes, smooth crisp contours,
minimal shading, low visual complexity, generous negative space,
balanced contemporary editorial composition
[VISUAL ATTRIBUTES] muted earth palette, soft diffused light
[COMPOSITION] symbolic center, 40% negative space
[RENDERING REQUIREMENTS] limited controlled color palette, clear color separation
[NEGATIVE STYLE LOCK] photorealistic, photographic depth of field, 3D rendering,
PBR materials, complex realistic reflections, volumetric cinematic lighting,
oil painting brush strokes, watercolor bleeding, dense visual details
```

## 结构顺序建议

1. Subject（主体 + 动作）
2. Scene（环境 + 时间）
3. Style Lock（风格强锁定，紧随主体场景之后，防止漂移）
4. Visual Attributes（palette / lighting / mood）
5. Composition（构图）
6. Rendering Requirements（渲染要求，可并入 Style Lock）
7. Negative Style Lock（负向）

## 常见错误（baseline）

- 直接把 Style 名称当整个 prompt（没有加载 fingerprint 细节）；
- 把 palette 描述进 Style Lock（Style 与 Attribute 混淆）；
- 用户场景要求与 Style 冲突时直接照用户要求执行（应先输出 conflict）；
- 修改 immutable 区域的语义（如把 flat 2D 改成有景深）。
