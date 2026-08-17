# AI Visual Style Engine & Skill System
## AI 生图视觉风格引擎与 Skill 体系完整设计方案

> 版本：v1.0  
> 文档状态：总体设计 / 可实施  
> 目标：基于本方案，可继续创建 Visual Style Library、Style Selector、Prompt Compiler、Model Adapter、Reference Manager、Style Evaluator 等一组可组合的 AI Skill，并逐步建设 200+ 标准视觉风格知识库。

---

# 0. 文档摘要

本方案设计一套模型无关的 **AI Visual Style Engine（AI 视觉风格引擎）**。它不是一组 Prompt 收藏，也不是简单的“风格名称字典”，而是一套能够：

- 定义视觉风格；
- 选择视觉风格；
- 锁定视觉风格；
- 将统一视觉规范编译成不同模型 Prompt；
- 通过参考图增强视觉一致性；
- 对生成结果进行风格一致性检测；
- 自动纠偏和重新生成；
- 对项目级、多图、多页面内容保持统一视觉 Identity；
- 支撑图书精读视频、文章配图、知识视频、海报、社交媒体、人物、产品、教育内容等上层应用。

本方案的核心原则是：

> **Style 不是一个词，而是一份可执行的视觉规范。**

因此，不使用 `cinematic`、`minimal vector`、`watercolor` 等单一关键词作为 Style 的最终定义，而是将每个 Style 明确拆解为：

**Shape + Line + Color + Shading + Lighting + Texture + Composition + Spatial Depth + Detail + Material + Character Rendering + Background + Constraints**

再通过：

**Canonical Style Spec → Model Adapter → Model-specific Prompt**

解决 Seedream、GPT Image、Flux、Midjourney、SDXL 等不同模型之间的风格解释差异。

---

# 1. 建设目标

## 1.1 核心目标

建设一个统一、结构化、版本化、可评测的视觉风格体系，使得：

1. 同一个 Style 在不同主题下保持相同视觉语言；
2. 同一个 Style 在不同生图模型中差异可控；
3. 同一项目连续生成几十、几百张图片时不发生明显风格漂移；
4. 上层业务无需理解模型 Prompt 差异；
5. Style 可以被选择、继承、组合、版本化和测试；
6. 风格库可以持续扩展而不会无限产生重复风格；
7. 每个 Style 都可以通过标准测试场景进行验证；
8. AI 可以根据内容语义自动选择合适风格；
9. 人工仍可明确指定 Style、Palette、Lighting 等参数；
10. 新模型接入时主要新增 Adapter，而不是重写整个 Style Library。

## 1.2 设计原则

- **模型无关**：Style 定义不绑定具体模型。
- **风格可执行**：每个 Style 必须有结构化视觉规则。
- **属性可组合**：颜色、光影、构图等不无限膨胀为新 Style。
- **项目可锁定**：多图项目使用 Visual Identity 控制一致性。
- **输出可评测**：不是“看起来差不多”，而是有维度级评分。
- **规则可验证**：能够通过 Schema/Lint/Benchmark 验证的内容尽量交给代码。
- **版本可追溯**：Style、Adapter、Compiler、Preset 都必须版本化。
- **Skill 可测试**：Skill 本身必须有 baseline、压力场景和回归测试。

---

# 2. 非目标

本系统不负责：

- 训练基础生图模型；
- 替代具体生图平台；
- 解决模型本身无法生成的内容；
- 直接承担精确排版、复杂文字、数据图表渲染；
- 将所有审美概念都定义成独立 Style；
- 用一个超长 Prompt 强行解决所有问题。

复杂文字、坐标、图表数值、精确 Logo、UI 字段等，应优先通过 SVG / HTML / Canvas / Remotion / 后期排版完成。

---

# 3. 核心概念模型

## 3.1 Style

Style 是完整视觉语言，负责回答：

> **这张图“应该长什么样”。**

例如：

- Minimal Vector Illustration
- Editorial Conceptual Illustration
- Vintage Loose Ink Sketch
- Traditional Watercolor
- Cinematic Film Still
- Risograph Print
- Miniature Diorama

## 3.2 Attribute

Attribute 是可以跨 Style 组合的视觉参数，例如：

- Palette
- Lighting
- Composition
- Camera
- Texture
- Material
- Mood
- Era
- Line
- Shape

例如：

```text
Minimal Vector Illustration
+
Bright Candy Palette
+
Airy Composition
+
Flowing Curved Lines
```

而不是再创建一个新的 `Candy-Airy-Flowing-Minimal-Vector Style`。

## 3.3 Preset

Preset 是 Style + 一组常用 Attribute 的稳定组合，例如：

- 极简矢量 · 糖果清新
- 极简矢量 · 企业科技
- 极简矢量 · 莫兰迪生活方式
- 复古线稿 · 米黄纸张
- 电影剧照 · 历史纪实

Preset 方便普通用户直接调用，但底层仍保持 Style 与 Attribute 分离。

## 3.4 Visual Identity

Visual Identity 是项目级视觉身份，适用于：

- 一本书；
- 一条知识视频；
- 一个系列文章；
- 一个品牌；
- 一个课程；
- 一个社交媒体栏目。

它定义整个项目共享的：

- Primary Style
- Secondary Styles
- Palette
- Texture
- Typography direction
- Contrast
- Mood
- Era
- ReferenceSet

## 3.5 Style DNA

Style DNA 是每个 Style 的数值化视觉向量，用于：

- 比较风格；
- 防止重复；
- 风格选择；
- 一致性检测；
- 风格距离计算。

示例：

```yaml
realism: 1
abstraction: 8
detail_density: 2
spatial_depth: 2
texture_strength: 1
line_presence: 5
line_roughness: 1
lighting_complexity: 1
shading_strength: 1
```

## 3.6 Style Fingerprint

Style Fingerprint 是 Style 最重要的八类视觉指纹：

1. Shape
2. Line
3. Color
4. Shading
5. Lighting
6. Texture
7. Composition
8. Detail

只要这八项稳定，即使 Subject 完全不同，图片仍然应该属于同一种视觉语言。

---

# 4. 总体系统架构

```text
┌──────────────────────────────────────────────────┐
│                 Application Skills               │
│ Book / Video / Poster / Social / Product / Edu   │
└────────────────────────┬─────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────┐
│              Visual Intent Analyzer              │
│ 内容 / 场景 / 用途 / 受众 / 情绪 / 信息密度      │
└────────────────────────┬─────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────┐
│                  Style Selector                  │
│ Candidate Styles → Ranking → Style Strategy      │
└────────────────────────┬─────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────┐
│               Visual Style Library               │
│ Style Spec / DNA / Rules / Attribute / Preset    │
└────────────────────────┬─────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────┐
│               Project Visual Identity            │
│ Style Lock / Palette Lock / Reference Lock       │
└────────────────────────┬─────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────┐
│                 Prompt Compiler                  │
│ Subject + Scene + Style Lock + Attributes        │
└────────────────────────┬─────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────┐
│                  Model Adapter                   │
│ Seedream / GPT Image / Flux / MJ / SDXL          │
└────────────────────────┬─────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────┐
│                 Image Generator                  │
└────────────────────────┬─────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────┐
│             Style Consistency Evaluator          │
│ Fingerprint / DNA / References / Constraints     │
└───────────────┬───────────────────┬──────────────┘
                ↓                   ↓
              PASS             CORRECT/RETRY
```

---

# 5. Skill 体系设计

建议拆分为 8 个 Skill，而不是一个巨型 Skill。

## 5.1 `visual-intent-analyzer`

### 触发条件

当任务需要从内容、主题或页面语义中判断“应该采用什么视觉表达”时使用。

### 输入

- content
- usage
- audience
- emotional_tone
- information_density
- project_context

### 输出

```yaml
domain: history
content_type: nonfiction
visual_role: conceptual_explanation
mood:
  - reflective
  - intellectual
information_density: medium
narrative_mode: symbolic
```

### 不负责

- 最终选择 Style；
- 编译模型 Prompt；
- 生成图片。

## 5.2 `visual-style-selector`

### 触发条件

需要根据 Visual Intent 选择 Style、Preset 或 Style Strategy 时使用。

### 输出

```yaml
candidates:
  - style: IL03
    score: 0.92
  - style: CI08
    score: 0.84

selected:
  style: IL03
  confidence: 0.92

reason:
  - conceptual explanation
  - symbolic representation
  - adult knowledge content
```

## 5.3 `visual-style-library`

### 触发条件

需要读取、解释、比较或使用标准视觉风格定义时使用。

### 责任

- Style Spec；
- Style DNA；
- Style Fingerprint；
- Style inheritance；
- Confusion Matrix；
- Canonical Anchors；
- Constraints。

### 不负责

生成最终 Prompt。

## 5.4 `visual-identity-manager`

### 触发条件

一个项目需要多张图片、多页面或多场景保持统一视觉语言时使用。

### 负责

- Primary Style；
- Secondary Style white list；
- Palette Lock；
- Texture Lock；
- Mood Range；
- Era Lock；
- ReferenceSet；
- 允许变化范围。

## 5.5 `image-prompt-compiler`

### 触发条件

已有 Visual Spec，需要转换为可发送到某生图模型的 Prompt 时使用。

### 负责

```text
Visual Spec
→ Prompt AST
→ Locked Blocks
→ Model-independent Canonical Prompt
```

## 5.6 `image-model-adapter`

建议按模型拆为 Adapter reference/skill：

- seedream-adapter
- gpt-image-adapter
- flux-adapter
- midjourney-adapter
- sdxl-adapter

### 责任

只做：

> Canonical Visual Spec → 模型最容易理解的表达方式。

不能改变 Style 的核心定义。

## 5.7 `style-reference-manager`

负责：

- Style canonical references；
- project references；
- line references；
- palette references；
- texture references；
- composition references。

## 5.8 `image-style-evaluator`

### 输出

```yaml
style_score: 86

dimensions:
  shape: 91
  line: 88
  color: 82
  shading: 90
  lighting: 83
  texture: 79
  composition: 84
  detail: 87

decision: PASS
```

---

# 6. Skill 协作流程

## 6.1 自动风格模式

```text
User Content
   ↓
visual-intent-analyzer
   ↓
visual-style-selector
   ↓
visual-style-library
   ↓
visual-identity-manager
   ↓
image-prompt-compiler
   ↓
model-adapter
   ↓
generator
   ↓
image-style-evaluator
```

## 6.2 用户指定 Style

```text
User specifies VE01
   ↓
visual-style-library
   ↓
Visual Identity
   ↓
Prompt Compiler
   ↓
Adapter
```

此时 `visual-style-selector` 可以跳过。

## 6.3 用户提供参考图

```text
Reference Image
   ↓
Reference Analyzer
   ↓
Extract visual characteristics
   ↓
Match known Style / Custom Style
   ↓
Project Visual Identity
```

---

# 7. Style Schema

建议所有 Style 使用统一 YAML Schema。

```yaml
id: VE01
version: 1.0.0

name:
  zh: 极简矢量插画
  en: Minimal Vector Illustration

category:
  id: vector
  name_zh: 矢量艺术

parent_style: VECTOR_BASE

aliases:
  - minimalist vector illustration
  - clean vector art

definition:
  summary: ""
  detailed: ""

visual_intent:
  - clean
  - modern
  - simplified

fingerprint:
  shape: []
  line: []
  color: []
  shading: []
  lighting: []
  texture: []
  composition: []
  detail: []

style_dna:
  realism: 0
  abstraction: 0
  detail_density: 0
  spatial_depth: 0
  texture_strength: 0
  shading_strength: 0
  lighting_complexity: 0
  line_presence: 0
  line_roughness: 0
  shape_complexity: 0
  color_complexity: 0

shape_language:
  description: ""
  preferred: []
  avoid: []

line_language:
  description: ""
  preferred: []
  avoid: []

color_system:
  strategy: ""
  recommended_palette_types: []
  saturation_range: [0, 10]
  contrast_range: [0, 10]
  recommended_color_count: [0, 0]
  avoid: []

shading:
  method: []
  strength: 0
  avoid: []

lighting:
  physical_realism: 0
  methods: []
  avoid: []

texture:
  default: []
  strength: 0
  avoid: []

material:
  rendering_policy: ""
  preferred: []
  avoid: []

composition:
  preferred: []
  negative_space_range: ""
  layer_count: ""
  avoid: []

spatial_system:
  depth: 0
  perspective: []
  avoid: []

detail_density:
  level: 0
  focal_detail_policy: ""

character_rendering:
  face: ""
  skin: ""
  hair: ""
  anatomy: ""
  clothing: ""

background:
  complexity: 0
  preferred: []
  avoid: []

rules:
  must: []
  should: []
  may: []
  must_not: []

allowed_variations: []
forbidden_features: []

canonical_prompt:
  positive_anchor: []
  negative_anchor: []

confusion_with: []
correction_rules: []

use_cases:
  recommended: []
  discouraged: []

compatibility:
  portrait: 0
  landscape: 0
  product: 0
  poster: 0
  education: 0
  book_video: 0

reference_policy:
  minimum_reference_count: 3
  reference_types:
    - portrait
    - still_life
    - environment

evaluation_profile: VE01_DEFAULT
```

---

# 8. 每个 Style 的最低文档规格

| 模块 | 最低要求 |
|---|---|
| Summary | 100–200 字 |
| Detailed Definition | 300–800 字 |
| Fingerprint | 8 维完整 |
| DNA | 10+ 个数值 |
| MUST | ≥5 条 |
| SHOULD | ≥5 条 |
| MAY | ≥3 条 |
| MUST NOT | ≥8 条 |
| Canonical Positive Anchor | 50–150 词 |
| Negative Anchor | 30–100 词 |
| Confusion Styles | ≥2 |
| Correction Rules | ≥5 |
| Test Prompts | ≥5 |
| Reference Images | ≥3 |

建议生产级 Style 总资料量：**1500–3000 字 / Style**。

---

# 9. Style 规范示例：VE01

## 9.1 基本定义

**ID:** VE01  
**Name:** Minimal Vector Illustration / 极简矢量插画

一种以二维平面图形为主要表达方式的视觉风格。主体通过少量经过高度概括的几何形或有机形构成，不追求真实材质、真实光学或精细解剖，而强调轮廓识别、色彩关系、视觉节奏与留白。

## 9.2 Fingerprint

### Shape

- 简化 silhouette；
- 大面积有机色块；
- 圆、椭圆、圆角矩形、自由曲面；
- 低几何复杂度。

### Line

- 平滑；
- 连续；
- 少量；
- 线宽统一或最多两级。

### Color

- 3–7 个主要颜色；
- 色块边界清晰；
- 大面积纯色；
- 允许轻微渐变。

### Shading

- Flat；
- 0–15% 阴影强度；
- 不表现复杂体积光。

### Lighting

- 不强调真实物理光源；
- 可以通过浅色/深色区分层级。

### Texture

- 默认无纹理；
- 允许极轻微全局 Grain。

### Composition

- 30–60% 留白；
- 单一视觉中心；
- 2–4 个空间层级。

### Detail

- 2/10。

## 9.3 MUST

- 保持二维平面视觉；
- 使用简化形状；
- 使用清晰色块；
- 保持低细节密度；
- 保持平滑轮廓；
- 物体缩小后 silhouette 仍清晰。

## 9.4 MUST NOT

- 真实皮肤毛孔；
- 摄影景深；
- PBR 材质；
- 强烈体积光；
- 油画笔触；
- 水彩渗色；
- 高密度交叉排线；
- 复杂真实反射；
- 真实毛发细节。

## 9.5 Canonical Positive Anchor

```text
minimal vector illustration,
clean flat 2D visual language,
large simplified organic and geometric shapes,
smooth crisp contours,
limited controlled color palette,
clear color separation,
minimal shading,
low visual complexity,
simple recognizable silhouettes,
generous negative space,
balanced contemporary editorial composition
```

## 9.6 Negative Anchor

```text
photorealistic,
realistic skin pores,
photographic depth of field,
3D rendering,
PBR materials,
complex realistic reflections,
volumetric cinematic lighting,
oil painting brush strokes,
watercolor bleeding,
rough pencil shading,
dense visual details
```

---

# 10. Style 规范示例：DR07

## Vintage Loose Ink Sketch / 复古松弛墨线速写

核心特征不是“线稿”，而是：

> 手绘的不完美、断续线条、重复笔迹、线宽变化、纸张质感和复古编辑构图。

### MUST

- 非完全闭合轮廓；
- 允许重复描线；
- 允许局部 construction lines；
- 线条粗细自然变化；
- 背景使用暖米白/象牙纸；
- 黑灰占主要视觉比例；
- 辅色低饱和。

### MUST NOT

- 完美 Bézier 曲线；
- UI icon 式等宽线；
- 纯白数字画布；
- 大面积 Candy Color；
- 摄影光照；
- 真实 PBR 材质；
- 数字柔光渐变。

### Canonical Anchor

```text
vintage loose ink sketch illustration,
naturally imperfect hand-drawn lines,
broken and overlapping contours,
variable ink line weight,
spontaneous rough sketch character,
loose hatching and scribbled shading,
warm ivory textured paper,
restrained monochrome palette,
very subtle muted accent color,
refined vintage editorial composition,
large breathing space
```

---

# 11. Attribute Library

建议建立至少 10 个属性域：

```text
attributes/
├── palette/
├── lighting/
├── composition/
├── camera/
├── texture/
├── material/
├── line/
├── shape/
├── mood/
└── era/
```

---

# 12. Palette 设计

每个 Palette 需要定义：

```yaml
id: PAL_CANDY_BRIGHT

name:
  zh: 明亮糖果色

saturation: 7
brightness: 8
contrast: 5

color_tendency:
  - coral pink
  - lemon yellow
  - mint green
  - sky blue
  - lavender

rules:
  must:
    - clean color relationships
  avoid:
    - muddy brown
    - dirty gray
    - excessive black

prompt_anchor:
  - bright candy color palette
  - clean playful colors
```

建议首批 Palette：

1. Natural
2. Pastel
3. Candy
4. Morandi
5. Earth Tone
6. Monochrome
7. Black & White
8. Muted
9. High Saturation
10. Low Saturation
11. Warm
12. Cool
13. Teal & Orange
14. Vintage Faded
15. Cream
16. Macaron
17. Neon
18. Dark
19. Black Gold
20. Traditional Chinese
21. Nordic
22. Sage Green
23. Dusty Blue
24. Terracotta
25. Ivory Charcoal

---

# 13. Lighting Library

建议至少：

- Natural Light
- Soft Diffused Light
- Window Light
- Golden Hour
- Blue Hour
- Backlight
- Rim Light
- Side Light
- Top Light
- Studio Light
- High Key
- Low Key
- Cinematic Motivated Light
- Dramatic Light
- Volumetric Light
- God Rays
- Neon Light
- Overcast Light
- Candle Light
- Moonlight
- Flat Graphic Light
- Ambient Soft Light

每项必须描述：

- light source；
- hardness；
- direction；
- shadow behavior；
- contrast；
- allowed Style 范围；
- incompatible Style。

---

# 14. Composition Library

建议：

- Centered
- Symmetrical
- Rule of Thirds
- Golden Ratio
- Diagonal
- Leading Lines
- Frame within Frame
- Negative Space
- Close-up
- Medium Shot
- Wide Shot
- Extreme Wide
- Bird's-eye View
- Top-down
- Low Angle
- High Angle
- Dutch Angle
- Isometric
- Editorial Layout
- Poster Layout
- Layered Depth
- Minimal Composition
- Hero Composition
- Split Composition
- Radial Composition
- Grid Composition

---

# 15. Texture Library

建议：

- Clean Vector
- Paper Texture
- Fine Grain
- Film Grain
- Canvas
- Watercolor Paper
- Rough Paper
- Ink Bleed
- Halftone
- Noise
- Matte
- Glossy
- Brushed Metal
- Glass
- Ceramic
- Clay
- Fabric
- Wood
- Stone
- Concrete
- Plastic
- Translucent
- Holographic
- Aged Print
- Risograph Grain

---

# 16. Mood Library

建议：

- Calm
- Healing
- Warm
- Romantic
- Poetic
- Dreamy
- Mysterious
- Dark
- Lonely
- Melancholic
- Hopeful
- Joyful
- Playful
- Energetic
- Epic
- Majestic
- Serious
- Intellectual
- Elegant
- Luxury
- Minimal
- Futuristic
- Nostalgic
- Sacred
- Tense
- Introspective
- Documentary
- Youthful
- Whimsical
- Meditative

---

# 17. Style 继承体系

Style 不应全部平铺。

示例：

```text
VECTOR_BASE
├── VE01 Minimal Vector
├── VE02 Flat Vector
├── VE03 Editorial Vector
├── VE04 Geometric Vector
├── VE05 Organic Vector
├── VE06 Candy Vector
├── VE07 Gradient Vector
├── VE08 Monoline
├── VE09 Continuous Line
├── VE10 Abstract Vector
├── VE11 Corporate Vector
└── VE12 UI Illustration
```

`VECTOR_BASE` 规定：

```yaml
dimensionality: 2D
edge_policy: clean
realistic_material: false
pbr: false
photographic_depth_of_field: false
```

子 Style 只描述差异。

---

# 18. Style 分类体系

总体建议：**16 个一级分类，约 212 个 Style。**

---

# 19. 一级分类与 Style Catalog

## 19.1 Photography — 16

- PH01 Natural Photography
- PH02 Hyperreal Photography
- PH03 Portrait Photography
- PH04 Environmental Portrait
- PH05 Fashion Photography
- PH06 Beauty Photography
- PH07 Commercial Photography
- PH08 Product Photography
- PH09 Still Life Photography
- PH10 Food Photography
- PH11 Street Photography
- PH12 Documentary Photography
- PH13 Architectural Photography
- PH14 Landscape Photography
- PH15 Macro Photography
- PH16 Analog Film Photography

## 19.2 Cinematic — 12

- CI01 Cinematic Film Still
- CI02 Hollywood Cinema
- CI03 Indie Film
- CI04 Film Noir
- CI05 Neo-Noir
- CI06 Epic Cinematic
- CI07 Sci-Fi Cinema
- CI08 Historical Cinema
- CI09 Romantic Cinema
- CI10 Thriller Cinema
- CI11 Documentary Cinema
- CI12 Retro Cinema

## 19.3 Anime / Manga — 14

- AN01 Japanese Anime
- AN02 Cel Shading Anime
- AN03 Anime Film Visual
- AN04 Youth Anime
- AN05 Shonen Manga
- AN06 Shojo Manga
- AN07 Seinen Manga
- AN08 Slice-of-Life Anime
- AN09 Fantasy Anime
- AN10 Sci-Fi Anime
- AN11 1980s Retro Anime
- AN12 1990s Anime
- AN13 Chibi
- AN14 Semi-realistic Anime

> 具体在世艺术家或工作室名称不作为 Canonical Style ID；使用可解释的视觉特征定义替代。

## 19.4 Illustration — 16

- IL01 Flat Illustration
- IL02 Editorial Illustration
- IL03 Conceptual Illustration
- IL04 Narrative Illustration
- IL05 Metaphorical Illustration
- IL06 Minimal Illustration
- IL07 Grain Illustration
- IL08 Commercial Illustration
- IL09 Lifestyle Illustration
- IL10 Fashion Illustration
- IL11 Book Illustration
- IL12 Children's Illustration
- IL13 Scientific Illustration
- IL14 Botanical Illustration
- IL15 Medical Illustration
- IL16 Educational Illustration

## 19.5 Vector — 12

- VE01 Minimal Vector
- VE02 Flat Vector
- VE03 Editorial Vector
- VE04 Geometric Vector
- VE05 Organic Vector
- VE06 Candy Vector
- VE07 Soft Gradient Vector
- VE08 Monoline
- VE09 Continuous Line
- VE10 Abstract Vector
- VE11 Corporate Vector
- VE12 UI Illustration

## 19.6 Painting — 16

- PA01 Classical Oil Painting
- PA02 Realistic Oil Painting
- PA03 Impressionism
- PA04 Post-Impressionism
- PA05 Expressionism
- PA06 Modern Oil Painting
- PA07 Impasto
- PA08 Traditional Watercolor
- PA09 Soft Watercolor
- PA10 Gouache
- PA11 Acrylic Painting
- PA12 Pastel Painting
- PA13 Tempera
- PA14 Fresco
- PA15 Digital Painting
- PA16 Painterly Digital Art

## 19.7 Drawing — 12

- DR01 Pencil Drawing
- DR02 Charcoal Drawing
- DR03 Pen Line Drawing
- DR04 Ink Line Drawing
- DR05 Architectural Line Drawing
- DR06 Quick Gesture Sketch
- DR07 Vintage Loose Ink Sketch
- DR08 Minimal Line Art
- DR09 Continuous Line Drawing
- DR10 Vintage Etching Drawing
- DR11 Scientific Plate Drawing
- DR12 Product Design Sketch

## 19.8 Eastern Art — 14

- EA01 Chinese Ink Wash
- EA02 Freehand Landscape
- EA03 Gongbi
- EA04 Blue-Green Landscape
- EA05 Fine Outline / Bai Miao
- EA06 Song Dynasty Aesthetic
- EA07 Dunhuang Mineral Color
- EA08 Tang Mural
- EA09 Chinese Woodblock New Year Print
- EA10 Neo-Chinese
- EA11 Guochao
- EA12 Zen Eastern Minimalism
- EA13 Ukiyo-e
- EA14 Traditional Japanese Woodblock

## 19.9 Print Art — 10

- PR01 Woodcut
- PR02 Woodblock
- PR03 Engraving
- PR04 Etching
- PR05 Lithograph
- PR06 Screen Print
- PR07 Risograph
- PR08 Halftone Print
- PR09 Vintage Print
- PR10 Newspaper Illustration

## 19.10 3D / CGI — 16

- TD01 Photoreal CGI
- TD02 Product CGI
- TD03 Architectural CGI
- TD04 Cartoon 3D
- TD05 Soft 3D
- TD06 Clay 3D
- TD07 Plastic 3D
- TD08 Low Poly
- TD09 Voxel
- TD10 Isometric 3D
- TD11 Miniature
- TD12 Diorama
- TD13 Toy-like 3D
- TD14 Game Cinematic 3D
- TD15 Futuristic CGI
- TD16 Abstract 3D

## 19.11 Craft — 12

- CR01 Paper Cut
- CR02 Paper Craft
- CR03 Origami
- CR04 Handmade Clay
- CR05 Felt Art
- CR06 Knitted Art
- CR07 Embroidery
- CR08 Fabric Textile
- CR09 Ceramic Art
- CR10 Porcelain Art
- CR11 Mosaic
- CR12 Handmade Collage

## 19.12 Graphic Design — 16

- GD01 Swiss Design
- GD02 International Typographic Style
- GD03 Bauhaus
- GD04 Constructivism
- GD05 Art Deco
- GD06 Art Nouveau
- GD07 Mid-century Modern
- GD08 Memphis
- GD09 Brutalism
- GD10 Neo Brutalism
- GD11 Minimal Graphic Design
- GD12 Editorial Design
- GD13 Magazine Design
- GD14 Vintage Poster
- GD15 Modern Poster
- GD16 Geometric Graphic Design

## 19.13 Concept / Game Art — 12

- GA01 Environment Concept Art
- GA02 Character Concept Art
- GA03 Fantasy Concept Art
- GA04 Sci-Fi Concept Art
- GA05 Matte Painting
- GA06 Game Splash Art
- GA07 Card Illustration
- GA08 RPG Illustration
- GA09 Strategy Game Art
- GA10 AAA Game Visual
- GA11 Game Loading Screen
- GA12 Worldbuilding Art

## 19.14 Fantasy / Surreal — 16

- FA01 Fantasy
- FA02 High Fantasy
- FA03 Dark Fantasy
- FA04 Magical Realism
- FA05 Surrealism
- FA06 Dreamlike
- FA07 Dreamcore
- FA08 Weirdcore
- FA09 Liminal Space
- FA10 Symbolic Art
- FA11 Psychedelic
- FA12 Cyberpunk
- FA13 Steampunk
- FA14 Solarpunk
- FA15 Retrofuturism
- FA16 Biopunk

## 19.15 Retro / Era — 14

- RT01 Victorian
- RT02 1920s
- RT03 1930s
- RT04 1940s
- RT05 1950s
- RT06 1960s
- RT07 1970s
- RT08 1980s
- RT09 1990s
- RT10 Y2K
- RT11 Old Shanghai
- RT12 Hong Kong Retro
- RT13 Showa Japan
- RT14 Soviet Retro

> 在实现中，Retro 同时也可以作为 Era Attribute；当年代视觉本身成为画面主语言时才作为主 Style 使用。

## 19.16 Information / Scientific — 14

- IN01 Infographic
- IN02 Scientific Illustration
- IN03 Educational Illustration
- IN04 Technical Diagram
- IN05 Blueprint
- IN06 Exploded View
- IN07 Cutaway Illustration
- IN08 Anatomical Illustration
- IN09 Botanical Plate
- IN10 Map Illustration
- IN11 Timeline Visual
- IN12 Process Illustration
- IN13 Isometric Infographic
- IN14 Data Illustration

---

# 20. Style 数量治理

禁止因为以下属性不同就创建新 Style：

- 柔和；
- 高饱和；
- 暗色；
- 明亮；
- 黄金时刻；
- 低角度；
- 米黄色；
- 糖果色；
- 电影光；
- 16:9；
- 复古纸张。

这些应成为 Attribute。

新增 Style 前必须检查：

```text
1. 是否存在新的 Shape Language？
2. 是否存在新的 Rendering Method？
3. 是否存在新的 Line Language？
4. 是否存在新的 Material/Pigment behavior？
5. 与已有 Style 的 Style DNA 距离是否足够？
6. 是否仅仅是 Palette / Lighting / Era 差异？
```

如果主要差异来自 Attribute，则不新增 Style。

---

# 21. Confusion Matrix

每个 Style 必须定义最容易混淆的 Style。

```yaml
style: VE01

confusion_with:
  - style: IL01
    risk: high
    difference:
      - VE01 更依赖干净几何轮廓
      - IL01 允许更复杂叙事细节
    correction:
      - simplify shapes
      - reduce texture
      - strengthen crisp vector edges

  - style: DR08
    risk: medium
    difference:
      - VE01 依赖色块
      - DR08 依赖线条
```

---

# 22. Style Selector

Style Selector 不应仅由 LLM 直觉决定。

建议采用：**LLM 提取语义 + 可解释评分**。

## 22.1 输入维度

- Domain
- Content Type
- Visual Role
- Narrative Mode
- Information Density
- Audience
- Emotion
- Abstraction Need
- Realism Need
- Project Identity
- Medium
- Aspect Ratio

## 22.2 评分

```text
Score =
ContentMatch      × 0.25
VisualRoleMatch   × 0.20
NarrativeMatch    × 0.15
MoodMatch         × 0.10
AudienceMatch     × 0.08
MediumMatch       × 0.07
IdentityMatch     × 0.10
ConsistencyRisk   × 0.05
```

权重允许由 Strategy 覆盖。

---

# 23. Style Strategy

不同内容域需要策略层：

```text
strategies/
├── book/
├── video/
├── education/
├── poster/
├── product/
├── social/
└── branding/
```

## 23.1 历史

```yaml
primary:
  - CI08
  - IL03
  - IL04

secondary:
  - PR03
  - PR04
  - PA01

information:
  - IN10
  - IN11

avoid:
  - VE06
  - TD06
```

## 23.2 心理学

```yaml
primary:
  - IL03
  - IL05
  - FA05

secondary:
  - VE03
  - IL06

preferred_mood:
  - introspective
  - intellectual
```

## 23.3 商业管理

```yaml
primary:
  - IL02
  - VE01
  - VE11

secondary:
  - TD02
  - IL03

avoid:
  - excessive_fantasy
  - high_texture_painting
```

## 23.4 文学

```yaml
primary:
  - IL04
  - CI01
  - PA08

secondary:
  - PA01
  - FA05
  - PR04

mood_weight: high
```

---

# 24. Project Visual Identity

一旦项目需要多图，应创建 Visual Identity。

```yaml
project_id: book_sapiens_001

primary_style:
  id: IL03
  version: 1.2.0

secondary_styles:
  - CI08
  - PR04

palette:
  id: PAL_MUTED_EARTH

texture:
  id: TEX_FINE_GRAIN

mood:
  base:
    - intellectual
    - reflective

contrast:
  min: 3
  max: 6

style_lock:
  shape: high
  line: high
  palette: medium
  texture: high
  composition: medium

references:
  project:
    - REF_PROJECT_01
    - REF_PROJECT_02
```

---

# 25. Prompt AST

不建议 Prompt Compiler 直接拼字符串。

建议先生成中间 AST：

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
  mood:
    - lonely
    - introspective

locks:
  style: true
  palette: true

negative:
  inherit_style_negative: true
```

再由 Adapter 编译。

---

# 26. Prompt 固定结构

```text
[SUBJECT]
[SCENE]
[STYLE LOCK]
[VISUAL ATTRIBUTES]
[COMPOSITION]
[RENDERING REQUIREMENTS]
[NEGATIVE STYLE LOCK]
```

其中：

### 可变

- Subject
- Scene
- Action

### 半锁定

- Palette
- Lighting
- Composition
- Mood

### 强锁定

- Shape Language
- Line Language
- Rendering Method
- Shading
- Texture Policy
- Style Negative

---

# 27. Style Lock

```yaml
style_lock:

  immutable:
    - rendering_method
    - shape_language
    - line_language
    - shading_policy
    - texture_policy

  controlled:
    - palette
    - lighting
    - composition
    - mood

  free:
    - subject
    - object
    - environment
    - action
```

Prompt Compiler 禁止自动改写 immutable 区域的语义。

---

# 28. Model Adapter 架构

```text
Canonical Spec
      ↓
Prompt AST
      ↓
┌───────────────┐
│ Adapter       │
├───────────────┤
│ Seedream      │
│ GPT Image     │
│ Flux          │
│ Midjourney    │
│ SDXL          │
└───────────────┘
```

---

# 29. Adapter Profile

```yaml
model_family: seedream

prompt_behavior:
  natural_language: strong
  keyword_density: medium
  long_prompt_tolerance: high

capabilities:
  reference_image: true
  multiple_reference_images: true
  typography: medium
  negative_prompt: medium
  image_editing: true

compiler:
  sentence_style: descriptive
  preserve_canonical_anchor: semantic
```

---

# 30. Adapter 设计原则

Adapter 允许：

- 改变句式；
- 改变关键词排序；
- 将英文关键词转成自然语言；
- 根据模型删减无效词；
- 添加模型特有参数。

Adapter 不允许：

- 修改 Style DNA；
- 删除 MUST；
- 引入 MUST NOT 特征；
- 将 Style A 翻译为 Style B。

---

# 31. Reference System

## 31.1 每个核心 Style 最低参考图

- portrait；
- still-life；
- environment。

推荐增加：

- architecture；
- complex-scene；
- abstract。

## 31.2 参考图角色

```yaml
references:
  overall_style: []
  line: []
  palette: []
  texture: []
  composition: []
  character: []
```

## 31.3 Reference 元数据

```yaml
id:
source:
license:
style_id:
style_version:
role:
approved:
created_at:
```

---

# 32. Style Evaluator

Evaluator 不只做“像不像”，而是做维度级评分。

```text
Shape        20%
Line         15%
Color        15%
Shading      10%
Lighting     10%
Texture      10%
Composition  10%
Detail       10%
```

不同 Style 可以覆盖权重，例如 DR07 可以提高 Line / Texture 权重。

---

# 33. 判定规则

建议：

```text
85–100  Strong Pass
80–84   Pass
65–79   Correction
0–64    Regenerate
```

项目级连续生成还需要额外计算：

`Project Identity Consistency Score`

---

# 34. Correction Engine

Evaluator 输出：

```yaml
problems:
  - dimension: texture
    expected: 1
    actual: 7
    severity: high
```

Correction Engine 查找 Style correction rules：

```yaml
texture_too_realistic:
  instructions:
    - eliminate realistic material microtexture
    - return to flat color regions
    - remove photographic surface reflections
```

再进入 Compiler。

---

# 35. Style Benchmark

每个 Style 必须至少跑以下测试：

1. Portrait
2. Still Life
3. Architecture / Environment
4. Nature
5. Complex Multi-object Scene

不能只测人物，因为某些 Style 生人物正常，生建筑可能变成 3D，生复杂场景又可能漂到摄影。

---

# 36. Cross-model Benchmark

核心 40 Style 建议至少测试：

- Seedream；
- GPT Image；
- Flux；
- Midjourney。

示例：

| Style | Seedream | GPT Image | Flux | MJ | Cross-model |
|---|---:|---:|---:|---:|---:|
| VE01 | 91 | 89 | 85 | 87 | 88 |
| DR07 | 90 | 88 | 86 | 84 | 87 |

低于阈值优先调整 Adapter，不先修改 Canonical Style。

---

# 37. Skill 测试方法

Skill 本身也必须测试。

采用：

```text
Baseline
→ Skill
→ Regression
```

## 37.1 Baseline

不给 Skill 时，让 Agent 处理典型任务，记录错误：

- 只输出一个风格词；
- 混淆 Style / Palette；
- 把年代当 Style；
- 修改 Style Lock；
- 忽略 MUST NOT；
- 直接复制一个 Prompt 给所有模型。

## 37.2 Skill Test

加载 Skill 后重跑同一场景，验收 Agent 是否：

- 正确识别触发条件；
- 使用 Style Library；
- 输出结构化 Visual Spec；
- 不越权；
- 按协作链调用后续模块。

## 37.3 Pressure Cases

必须测试：

- 用户明确要求错误分类；
- 用户只说“高级一点”；
- 用户同时给多个冲突 Style；
- 项目已有 Visual Identity；
- 用户要求随机改变画风；
- Model Adapter 不支持某特性；
- 用户提供参考图但未指定 Style；
- 当前 Style 与页面语义冲突。

---

# 38. Skill 文件规范

建议：

```text
skills/
└── visual-style-selector/
    ├── SKILL.md
    ├── references/
    ├── schemas/
    └── tests/
```

`SKILL.md` 只放：

- 使用条件；
- 核心原则；
- 决策流程；
- 关键约束；
- 快速参考。

大量 Style 定义不得全部塞进 `SKILL.md`，应拆入 reference 文件。

---

# 39. Skill Frontmatter

示例：

```yaml
---
name: visual-style-selector
description: Use when an image, illustration, video frame, poster, or visual content task requires choosing a consistent visual style from subject matter, audience, mood, content role, or an existing project visual identity.
---
```

Description 只写：什么时候应该加载这个 Skill。不要在 Description 中完整描述工作流程。

---

# 40. Skill 触发边界

## visual-intent-analyzer

触发：

- 用户给内容，希望设计画面；
- 需要判断视觉角色。

不触发：

- 用户已经明确给 Visual Intent 数据。

## visual-style-selector

触发：

- `style=auto`；
- 用户问“适合什么画风”。

不触发：

- 已给明确 Style ID 且无需推荐。

## image-prompt-compiler

触发：

- 已有 Style/Visual Spec，需要模型 Prompt。

不触发：

- 用户只在讨论风格理论。

## evaluator

触发：

- 已经有生成结果；
- 需要一致性 QA。

---

# 41. Skill 间统一协议

建议所有 Skill 使用同一 Envelope：

```yaml
visual_request:
  request_id:
  project_id:
  usage:
  model:
  aspect_ratio:

  content: {}
  visual_intent: {}
  style: {}
  attributes: {}
  identity: {}
  references: []
  generation: {}
  evaluation: {}
```

各 Skill 只能修改自己负责的节点。

---

# 42. 工程目录结构

```text
visual-style-engine/
│
├── README.md
├── SKILL-SYSTEM.md
│
├── schemas/
│   ├── visual-request.schema.yaml
│   ├── style.schema.yaml
│   ├── attribute.schema.yaml
│   ├── preset.schema.yaml
│   ├── identity.schema.yaml
│   ├── reference.schema.yaml
│   └── evaluation.schema.yaml
│
├── skills/
│   ├── visual-intent-analyzer/
│   ├── visual-style-selector/
│   ├── visual-style-library/
│   ├── visual-identity-manager/
│   ├── image-prompt-compiler/
│   ├── image-model-adapter/
│   ├── style-reference-manager/
│   └── image-style-evaluator/
│
├── style-library/
│   ├── base/
│   ├── photography/
│   ├── cinematic/
│   ├── anime/
│   ├── illustration/
│   ├── vector/
│   ├── painting/
│   ├── drawing/
│   ├── eastern-art/
│   ├── print/
│   ├── 3d/
│   ├── craft/
│   ├── graphic-design/
│   ├── concept-art/
│   ├── fantasy/
│   ├── retro/
│   └── information/
│
├── attributes/
│   ├── palette/
│   ├── lighting/
│   ├── composition/
│   ├── camera/
│   ├── texture/
│   ├── material/
│   ├── line/
│   ├── shape/
│   ├── mood/
│   └── era/
│
├── presets/
│
├── strategies/
│   ├── book/
│   ├── video/
│   ├── poster/
│   ├── education/
│   ├── social/
│   ├── branding/
│   └── product/
│
├── adapters/
│   ├── seedream/
│   ├── gpt-image/
│   ├── flux/
│   ├── midjourney/
│   └── sdxl/
│
├── references/
│   ├── styles/
│   └── projects/
│
├── evaluation/
│   ├── profiles/
│   ├── confusion-matrix/
│   ├── correction-rules/
│   └── benchmarks/
│
└── tests/
    ├── skill-tests/
    ├── style-tests/
    ├── adapter-tests/
    └── regression/
```

---

# 43. Style Versioning

采用 Semantic Version：

```text
VE01@1.0.0
```

### PATCH

- Prompt 词序微调；
- 小幅 Adapter 优化；
- 不改变视觉定义。

### MINOR

- 增加约束；
- 增加参考图；
- 优化 Fingerprint；
- 视觉范围不发生根本变化。

### MAJOR

- Style DNA 改变；
- 核心 Rendering Method 改变；
- 旧版本图片与新版本已明显不是同一视觉语言。

---

# 44. Project Reproducibility

项目必须保存：

```yaml
style:
  id: IL03
  version: 1.2.0

adapter:
  model: seedream
  version: 1.1.0

preset:
  id: PRESET_013
  version: 1.0.0

references:
  - ref_001

compiler:
  version: 1.3.2
```

避免 Style Library 更新后旧项目无法重现。

---

# 45. Cache

可以缓存：

- StyleSpec
- Style + Attribute resolved spec
- Canonical Prompt
- Adapter compiled prompt
- Reference feature / embedding

Cache Key：

```text
styleId
+
styleVersion
+
attributeHash
+
adapterVersion
```

---

# 46. 可观测性

每次生成建议记录：

```yaml
request_id:
project_id:
style_id:
style_version:
preset_id:
adapter:
compiled_prompt_hash:
reference_ids:
generation_model:
evaluation_score:
corrections:
retry_count:
```

后续可以分析：

- 哪些 Style 最稳定；
- 哪个模型最容易漂；
- 哪些负向约束有效；
- 哪些 Adapter 需要优化。

---

# 47. 风格质量指标

## SSR — Style Success Rate

```text
通过 Style QA 的生成次数 / 总生成次数
```

## CMCS — Cross Model Consistency Score

同一 Style 不同模型的一致性。

## PICS — Project Identity Consistency Score

同一项目多图一致性。

## FDR — First-pass Design Rate

第一次生成即可通过的比例。

## CRR — Correction Recovery Rate

进入自动纠偏后能够通过的比例。

---

# 48. Reference Quality 指标

每个 Style 的参考图应检查：

- 是否覆盖不同 Subject；
- 是否过度依赖某个具体内容；
- 是否包含错误 Style 特征；
- 色彩是否代表 Style 而非单一 Preset；
- 是否存在过强角色 Identity。

Style Reference 应参考“视觉语言”，而不是固定人物。

---

# 49. 图书精读视频集成

建议：

```text
Book Analysis
      ↓
Chapter / Page Semantic Unit
      ↓
Visual Intent
      ↓
Book Visual Identity
      ↓
Page Style Strategy
      ↓
Prompt Compiler
      ↓
Image Generation
```

一本书可以：

- 主 Style 统一；
- 场景 Style 有限变化；
- Palette 统一；
- Texture 统一；
- Mood 在指定范围内变化。

示例：

```yaml
primary_style: IL03
allowed_secondary:
  - CI08
  - PR04

palette_lock: PAL_MUTED_EARTH
texture_lock: TEX_FINE_GRAIN

style_distribution:
  IL03: 60%
  CI08: 25%
  PR04: 15%
```

---

# 50. 海报场景集成

海报与普通插画不同，应额外分析：

- typography area；
- title safe area；
- negative space；
- reading order；
- copy amount；
- foreground/background conflict。

Prompt 只负责生成视觉底图时，应明确：

```text
leave clean negative space for typography
```

大量文字建议后置排版。

---

# 51. 人物生成集成

人物项目额外增加：

```yaml
character_identity:
  face:
  hair:
  age_range:
  body:
  clothing:

style_identity:
  style:
  palette:
  rendering:
```

人物 Identity 与 Style Identity 必须分离。

否则：

- 换画风时可能改变人物身份；
- 换人物时可能导致风格漂移。

---

# 52. 用户自定义 Style

支持两种模式。

## 52.1 Derived Style

基于现有 Style：

```yaml
extends: DR07

overrides:
  accent_palette: dusty_blue
  texture_strength: 4
```

## 52.2 Custom Style

从参考图分析生成临时 Style Spec。

流程：

1. Extract；
2. Normalize；
3. Remove subject-specific features；
4. Generate Fingerprint；
5. Generate Rules；
6. Test；
7. Save。

---

# 53. 自定义 Style 不直接污染公共库

用户 Custom Style 默认：

```text
scope = project
```

经过人工确认和 Benchmark 后，才可以升级为：

```text
scope = library
```

---

# 54. Model Capability Fallback

如果某模型无法准确支持某属性：

```yaml
requested:
  complex_typography: true

adapter:
  support: weak
```

返回：

```yaml
fallback:
  image_without_text: true
  typography_postprocess: required
```

而不是让模型硬生成。

---

# 55. 冲突解决

例如：

```text
Style = Minimal Vector
User = realistic skin pores
```

冲突顺序：

```text
Safety / system constraints
>
Project Visual Identity
>
Explicit Style Lock
>
Explicit user scene requirements
>
Attributes
>
Model defaults
```

Selector / Compiler 应指出：

```yaml
conflict:
  type: style_violation
  feature: realistic skin pores
```

可选择：

- 保留 Style，移除冲突属性；
- 用户明确要求时切换 Style。

---

# 56. Prompt 长度治理

禁止为了“更稳定”不断堆叠同义词。

建议 Prompt 分：

### Core Anchor

不可省。

### Support Anchor

模型能力允许时使用。

### Scene Description

按任务变化。

### Negative Lock

只保留真正会导致风格漂移的核心负向约束。

---

# 57. Canonical Prompt 与 Adapter Prompt 分离

`styles/VE01.yaml` 只保存模型无关视觉语义。

`adapters/seedream/VE01.yaml` 保存针对模型的：

- phrasing；
- ordering；
- reference usage；
- generation parameters。

---

# 58. 推荐首批 40 个 Core Style

### Photography / Cinematic

1. PH01
2. PH03
3. PH08
4. PH12
5. PH16
6. CI01
7. CI04
8. CI08

### Illustration / Vector

9. IL01
10. IL02
11. IL03
12. IL04
13. IL05
14. IL06
15. IL07
16. VE01
17. VE03
18. VE05
19. VE06

### Painting / Drawing

20. PA01
21. PA03
22. PA08
23. PA10
24. PA15
25. DR01
26. DR04
27. DR07
28. DR08

### Eastern / Print

29. EA01
30. EA03
31. EA06
32. EA07
33. EA10
34. PR01
35. PR04
36. PR07

### 3D / Design / Fantasy

37. TD06
38. TD12
39. GD01
40. FA05

这 40 个足以覆盖大量实际应用。

---

# 59. 建设阶段

## Phase 0 — Specification Freeze

输出：

- taxonomy；
- naming；
- schema；
- directory；
- version rule；
- skill boundary。

验收：任何团队成员对 Style / Attribute / Preset / Identity 的含义理解一致。

## Phase 1 — Core Schema

完成：

- style.schema.yaml；
- attribute.schema.yaml；
- visual-request.schema.yaml；
- identity.schema.yaml；
- evaluation.schema.yaml。

## Phase 2 — Core 40 Style

每个 Style 完成：

- full spec；
- canonical prompt；
- negative；
- confusion；
- correction；
- 5 test prompts。

## Phase 3 — Attribute Library

完成：

- 25+ Palette；
- 20+ Lighting；
- 25+ Composition；
- 25+ Texture；
- 30+ Mood；
- Camera；
- Era；
- Material。

## Phase 4 — Selector

先采用：

> LLM Semantic Extraction + Rule Ranking。

不要一开始训练专用分类模型。

## Phase 5 — Prompt Compiler

实现：

```text
AST
+
Style Lock
+
Attribute merge
+
Conflict resolution
```

## Phase 6 — Seedream + GPT Image Adapter

第一批先做两个模型，验证跨模型架构。

## Phase 7 — Reference & Evaluator

建立：

- 3–6 canonical references / Core Style；
- five-scenario benchmark；
- scoring。

## Phase 8 — Flux / Midjourney Adapter

验证同一个 Canonical Style 可以适配不同 Prompt 习惯模型。

## Phase 9 — 100 Style

扩充常用风格。

## Phase 10 — 212 Style

完成完整库。

---

# 60. 验收标准

系统达到 v1 Production Ready，至少满足：

### Style

- Core 40 全部有完整 Visual Spec；
- 每个 Style 至少 5 类测试；
- 无明显重复 Style。

### Cross-model

- 两个主模型 CMCS ≥ 80；
- Core 20 ≥ 85。

### Project

- 20 张连续图片 PICS ≥ 85。

### Skill

- 所有主要 Skill 有 trigger tests；
- 无明显 Skill 抢任务；
- Style Selector 输出可解释原因。

### Versioning

- 所有生成记录可追溯到 Style + Adapter + Compiler 版本。

---

# 61. 端到端示例

用户：

> 为《人类简史》“农业革命”章节生成一张 16:9 配图，需要有历史感，但不是普通历史照片，希望表达“农业带来了稳定，也带来了新的束缚”。

## Step 1 Visual Intent

```yaml
domain: history
visual_role: conceptual_explanation
narrative_mode: metaphorical
mood:
  - reflective
  - slightly oppressive
realism_need: medium
```

## Step 2 Selector

```yaml
primary: IL03
secondary:
  - CI08
  - PR04

selected: IL03
score: 0.94
```

## Step 3 Attributes

```yaml
palette: PAL_MUTED_EARTH
texture: TEX_FINE_GRAIN
composition: CMP_SYMBOLIC_CENTER
mood:
  - reflective
  - restrained
```

## Step 4 Scene

```text
一片规则农田形成巨大的几何网格，
一名农民站在田间，
远处粮仓象征稳定，
但农田边界逐渐形成类似牢笼的视觉结构。
```

## Step 5 Style Lock

加载 IL03 的：

- Shape；
- Rendering；
- Detail；
- Negative；
- Composition behavior。

## Step 6 Adapter

根据 Seedream 或 GPT Image 编译不同 Prompt。

## Step 7 Evaluate

如果输出变成电影摄影：

```text
Style Drift:
IL03 → CI08
```

Evaluator 触发 correction：

```text
reduce photographic realism
restore conceptual editorial rendering
simplify physical lighting
strengthen symbolic illustration language
```

---

# 62. 对上层 Skill 的统一接口

上层只需要：

```yaml
request:
  usage: book_video
  content: "..."
  aspect_ratio: "16:9"
  model: seedream
  style: auto
  project_id: sapiens
```

返回：

```yaml
result:
  visual_intent: {}
  style: {}
  visual_spec: {}
  prompt: ""
  negative_prompt: ""
  references: []
  evaluation_profile: ""
```

上层不需要知道模型 Prompt 细节。

---

# 63. 数据、代码与 LLM 的职责划分

## 数据

YAML / JSON：

- Style；
- Attribute；
- Preset；
- Strategy；
- Adapter rule；
- Evaluation profile。

## 代码

负责：

- Load；
- Merge；
- Validate；
- Rank；
- Compile；
- Compare；
- Version；
- Cache。

## LLM

负责：

- 理解内容；
- 提取 Visual Intent；
- 解释语义；
- 生成 Subject Scene；
- 在规则范围内补全自然语言。

明确：

> 能机械验证的约束尽量交给代码，而不是仅靠 Skill 文档提醒。

---

# 64. Schema Validation

推荐加入自动检查：

```text
Style ID unique
Version valid
MUST >= 5
MUST_NOT >= 5
Fingerprint complete
DNA complete
Positive anchor not empty
Negative anchor not empty
Confusion rules present
Benchmark present
```

CI 中执行。

---

# 65. Style Lint

建议开发：

```text
style-lint
```

检查：

- Style 重复；
- Alias 冲突；
- 禁止属性互相矛盾；
- Canonical Anchor 中出现具体模型参数；
- MUST 和 MUST NOT 冲突；
- Style DNA 越界；
- Reference 缺失。

---

# 66. Adapter Lint

检查：

- 是否删除 MUST；
- 是否引入 MUST NOT；
- 是否改变 Style 定义；
- 是否使用已废弃模型参数；
- 是否缺失 Style Lock。

---

# 67. 回归测试

Style 更新之后自动重跑：

```text
Style Benchmark
Adapter Benchmark
Project Sample Benchmark
```

重点关注：Style 的“优化”不能让旧场景变差。

---

# 68. 人工评审机制

Evaluator 不能完全替代审美评审。

建议建立：

```text
Machine Score
+
Human Review
```

Core Style 发布前至少人工确认：

- 是否真正可辨识；
- 与相邻 Style 是否差异足够；
- Reference 是否代表风格；
- 是否存在明显 AI cliché；
- 是否过度约束导致内容表现能力下降。

---

# 69. Style 生命周期

```text
DRAFT
↓
SPEC_READY
↓
BENCHMARKING
↓
REVIEW
↓
ACTIVE
↓
DEPRECATED
↓
ARCHIVED
```

---

# 70. Style Registry

```yaml
styles:
  VE01:
    version: 1.2.0
    status: ACTIVE
    category: vector

  DR07:
    version: 1.1.0
    status: ACTIVE
```

Selector 只推荐 ACTIVE。

---

# 71. Skill Registry

```yaml
skills:
  visual-intent-analyzer:
    version: 1.0.0

  visual-style-selector:
    version: 1.0.0

  visual-style-library:
    version: 1.0.0

  visual-identity-manager:
    version: 1.0.0

  image-prompt-compiler:
    version: 1.0.0

  image-style-evaluator:
    version: 1.0.0
```

---

# 72. 后续扩展

未来可以增加：

## Style Search

自然语言搜索：

> “类似旧书版画但是更现代”

返回 Style + Attribute。

## Style Similarity

例如：

```text
PR04 Etching      0.91
DR10 Etching Line 0.86
PR03 Engraving    0.82
```

## Style Recommendation UI

提供：

- 风格预览；
- 色板；
- 人物样图；
- 场景样图；
- 相似风格对比。

## Style Learning

根据项目中人工批准的图片逐步优化：

- Project Reference；
- Adapter；
- Evaluation threshold。

不直接自动修改 Canonical Style。

---

# 73. 关键设计决策总结

1. **Style 与 Prompt 分离。**
2. **Style 与 Attribute 分离。**
3. **Canonical Visual Spec 与 Model Adapter 分离。**
4. **项目级 Visual Identity 独立存在。**
5. **Prompt 必须包含 Style Lock。**
6. **参考图是一致性的重要增强层。**
7. **生成之后必须有 Evaluator。**
8. **新增风格必须经过 Benchmark，而不是只添加一个名称。**
9. **Skill 使用测试驱动方式验证其是否真正改变 Agent 行为。**
10. **先建设 40 个高质量 Core Style，再扩展到 212。**

---

# 74. 最终系统形态

```text
                          AI VISUAL STYLE ENGINE

                             ┌──────────────┐
                             │   Content    │
                             └──────┬───────┘
                                    ↓
                         ┌────────────────────┐
                         │ Visual Intent      │
                         │ Analyzer           │
                         └─────────┬──────────┘
                                   ↓
                         ┌────────────────────┐
                         │ Style Selector     │
                         └─────────┬──────────┘
                                   ↓
              ┌────────────────────┴────────────────────┐
              ↓                                         ↓
     ┌──────────────────┐                    ┌───────────────────┐
     │ Style Library    │                    │ Project Identity  │
     └─────────┬────────┘                    └─────────┬─────────┘
               └────────────────────┬──────────────────┘
                                    ↓
                         ┌────────────────────┐
                         │ Visual Spec        │
                         └─────────┬──────────┘
                                   ↓
                         ┌────────────────────┐
                         │ Prompt Compiler    │
                         └─────────┬──────────┘
                                   ↓
                         ┌────────────────────┐
                         │ Model Adapter      │
                         └─────────┬──────────┘
                                   ↓
                         ┌────────────────────┐
                         │ Reference Manager  │
                         └─────────┬──────────┘
                                   ↓
                         ┌────────────────────┐
                         │ Image Generator    │
                         └─────────┬──────────┘
                                   ↓
                         ┌────────────────────┐
                         │ Style Evaluator    │
                         └──────┬───────┬─────┘
                                │       │
                              PASS   CORRECT
                                │       │
                                │       └──────→ Compiler
                                ↓
                         ┌────────────────────┐
                         │ Final Image        │
                         └────────────────────┘
```

---

# 75. 推荐下一步直接创建的内容

基于本设计文档，下一步应开始实际建立 Skill 体系。

推荐顺序：

```text
01  schemas/style.schema.yaml
02  schemas/visual-request.schema.yaml
03  schemas/attribute.schema.yaml
04  skills/visual-style-library/SKILL.md
05  skills/visual-intent-analyzer/SKILL.md
06  skills/visual-style-selector/SKILL.md
07  skills/image-prompt-compiler/SKILL.md
08  styles/base/*.yaml
09  Core Style VE01 / IL03 / DR07 / CI01 / PA08
10  attributes/palette/*
11  attributes/composition/*
12  adapters/seedream/*
13  adapters/gpt-image/*
14  evaluation profiles
15  baseline tests
16  benchmark tests
17  reference image generation
18  Core 40 Style
19  expand to 100
20  expand to 212
```

---

# 76. Definition of Done

整个 Skill 体系真正完成，不以“已经创建 SKILL.md”为标准，而以以下条件为准：

- Agent 知道什么时候应该调用哪个 Skill；
- Agent 不会把 Style 和 Palette 混为一谈；
- Agent 能根据内容选择合适 Style；
- 同一 Style 的视觉语言有明确、可执行定义；
- 模型差异由 Adapter 吸收；
- 项目多图有 Visual Identity；
- Prompt 中 Style Lock 不会被随意改写；
- 每个 Style 都有参考图；
- 每个 Style 都有 Benchmark；
- 每个 Skill 都有 baseline / regression test；
- 生成结果可以自动评分和纠偏；
- Style / Adapter / Prompt Compiler 都可版本追踪；
- 新增模型无需重做整个 Style Library；
- 新增 Style 不会导致风格库无限重复膨胀。

达到这些条件后，这套体系才可以称为：

> **生产级 AI Visual Style Skill System。**

---

# 附录 A：Style 文件模板

```yaml
id:
version:

name:
  zh:
  en:

category:
parent_style:
aliases: []

definition:
  summary:
  detailed:

visual_intent: []

fingerprint:
  shape: []
  line: []
  color: []
  shading: []
  lighting: []
  texture: []
  composition: []
  detail: []

style_dna:
  realism:
  abstraction:
  detail_density:
  spatial_depth:
  texture_strength:
  shading_strength:
  lighting_complexity:
  line_presence:
  line_roughness:
  shape_complexity:
  color_complexity:

shape_language: {}
line_language: {}
color_system: {}
shading: {}
lighting: {}
texture: {}
material: {}
composition: {}
spatial_system: {}
detail_density: {}
character_rendering: {}
background: {}

rules:
  must: []
  should: []
  may: []
  must_not: []

allowed_variations: []
forbidden_features: []

canonical_prompt:
  positive_anchor: []
  negative_anchor: []

confusion_with: []
correction_rules: []

use_cases:
  recommended: []
  discouraged: []

compatibility: {}
reference_policy: {}
evaluation_profile:
```

---

# 附录 B：Attribute 文件模板

```yaml
id:
version:

name:
  zh:
  en:

type:
description:

parameters: {}

compatible_styles: []
incompatible_styles: []

rules:
  must: []
  avoid: []

prompt_anchor:
  positive: []
  negative: []
```

---

# 附录 C：Model Adapter 文件模板

```yaml
model_family:
version:

capabilities: {}
prompt_behavior: {}

compile_rules:
  subject:
  scene:
  style:
  attributes:
  negative:
  reference:

fallback_rules: []
unsupported_features: []
style_overrides: {}
```

---

# 附录 D：Evaluation Profile 模板

```yaml
id:
style_id:
style_version:

weights:
  shape: 0.20
  line: 0.15
  color: 0.15
  shading: 0.10
  lighting: 0.10
  texture: 0.10
  composition: 0.10
  detail: 0.10

thresholds:
  strong_pass: 85
  pass: 80
  correction: 65

hard_fail:
  - violates_must_not
  - wrong_rendering_method

correction_map: {}
```

---

# 附录 E：Style Benchmark 模板

```yaml
style:
  id:
  version:

cases:
  portrait:
    subject:
    expected:

  still_life:
    subject:
    expected:

  environment:
    subject:
    expected:

  nature:
    subject:
    expected:

  complex_scene:
    subject:
    expected:

models:
  - seedream
  - gpt-image
  - flux
  - midjourney

acceptance:
  per_model_min_score: 80
  cross_model_min_score: 80
```

---

# 附录 F：项目 Visual Identity 模板

```yaml
project_id:
version:

primary_style:
  id:
  version:

secondary_styles: []

palette:
texture:
mood:
era:

composition_policy: {}

style_lock:
  shape:
  line:
  palette:
  lighting:
  texture:
  composition:

references: []
allowed_variations: []
forbidden_styles: []
```

---

# 结语

本方案的核心不是建立一个“拥有 212 个风格名称的 Prompt 库”，而是建立一套：

> **可定义、可解释、可组合、可继承、可适配、可评测、可纠偏、可版本化的视觉语言系统。**

当 Style 被设计成 Visual Spec，Prompt 被设计成编译结果，模型差异被 Model Adapter 吸收，项目一致性由 Visual Identity 管理，生成结果再经过 Evaluator 校验后，生图能力才从“随机试 Prompt”升级为可以工程化复用的视觉生成基础设施。

这也是后续创建完整 AI 生图 Skill 体系的设计基线。
