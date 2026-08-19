# Style Library 目录导航

## 16 个一级分类 → 目录

| 分类 | 目录 | 数量 |
|---|---|---|
| Photography | photography | 16 |
| Cinematic | cinematic | 12 |
| Anime / Manga | anime | 14 |
| Illustration | illustration | 16 |
| Vector | vector | 12 |
| Painting | painting | 16 |
| Drawing | drawing | 12 |
| Eastern Art | eastern-art | 14 |
| Print Art | print | 10 |
| 3D / CGI | 3d | 16 |
| Craft | craft | 12 |
| Graphic Design | graphic-design | 16 |
| Concept / Game Art | concept-art | 12 |
| Fantasy / Surreal | fantasy | 16 |
| Retro / Era | retro | 14 |
| Information / Scientific | information | 14 |

## base/ 父类

| 父类 | 基线 |
|---|---|
| VECTOR_BASE | dimensionality: 2D / edge_policy: clean / realistic_material: false / pbr: false / photographic_depth_of_field: false |
| PAINTING_BASE | material pigment behavior / brush evidence / non-photographic |
| EASTERN_BASE | 东方水墨/矿物色/留白传统 |
| PRINT_BASE | 印刷介质、网点/版痕、历史感 |

> 每个分类可补充自己的 BASE（如 ILLUSTRATION_BASE）。新增 Style 优先挂在现有 BASE 下，不重复定义公共属性。

## 检索别名

Style 文件的 `aliases` 字段支持自然语言检索。示例：
- VE01 aliases: [minimalist vector illustration, clean vector art]
- DR07 aliases: [vintage ink sketch, loose ink drawing]

## 读取切片建议

- **selector**：DNA + compatibility + visual_intent + use_cases
- **compiler**：fingerprint + rules + canonical_prompt + allowed_variations
- **evaluator**：confusion_with + correction_rules + evaluation_profile
- **identity**：rules.must_not + forbidden_features + allowed_variations
