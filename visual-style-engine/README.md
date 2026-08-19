# AI Visual Style Engine

模型无关的 **AI 视觉风格引擎与 Skill 体系**。让生图从"随机试 Prompt"升级为可工程化复用的视觉生成基础设施：**可定义、可解释、可组合、可继承、可适配、可评测、可纠偏、可版本化**。

> 设计基线：`../design/AI_Visual_Style_Skill_System_Design.md`（v1.0，总体设计/可实施）

## 使用场景

本引擎服务于所有"需要按统一视觉语言批量生成图片"的上层应用：

| 场景 | 典型需求 | 推荐策略 | 主 Style 参考 |
|---|---|---|---|
| 图书精读视频 | 一本书每章/每页配图，全卷视觉统一 | `strategies/book/`、书视频 Identity（主 Style + 有限次级 + Palette/Texture 锁） | IL03 / CI08 / PR04 |
| 知识视频 / 课程 | 系列讲解插画、封面与内页一致 | `strategies/video/` | IL03 / IL01 / IN03 |
| 文章 / 编辑配图 | 一篇文章一张或多张概念插图 | 单图可跳过 Identity，直接 selector | IL03 / IL02 / IL05 |
| 海报 / 封面 | 视觉冲击 + 为标题留白 | `strategies/poster/`（typography area 分析，底图留白） | IL03 / GD01 / PR07 / CI01 |
| 社交媒体栏目 | 固定栏目画风，多期一致 | identity-manager + preset | VE01 / DR07 / IL06 |
| 产品 / 品牌视觉 | 产品展示、材质还原、背景纯净 | `strategies/product/` | PH08 / TD02 / VE01 |
| 教育内容 | 信息清晰、去干扰、按学龄分层 | `strategies/education/` | IN03 / IL16 / TD06 |
| 历史 / 人文内容 | 时代质感、纪实氛围 | `strategies/` + CI08 / EA01 / DR07 | CI08 / EA01 / PH12 |

> 判断标准：需要 1 张图 → 直接选 Style 出图；需要 N 张图且要保持统一 → 先建 Visual Identity。

## 风格列表（支持哪些风格形式）

引擎内置 **16 个一级风格形式（分类）**，共登记 **222** 个具体风格。

- ✅ **ACTIVE（已就绪/可即用）**：已建立完整 YAML 规格定义，可直接在 `style=` 中指定或经 selector 推荐。
- 🚧 **DRAFT（已登记/规划中）**：已列入目录并命名，规格正在补全，暂由相近 ACTIVE 风格兜底。

### 风格形式总览（16 类）

| 分类 ID | 中文名 | 英文名 | 风格数 | 已就绪 |
|---|---|---|---|---|
| `photography` | 摄影 | Photography | 16 | 5 |
| `cinematic` | 电影感 | Cinematic | 12 | 3 |
| `anime` | 动漫 | Anime / Manga | 14 | 0 |
| `illustration` | 插画 | Illustration | 16 | 7 |
| `vector` | 矢量艺术 | Vector | 12 | 4 |
| `painting` | 绘画 | Painting | 16 | 5 |
| `drawing` | 素描线绘 | Drawing | 12 | 4 |
| `eastern-art` | 东方艺术 | Eastern Art | 14 | 5 |
| `print` | 印刷艺术 | Print Art | 10 | 3 |
| `3d` | 3D / CGI | 3D / CGI | 16 | 2 |
| `craft` | 手工艺 | Craft | 12 | 0 |
| `graphic-design` | 平面设计 | Graphic Design | 16 | 1 |
| `concept-art` | 概念与游戏美术 | Concept / Game Art | 12 | 0 |
| `fantasy` | 奇幻与超现实 | Fantasy / Surreal | 16 | 1 |
| `retro` | 复古年代 | Retro / Era | 14 | 0 |
| `information` | 信息与科学 | Information / Scientific | 14 | 0 |

### 完整风格清单

#### photography · 摄影（Photography）

| ID | 中文名 | 英文名 | 状态 | 简介 |
|---|---|---|---|---|
| `PH01` | 自然摄影 | Natural Photography | ✅ ACTIVE | 自然光、真实场景、无干预感的纪实美学 |
| `PH02` | 超写实摄影 | Hyperreal Photography | 🚧 DRAFT |  |
| `PH03` | 肖像摄影 | Portrait Photography | ✅ ACTIVE | 以人物为主体，关注表情神态与光线塑造 |
| `PH04` | 环境肖像 | Environmental Portrait | 🚧 DRAFT |  |
| `PH05` | 时尚摄影 | Fashion Photography | 🚧 DRAFT |  |
| `PH06` | 美妆摄影 | Beauty Photography | 🚧 DRAFT |  |
| `PH07` | 商业摄影 | Commercial Photography | 🚧 DRAFT |  |
| `PH08` | 产品摄影 | Product Photography | ✅ ACTIVE | 产品主体突出、布光精细、无干扰背景 |
| `PH09` | 静物摄影 | Still Life Photography | 🚧 DRAFT |  |
| `PH10` | 美食摄影 | Food Photography | 🚧 DRAFT |  |
| `PH11` | 街头摄影 | Street Photography | 🚧 DRAFT |  |
| `PH12` | 纪实摄影 | Documentary Photography | ✅ ACTIVE | 真实事件记录、客观克制、不摆拍 |
| `PH13` | 建筑摄影 | Architectural Photography | 🚧 DRAFT |  |
| `PH14` | 风景摄影 | Landscape Photography | 🚧 DRAFT |  |
| `PH15` | 微距摄影 | Macro Photography | 🚧 DRAFT |  |
| `PH16` | 模拟胶片摄影 | Analog Film Photography | ✅ ACTIVE | 胶片颗粒、色偏、宽容度的复古影像质感 |

#### cinematic · 电影感（Cinematic）

| ID | 中文名 | 英文名 | 状态 | 简介 |
|---|---|---|---|---|
| `CI01` | 电影剧照 | Cinematic Film Still | ✅ ACTIVE | 构图/布光/调色均按电影帧标准，叙事感强 |
| `CI02` | 好莱坞电影 | Hollywood Cinema | 🚧 DRAFT |  |
| `CI03` | 独立电影 | Indie Film | 🚧 DRAFT |  |
| `CI04` | 黑色电影 | Film Noir | ✅ ACTIVE | 高反差黑白或低饱和、硬光、阴影叙事 |
| `CI05` | 新黑色电影 | Neo-Noir | 🚧 DRAFT |  |
| `CI06` | 史诗电影 | Epic Cinematic | 🚧 DRAFT |  |
| `CI07` | 科幻电影 | Sci-Fi Cinema | 🚧 DRAFT |  |
| `CI08` | 历史电影 | Historical Cinema | ✅ ACTIVE | 时代质感、服饰器物考究、纪实电影光 |
| `CI09` | 浪漫电影 | Romantic Cinema | 🚧 DRAFT |  |
| `CI10` | 惊悚电影 | Thriller Cinema | 🚧 DRAFT |  |
| `CI11` | 纪录电影 | Documentary Cinema | 🚧 DRAFT |  |
| `CI12` | 复古电影 | Retro Cinema | 🚧 DRAFT |  |

#### anime · 动漫（Anime / Manga）

| ID | 中文名 | 英文名 | 状态 | 简介 |
|---|---|---|---|---|
| `AN01` | 日本动漫 | Japanese Anime | 🚧 DRAFT |  |
| `AN02` | 赛璐璐动漫 | Cel Shading Anime | 🚧 DRAFT |  |
| `AN03` | 动画电影视觉 | Anime Film Visual | 🚧 DRAFT |  |
| `AN04` | 青春动漫 | Youth Anime | 🚧 DRAFT |  |
| `AN05` | 少年漫画 | Shonen Manga | 🚧 DRAFT |  |
| `AN06` | 少女漫画 | Shojo Manga | 🚧 DRAFT |  |
| `AN07` | 青年漫画 | Seinen Manga | 🚧 DRAFT |  |
| `AN08` | 日常系动漫 | Slice-of-Life Anime | 🚧 DRAFT |  |
| `AN09` | 奇幻动漫 | Fantasy Anime | 🚧 DRAFT |  |
| `AN10` | 科幻动漫 | Sci-Fi Anime | 🚧 DRAFT |  |
| `AN11` | 80年代复古动漫 | 1980s Retro Anime | 🚧 DRAFT |  |
| `AN12` | 90年代动漫 | 1990s Anime | 🚧 DRAFT |  |
| `AN13` | 萌系 | Chibi | 🚧 DRAFT |  |
| `AN14` | 半写实动漫 | Semi-realistic Anime | 🚧 DRAFT |  |

#### illustration · 插画（Illustration）

| ID | 中文名 | 英文名 | 状态 | 简介 |
|---|---|---|---|---|
| `IL01` | 扁平插画 | Flat Illustration | ✅ ACTIVE | 纯色块、无渐变阴影、图形化叙事 |
| `IL02` | 编辑插画 | Editorial Illustration | ✅ ACTIVE | 为文章/报道服务的概念化插图，图文关系优先 |
| `IL03` | 概念插画 | Conceptual Illustration | ✅ ACTIVE | 以视觉传达抽象概念，象征与隐喻为主 |
| `IL04` | 叙事插画 | Narrative Illustration | ✅ ACTIVE | 讲述一个场景/故事，有时间与情节 |
| `IL05` | 隐喻插画 | Metaphorical Illustration | ✅ ACTIVE | 把抽象关系/观点具象成可读画面 |
| `IL06` | 极简插画 | Minimal Illustration | ✅ ACTIVE | 大量留白、少元素、强符号 |
| `IL07` | 颗粒插画 | Grain Illustration | ✅ ACTIVE | 色块 + 颗粒噪点纹理，杂志感 |
| `IL08` | 商业插画 | Commercial Illustration | 🚧 DRAFT |  |
| `IL09` | 生活方式插画 | Lifestyle Illustration | 🚧 DRAFT |  |
| `IL10` | 时尚插画 | Fashion Illustration | 🚧 DRAFT |  |
| `IL11` | 书籍插画 | Book Illustration | 🚧 DRAFT |  |
| `IL12` | 童书插画 | Children's Illustration | 🚧 DRAFT |  |
| `IL13` | 科学插画 | Scientific Illustration | 🚧 DRAFT |  |
| `IL14` | 植物插画 | Botanical Illustration | 🚧 DRAFT |  |
| `IL15` | 医学插画 | Medical Illustration | 🚧 DRAFT |  |
| `IL16` | 教育插画 | Educational Illustration | 🚧 DRAFT |  |

#### vector · 矢量艺术（Vector）

| ID | 中文名 | 英文名 | 状态 | 简介 |
|---|---|---|---|---|
| `VE01` | 极简矢量插画 | Minimal Vector Illustration | ✅ ACTIVE | 简化形状、清晰色块、留白、低细节 |
| `VE02` | 扁平矢量 | Flat Vector | 🚧 DRAFT |  |
| `VE03` | 编辑矢量 | Editorial Vector | ✅ ACTIVE | 杂志编辑式构图、图文节奏 |
| `VE04` | 几何矢量 | Geometric Vector | 🚧 DRAFT |  |
| `VE05` | 有机矢量 | Organic Vector | ✅ ACTIVE | 自由曲面、生物形态、柔润 |
| `VE06` | 糖果矢量 | Candy Vector | ✅ ACTIVE | 糖果色 + 圆润可爱 |
| `VE07` | 柔和渐变矢量 | Soft Gradient Vector | 🚧 DRAFT |  |
| `VE08` | 单线画 | Monoline | 🚧 DRAFT |  |
| `VE09` | 连续线画 | Continuous Line | 🚧 DRAFT |  |
| `VE10` | 抽象矢量 | Abstract Vector | 🚧 DRAFT |  |
| `VE11` | 企业矢量 | Corporate Vector | 🚧 DRAFT |  |
| `VE12` | UI 插画 | UI Illustration | 🚧 DRAFT |  |

#### painting · 绘画（Painting）

| ID | 中文名 | 英文名 | 状态 | 简介 |
|---|---|---|---|---|
| `PA01` | 古典油画 | Classical Oil Painting | ✅ ACTIVE | 古典构图、罩染光影、典雅色调 |
| `PA02` | 写实油画 | Realistic Oil Painting | 🚧 DRAFT |  |
| `PA03` | 印象派 | Impressionism | ✅ ACTIVE | 光影色彩笔触分离、氛围优先 |
| `PA04` | 后印象派 | Post-Impressionism | 🚧 DRAFT |  |
| `PA05` | 表现主义 | Expressionism | 🚧 DRAFT |  |
| `PA06` | 现代油画 | Modern Oil Painting | 🚧 DRAFT |  |
| `PA07` | 厚涂 | Impasto | 🚧 DRAFT |  |
| `PA08` | 传统水彩 | Traditional Watercolor | ✅ ACTIVE | 透明水色、渗化、纸面水痕 |
| `PA09` | 柔和水彩 | Soft Watercolor | 🚧 DRAFT |  |
| `PA10` | 水粉 | Gouache | ✅ ACTIVE | 不透明水粉、扁平色块、可覆盖 |
| `PA11` | 丙烯画 | Acrylic Painting | 🚧 DRAFT |  |
| `PA12` | 粉彩画 | Pastel Painting | 🚧 DRAFT |  |
| `PA13` | 蛋彩画 | Tempera | 🚧 DRAFT |  |
| `PA14` | 湿壁画 | Fresco | 🚧 DRAFT |  |
| `PA15` | 数字绘画 | Digital Painting | ✅ ACTIVE | 数字媒介的绘画质感 |
| `PA16` | 绘画感数字艺术 | Painterly Digital Art | 🚧 DRAFT |  |

#### drawing · 素描线绘（Drawing）

| ID | 中文名 | 英文名 | 状态 | 简介 |
|---|---|---|---|---|
| `DR01` | 铅笔素描 | Pencil Drawing | ✅ ACTIVE | 石墨层次、纸面颗粒、灰度造型 |
| `DR02` | 炭笔素描 | Charcoal Drawing | 🚧 DRAFT |  |
| `DR03` | 钢笔线绘 | Pen Line Drawing | 🚧 DRAFT |  |
| `DR04` | 墨线画 | Ink Line Drawing | ✅ ACTIVE | 硬朗墨线、强调轮廓与走势 |
| `DR05` | 建筑线稿 | Architectural Line Drawing | 🚧 DRAFT |  |
| `DR06` | 速写 | Quick Gesture Sketch | 🚧 DRAFT |  |
| `DR07` | 复古松弛墨线速写 | Vintage Loose Ink Sketch | ✅ ACTIVE | 手绘不完美、断续重复线、纸张质感 |
| `DR08` | 极简线画 | Minimal Line Art | ✅ ACTIVE | 最少的线表达形状 |
| `DR09` | 连续线画 | Continuous Line Drawing | 🚧 DRAFT |  |
| `DR10` | 复古蚀刻线绘 | Vintage Etching Drawing | 🚧 DRAFT |  |
| `DR11` | 科学图版线绘 | Scientific Plate Drawing | 🚧 DRAFT |  |
| `DR12` | 产品设计草图 | Product Design Sketch | 🚧 DRAFT |  |

#### eastern-art · 东方艺术（Eastern Art）

| ID | 中文名 | 英文名 | 状态 | 简介 |
|---|---|---|---|---|
| `EA01` | 中国水墨 | Chinese Ink Wash | ✅ ACTIVE | 墨分五色、水韵晕染、留白意境 |
| `EA02` | 写意山水 | Freehand Landscape | 🚧 DRAFT |  |
| `EA03` | 工笔 | Gongbi | ✅ ACTIVE | 精细线描 + 矿物色渲染 |
| `EA04` | 青绿山水 | Blue-Green Landscape | 🚧 DRAFT |  |
| `EA05` | 白描 | Fine Outline / Bai Miao | 🚧 DRAFT |  |
| `EA06` | 宋代美学 | Song Dynasty Aesthetic | ✅ ACTIVE | 素雅、留白、极致的克制 |
| `EA07` | 敦煌矿物色 | Dunhuang Mineral Color | ✅ ACTIVE | 土红/石青/石绿/金，壁画质感 |
| `EA08` | 唐代壁画 | Tang Mural | 🚧 DRAFT |  |
| `EA09` | 中国年画 | Chinese Woodblock New Year Print | 🚧 DRAFT |  |
| `EA10` | 新中式 | Neo-Chinese | ✅ ACTIVE | 东方元素 + 现代设计语言 |
| `EA11` | 国潮 | Guochao | 🚧 DRAFT |  |
| `EA12` | 禅意东方极简 | Zen Eastern Minimalism | 🚧 DRAFT |  |
| `EA13` | 浮世绘 | Ukiyo-e | 🚧 DRAFT |  |
| `EA14` | 日本传统木版画 | Traditional Japanese Woodblock | 🚧 DRAFT |  |

#### print · 印刷艺术（Print Art）

| ID | 中文名 | 英文名 | 状态 | 简介 |
|---|---|---|---|---|
| `PR01` | 木刻 | Woodcut | ✅ ACTIVE | 木版刀具刻痕、黑白强烈 |
| `PR02` | 木版画 | Woodblock | 🚧 DRAFT |  |
| `PR03` | 雕刻版画 | Engraving | 🚧 DRAFT |  |
| `PR04` | 蚀刻版画 | Etching | ✅ ACTIVE | 酸蚀线条、松动画意 |
| `PR05` | 石版画 | Lithograph | 🚧 DRAFT |  |
| `PR06` | 丝网印刷 | Screen Print | 🚧 DRAFT |  |
| `PR07` | 孔版印刷 | Risograph | ✅ ACTIVE | 荧光/撞色、错位套印、颗粒 |
| `PR08` | 半色调印刷 | Halftone Print | 🚧 DRAFT |  |
| `PR09` | 复古印刷 | Vintage Print | 🚧 DRAFT |  |
| `PR10` | 报纸插画 | Newspaper Illustration | 🚧 DRAFT |  |

#### 3d · 3D / CGI（3D / CGI）

| ID | 中文名 | 英文名 | 状态 | 简介 |
|---|---|---|---|---|
| `TD01` | 照片级 CGI | Photoreal CGI | 🚧 DRAFT |  |
| `TD02` | 产品 CGI | Product CGI | 🚧 DRAFT |  |
| `TD03` | 建筑 CGI | Architectural CGI | 🚧 DRAFT |  |
| `TD04` | 卡通 3D | Cartoon 3D | 🚧 DRAFT |  |
| `TD05` | 柔和 3D | Soft 3D | 🚧 DRAFT |  |
| `TD06` | 黏土 3D | Clay 3D | ✅ ACTIVE | 黏土质感、手作感 |
| `TD07` | 塑料 3D | Plastic 3D | 🚧 DRAFT |  |
| `TD08` | 低多边形 | Low Poly | 🚧 DRAFT |  |
| `TD09` | 体素 | Voxel | 🚧 DRAFT |  |
| `TD10` | 等距 3D | Isometric 3D | 🚧 DRAFT |  |
| `TD11` | 微缩模型 | Miniature | 🚧 DRAFT |  |
| `TD12` | 立体模型 | Diorama | ✅ ACTIVE | 手工立体场景、桌面剧场 |
| `TD13` | 玩具感 3D | Toy-like 3D | 🚧 DRAFT |  |
| `TD14` | 游戏 CG | Game Cinematic 3D | 🚧 DRAFT |  |
| `TD15` | 未来主义 CGI | Futuristic CGI | 🚧 DRAFT |  |
| `TD16` | 抽象 3D | Abstract 3D | 🚧 DRAFT |  |

#### craft · 手工艺（Craft）

| ID | 中文名 | 英文名 | 状态 | 简介 |
|---|---|---|---|---|
| `CR01` | 剪纸 | Paper Cut | 🚧 DRAFT |  |
| `CR02` | 纸艺 | Paper Craft | 🚧 DRAFT |  |
| `CR03` | 折纸 | Origami | 🚧 DRAFT |  |
| `CR04` | 手工黏土 | Handmade Clay | 🚧 DRAFT |  |
| `CR05` | 毛毡艺术 | Felt Art | 🚧 DRAFT |  |
| `CR06` | 编织艺术 | Knitted Art | 🚧 DRAFT |  |
| `CR07` | 刺绣 | Embroidery | 🚧 DRAFT |  |
| `CR08` | 织物纺织 | Fabric Textile | 🚧 DRAFT |  |
| `CR09` | 陶艺 | Ceramic Art | 🚧 DRAFT |  |
| `CR10` | 瓷器艺术 | Porcelain Art | 🚧 DRAFT |  |
| `CR11` | 马赛克 | Mosaic | 🚧 DRAFT |  |
| `CR12` | 手工拼贴 | Handmade Collage | 🚧 DRAFT |  |

#### graphic-design · 平面设计（Graphic Design）

| ID | 中文名 | 英文名 | 状态 | 简介 |
|---|---|---|---|---|
| `GD01` | 瑞士设计 | Swiss Design | ✅ ACTIVE | 网格系统、无衬线、客观秩序 |
| `GD02` | 国际字体风格 | International Typographic Style | 🚧 DRAFT |  |
| `GD03` | 包豪斯 | Bauhaus | 🚧 DRAFT |  |
| `GD04` | 构成主义 | Constructivism | 🚧 DRAFT |  |
| `GD05` | 装饰艺术 | Art Deco | 🚧 DRAFT |  |
| `GD06` | 新艺术运动 | Art Nouveau | 🚧 DRAFT |  |
| `GD07` | 世纪中叶现代 | Mid-century Modern | 🚧 DRAFT |  |
| `GD08` | 孟菲斯 | Memphis | 🚧 DRAFT |  |
| `GD09` | 粗野主义 | Brutalism | 🚧 DRAFT |  |
| `GD10` | 新粗野主义 | Neo Brutalism | 🚧 DRAFT |  |
| `GD11` | 极简平面设计 | Minimal Graphic Design | 🚧 DRAFT |  |
| `GD12` | 编辑设计 | Editorial Design | 🚧 DRAFT |  |
| `GD13` | 杂志设计 | Magazine Design | 🚧 DRAFT |  |
| `GD14` | 复古海报 | Vintage Poster | 🚧 DRAFT |  |
| `GD15` | 现代海报 | Modern Poster | 🚧 DRAFT |  |
| `GD16` | 几何平面设计 | Geometric Graphic Design | 🚧 DRAFT |  |

#### concept-art · 概念与游戏美术（Concept / Game Art）

| ID | 中文名 | 英文名 | 状态 | 简介 |
|---|---|---|---|---|
| `GA01` | 环境概念设计 | Environment Concept Art | 🚧 DRAFT |  |
| `GA02` | 角色概念设计 | Character Concept Art | 🚧 DRAFT |  |
| `GA03` | 奇幻概念设计 | Fantasy Concept Art | 🚧 DRAFT |  |
| `GA04` | 科幻概念设计 | Sci-Fi Concept Art | 🚧 DRAFT |  |
| `GA05` | 数字绘景 | Matte Painting | 🚧 DRAFT |  |
| `GA06` | 游戏宣传图 | Game Splash Art | 🚧 DRAFT |  |
| `GA07` | 卡牌插画 | Card Illustration | 🚧 DRAFT |  |
| `GA08` | RPG 插画 | RPG Illustration | 🚧 DRAFT |  |
| `GA09` | 策略游戏美术 | Strategy Game Art | 🚧 DRAFT |  |
| `GA10` | AAA 游戏视觉 | AAA Game Visual | 🚧 DRAFT |  |
| `GA11` | 游戏加载画面 | Game Loading Screen | 🚧 DRAFT |  |
| `GA12` | 世界观构建 | Worldbuilding Art | 🚧 DRAFT |  |

#### fantasy · 奇幻与超现实（Fantasy / Surreal）

| ID | 中文名 | 英文名 | 状态 | 简介 |
|---|---|---|---|---|
| `FA01` | 奇幻 | Fantasy | 🚧 DRAFT |  |
| `FA02` | 高奇幻 | High Fantasy | 🚧 DRAFT |  |
| `FA03` | 黑暗奇幻 | Dark Fantasy | 🚧 DRAFT |  |
| `FA04` | 魔幻现实主义 | Magical Realism | 🚧 DRAFT |  |
| `FA05` | 超现实主义 | Surrealism | ✅ ACTIVE | 梦境逻辑、物像错置、心理空间 |
| `FA06` | 梦境感 | Dreamlike | 🚧 DRAFT |  |
| `FA07` | 梦核 | Dreamcore | 🚧 DRAFT |  |
| `FA08` | 怪核 | Weirdcore | 🚧 DRAFT |  |
| `FA09` | 阈限空间 | Liminal Space | 🚧 DRAFT |  |
| `FA10` | 象征艺术 | Symbolic Art | 🚧 DRAFT |  |
| `FA11` | 迷幻艺术 | Psychedelic | 🚧 DRAFT |  |
| `FA12` | 赛博朋克 | Cyberpunk | 🚧 DRAFT |  |
| `FA13` | 蒸汽朋克 | Steampunk | 🚧 DRAFT |  |
| `FA14` | 太阳朋克 | Solarpunk | 🚧 DRAFT |  |
| `FA15` | 复古未来主义 | Retrofuturism | 🚧 DRAFT |  |
| `FA16` | 生物朋克 | Biopunk | 🚧 DRAFT |  |

#### retro · 复古年代（Retro / Era）

| ID | 中文名 | 英文名 | 状态 | 简介 |
|---|---|---|---|---|
| `RT01` | 维多利亚时代 | Victorian | 🚧 DRAFT |  |
| `RT02` | 1920年代 | 1920s | 🚧 DRAFT |  |
| `RT03` | 1930年代 | 1930s | 🚧 DRAFT |  |
| `RT04` | 1940年代 | 1940s | 🚧 DRAFT |  |
| `RT05` | 1950年代 | 1950s | 🚧 DRAFT |  |
| `RT06` | 1960年代 | 1960s | 🚧 DRAFT |  |
| `RT07` | 1970年代 | 1970s | 🚧 DRAFT |  |
| `RT08` | 1980年代 | 1980s | 🚧 DRAFT |  |
| `RT09` | 1990年代 | 1990s | 🚧 DRAFT |  |
| `RT10` | 千禧风 | Y2K | 🚧 DRAFT |  |
| `RT11` | 老上海 | Old Shanghai | 🚧 DRAFT |  |
| `RT12` | 香港复古 | Hong Kong Retro | 🚧 DRAFT |  |
| `RT13` | 昭和日本 | Showa Japan | 🚧 DRAFT |  |
| `RT14` | 苏联复古 | Soviet Retro | 🚧 DRAFT |  |

#### information · 信息与科学（Information / Scientific）

| ID | 中文名 | 英文名 | 状态 | 简介 |
|---|---|---|---|---|
| `IN01` | 信息图 | Infographic | 🚧 DRAFT |  |
| `IN02` | 科学插画 | Scientific Illustration | 🚧 DRAFT |  |
| `IN03` | 教育插画 | Educational Illustration | 🚧 DRAFT |  |
| `IN04` | 技术图表 | Technical Diagram | 🚧 DRAFT |  |
| `IN05` | 蓝图 | Blueprint | 🚧 DRAFT |  |
| `IN06` | 分解图 | Exploded View | 🚧 DRAFT |  |
| `IN07` | 剖面图 | Cutaway Illustration | 🚧 DRAFT |  |
| `IN08` | 解剖插画 | Anatomical Illustration | 🚧 DRAFT |  |
| `IN09` | 植物图版 | Botanical Plate | 🚧 DRAFT |  |
| `IN10` | 地图插画 | Map Illustration | 🚧 DRAFT |  |
| `IN11` | 时间轴视觉 | Timeline Visual | 🚧 DRAFT |  |
| `IN12` | 流程插画 | Process Illustration | 🚧 DRAFT |  |
| `IN13` | 等距信息图 | Isometric Infographic | 🚧 DRAFT |  |
| `IN14` | 数据插画 | Data Illustration | 🚧 DRAFT |  |


## 如何使用

### 调用方式（技能命令）

主技能名：**`visual-style-engine`**。在 WorkBuddy 对话中按以下方式启用：

| 方式 | 用法 | 说明 |
|---|---|---|
| 斜杠命令 | `/visual-style-engine <需求描述>` | 显式调用主技能，如 `/visual-style-engine 为这篇文章生成一张 IL03 风格的概念配图` |
| 自动触发 | 直接描述生图需求 | 命中 `SKILL.md` 的 description（需要选风格/统一视觉/编译 Prompt/风格 QA 时）自动加载 |
| 模块直调 | 引用 `skills/<name>/SKILL.md` | 需要单独使用某个模块时按其文档执行 |

主技能加载后会自动编排 8 个模块，**无需用户逐个调用**。模块技能名与触发场景：

| 模块技能名 | 什么需求会用到它 |
|---|---|
| `visual-intent-analyzer` | 给内容但没说风格，需要先判断"该怎么表达" |
| `visual-style-selector` | `style=auto` 或用户问"适合什么画风" |
| `visual-style-library` | 读取/比较某个 Style 的定义、DNA、规则 |
| `visual-identity-manager` | 一本书/一个系列/一个栏目要多张图且视觉统一 |
| `image-prompt-compiler` | 已有 Style/Spec，需要把它变成可发送的 Prompt |
| `image-model-adapter` | 需要按 seedream/gpt-image/flux/mj/sdxl 各自习惯编译 |
| `style-reference-manager` | 需要参考图来增强一致性，或校验参考图质量 |
| `image-style-evaluator` | 已有生成结果，需要做风格一致性评分与纠偏 |

### 主技能调用示例（按意图）

以下示例均可直接用 `/visual-style-engine ...` 触发，或把句子当作普通需求描述（命中 description 时自动加载主技能并编排 8 个模块）。

```text
# ── 1. 指定风格直出（跳过 selector）──
/visual-style-engine style=VE01 生成一张极简矢量插画，莫兰迪配色
/visual-style-engine style=EA01 画一幅中国水墨表现「孤舟蓑笠翁」
/visual-style-engine style=IL03 概念插画：用象征手法表现「认知负荷」
/visual-style-engine style=TD06 黏土风格做一个可爱的太阳能电池板

# ── 2. 自动选风格（style=auto / 不指定）──
/visual-style-engine 为《人类简史》农业革命章节生成 16:9 配图，要历史感但不是历史照片
/visual-style-engine 给这篇讲「复利」的公众号文章配一张概念图
/visual-style-engine 周末爬山的朋友圈配图，清新一点

# ── 3. 多图 / 系列：建立视觉身份 ──
/visual-style-engine 这个系列 12 张图要保持统一画风，帮我建立视觉身份
/visual-style-engine 为《高中物理图解》全书建立视觉身份：主风格 IL16+VE01，限定 3 色板
/visual-style-engine 品牌栏目「每周一书」固定栏目画风，先定 identity

# ── 4. 叠加 Attribute（色板 / 光 / 情绪）──
/visual-style-engine style=VE01 勾股定理示意图，色板 PAL_MORANDI，扁平无阴影
/visual-style-engine style=CI04 黑色电影质感的产品氛围图，硬光高反差
/visual-style-engine style=EA06 宋代美学留白，情绪 calm、克制

# ── 5. 参考图驱动 ──
/visual-style-engine 参考这张图.jpg 提取视觉特征并匹配最接近的 Style
/visual-style-engine 按这张参考图生成一张同风格的封面

# ── 6. 生成后评估与纠偏 ──
/visual-style-engine 评估这张图是否符合 IL03 概念插画风格
/visual-style-engine 这张图好像偏写实了，按 VE01 纠偏重生成

# ── 7. 不同内容域 ──
/visual-style-engine 高中数学，用极简矢量插画解释勾股定理，留白充足，不要写实
/visual-style-engine 产品摄影风展示一只手表，背景纯净
/visual-style-engine 海报底图：瑞士风格 + 大留白给标题
/visual-style-engine 敦煌矿物色风格绘制飞天，壁画质感
/visual-style-engine 超现实主义风格表现「梦境与现实的边界」
```

> 提示：指定 `style=<ID>` 时请确保该 ID 在「风格列表」中状态为 ✅ ACTIVE，否则引擎会回退到相近的 ACTIVE 风格并告知你。

### 各模块技能调用示例

主技能加载后会自动编排下面 8 个模块，**绝大多数情况你只需调用主技能**。但你也可以在对话中直接描述某个模块的意图，让对应模块单独工作（或引用 `skills/<name>/SKILL.md` 按其流程执行）。各模块的典型调用示例：

**① `visual-intent-analyzer` · 意图分析器**
> 给内容但没说风格，需要先判断"该怎么表达"。
```text
/visual-style-engine 分析这段科普内容的视觉意图：
「光合作用是植物把光能转化为化学能的过程」
→ 输出 visual_intent: domain=science, visual_role=process_explanation,
   mood=[clear, curious], information_density=high, narrative_mode=diagrammatic
```

**② `visual-style-selector` · 风格选择器**
> `style=auto` 或用户问"适合什么画风"。
```text
/visual-style-engine 自动为这条朋友圈文案选个插画风格：周末去爬山
→ 候选: IL06 极简插画 / VE05 有机矢量 / IL02 编辑插画
→ 选中 IL06 极简插画 (confidence 0.88)，原因: lifestyle, minimal, calm

/visual-style-engine 帮我比较 IL03 和 IL05 哪个更适合表达「信息茧房」
```

**③ `visual-style-library` · 风格库**
> 读取 / 比较某个 Style 的定义、DNA、规则、锚点。
```text
/visual-style-engine 给我看 IL03 概念插画的完整定义（fingerprint / rules / anchors / confusion_with）
/visual-style-engine 比较 VE01 和 IL06 在「留白」处理上的差异
/visual-style-engine VE01 的中文名、英文名、负向锚点是什么？
```

**④ `visual-identity-manager` · 视觉身份管理器**
> 一本书 / 一个系列 / 一个栏目要多张图且视觉统一。
```text
/visual-style-engine 为《高中物理图解》全书建立视觉身份：
主风格 IL16 + VE01，限定色板 PAL_MUTED，线宽统一，纹理锁定无纹理
→ 产出 identity 文件，后续 50 张图自动复用
```

**⑤ `image-prompt-compiler` · 提示词编译器**
> 已有 Style / Spec，需要把它变成可发送的 Prompt（AST + Style Lock）。
```text
/visual-style-engine 把「VE01 + 勾股定理 + PAL_MORANDI」编译成 Prompt AST 与最终 Prompt
/visual-style-engine 用 IL03 的 Style Lock 锁定 Shape/Line/Negative，生成 Canonical Prompt
```

**⑥ `image-model-adapter` · 模型适配器**
> 需要按 seedream / gpt-image / flux / midjourney / sdxl 各自习惯编译。
```text
/visual-style-engine 用 midjourney 的参数格式重写上面的 Prompt（--ar 16:9 --s 250 --style raw）
/visual-style-engine 把同一份 Spec 分别编译成 seedream 与 gpt-image 两种 Prompt
```

**⑦ `style-reference-manager` · 参考图管理器**
> 需要参考图增强一致性，或校验参考图质量。
```text
/visual-style-engine 用这张参考图.jpg 提取视觉特征并匹配最接近的 Style（同时生成 Custom Style）
/visual-style-engine 校验这批参考图是否足够代表 EA01 水墨，给出补充建议
```

**⑧ `image-style-evaluator` · 风格评估器**
> 已有生成结果，需要做风格一致性评分与纠偏。
```text
/visual-style-engine 评估这张图是否符合 EA01 水墨风格（8 维评分 + 命中 MUST NOT 检查）
→ 输出: shape 90 / line 88 / color 85 / shading 82 / lighting 80 / texture 90 /
        composition 84 / detail 86 = 85 PASS
/visual-style-engine 这张 VE01 图留白太少了，触发纠偏并重新生成
```

### 模式一：自动风格（默认）

用户只给内容，引擎自动完成意图分析 → 选风格 → 编译 → 出图：

```yaml
request:
  usage: book_video          # 使用场景
  content: "《人类简史》农业革命章节：农业带来稳定，也带来新的束缚"
  aspect_ratio: "16:9"
  model: seedream            # seedream / gpt-image / flux / midjourney / sdxl
  style: auto                # 自动选择
  project_id: sapiens        # 多图项目（自动建 Identity）
```

### 模式二：指定 Style

用户明确指定风格 ID 或 Preset（跳过 selector）：

```yaml
request:
  content: "..."
  style: VE01                # 指定 Style ID（style-library 中 ACTIVE）
  attributes:                # 可选：叠加 Attribute
    palette: PAL_MORANDI
    lighting: LIGHT_FLAT_GRAPHIC
    mood: [calm, elegant]
```

### 模式三：参考图驱动

用户提供参考图 → 提取视觉特征 → 匹配已知 Style 或生成 Custom Style（默认 project 范围，人工确认后可升级 library）。

### 执行流程（5 步）

1. **意图分析**：调用 `visual-intent-analyzer`，从内容提取 `visual_intent`（domain / visual_role / mood / 信息密度 / 叙事模式）；
2. **选风格**：调用 `visual-style-selector`（style=auto 时）得到候选 + 选中 Style + 可解释原因；多图项目同时调用 `visual-identity-manager` 建立 Identity（Style/Palette/Texture Lock）；
3. **读规格**：`visual-style-library` 读取 Style 的 fingerprint / rules / canonical_prompt / negative；
4. **编译**：`image-prompt-compiler` 生成 Prompt AST → `image-model-adapter` 按目标模型编译出最终 Prompt（含负向锁）；
5. **生成 + 评估**：生成图片后 `image-style-evaluator` 按 8 维评分；PASS 交付，CORRECT/REGENERATE 按 correction rules 纠偏重跑。

每个模块的触发条件、输入输出、边界见 `skills/<name>/SKILL.md`。

### 快速上手示例

用户一句话：**"为《人类简史》'农业革命'章节生成一张 16:9 配图，要有历史感但不是历史照片，表达'农业带来稳定也带来束缚'。"**

```text
① intent-analyzer → domain: history, visual_role: conceptual_explanation,
   narrative_mode: metaphorical, mood: [reflective, slightly_oppressive]
② selector       → selected: IL03 (0.94)，候选 CI08 / PR04
③ attributes     → palette: PAL_MUTED_EARTH, texture: TEX_FINE_GRAIN,
   composition: symbolic center
④ compiler       → Prompt AST + Style Lock（IL03 的 Shape/Rendering/Negative 锁定）
⑤ adapter        → seedream / gpt-image 各自的最终 Prompt
⑥ evaluator      → 若漂向 CI08（电影摄影）→ correction：
   reduce photographic realism / restore conceptual editorial rendering
```

## 输出是什么

引擎内部所有模块通过统一 Envelope（`schemas/visual-request.schema.yaml`）传递，各 Skill 只写自己负责的节点。完整请求与结果结构：

```yaml
visual_request:
  request_id: "req_20260817_001"
  project_id: sapiens
  usage: book_video
  model: seedream
  aspect_ratio: "16:9"

  content: {}               # 用户内容（intent-analyzer 读取）
  visual_intent:            # ① intent-analyzer 输出
    domain: history
    visual_role: conceptual_explanation
    narrative_mode: metaphorical
    mood: [reflective, slightly_oppressive]
    information_density: medium
  style:                    # ② selector 输出
    selected: {id: IL03, version: 1.2.0, confidence: 0.94}
    candidates: [{style: IL03, score: 0.94}, {style: CI08, score: 0.84}]
    reason: [conceptual explanation, symbolic representation]
  attributes:               # ③ Attribute 合并结果
    palette: PAL_MUTED_EARTH
    texture: TEX_FINE_GRAIN
    lighting: LIGHT_OVERCAST_SOFT
  identity:                 # 多图项目（identity-manager 输出）
    primary_style: {id: IL03, version: 1.2.0}
    palette: PAL_MUTED_EARTH
    texture: TEX_FINE_GRAIN
    style_lock: {shape: high, line: high, texture: high}
  references: []            # reference-manager 输出的参考图清单
  generation:               # ④ compiler + adapter 输出
    prompt_ast: {subject: ..., scene: ..., style: ..., attributes: ..., locks: {...}}
    canonical_prompt: "..."
    model_prompt: "..."     # adapter 编译后的最终 Prompt
    negative_prompt: "..."
  evaluation:               # ⑤ evaluator 输出
    style_score: 86
    dimensions: {shape: 91, line: 88, color: 82, shading: 90,
                 lighting: 83, texture: 79, composition: 84, detail: 87}
    decision: PASS          # PASS / CORRECT / REGENERATE
    corrections: []
```

**交付物形态**：

- 单次生成：`visual_request` 完整 JSON/YAML 记录（可追溯，含 style/adapter/compiler 版本）
- 上层应用拿到的结果：`visual_intent + style + visual_spec + model_prompt + negative_prompt + references + evaluation_profile`——**无需理解模型 Prompt 细节**
- 多图项目：额外产出 `project identity` 文件（复用全部后续图片）与观测日志（SSR/PICS 等指标）

**中间产物**：`style-library/<category>/<ID>.yaml` 是风格定义（数据）；`adapters/<model>/` 是模型差异（数据）；8 个 SKILL.md 是执行流程（技能）。

## 仓库结构

```text
visual-style-engine/
├── SKILL.md                  ← 引擎主入口技能（触发条件 / 协作链 / 模块导航）
├── SKILL-SYSTEM.md           ← 系统设计浓缩版（评分/判定/版本/治理规则）
├── schemas/                  ← 7 个 Schema：style / attribute / preset / identity / reference / evaluation / visual-request
├── skills/                   ← 8 个模块 Skill（各自 SKILL.md + references/）
├── style-library/            ← base 父类 + 16 个一级分类 catalog + Core Style yaml
├── attributes/               ← palette / lighting / composition / camera / texture / material / line / shape / mood / era
├── presets/                  ← Style + Attribute 稳定组合
├── strategies/               ← 内容域策略：book / video / education / poster / social / branding / product
├── adapters/                 ← 模型适配：seedream / gpt-image / flux / midjourney / sdxl
├── references/               ← 参考图索引（styles / projects）
├── evaluation/               ← profiles / confusion-matrix / correction-rules / benchmarks
└── tests/                    ← skill-tests / style-tests / adapter-tests / regression + style-lint 校验
```

## 核心工作流

```text
Content → Visual Intent → Style Selector → Visual Identity
       → Prompt Compiler (AST + Style Lock) → Model Adapter
       → Generator → Style Evaluator → PASS / CORRECT / REGENERATE
```

## 现状

✅ 已建成：体系骨架、Schema、8 Skill、16 分类 Catalog（222 Style）、Core 40 Style 定义（8 旗舰完整 + 32 紧凑）、Attribute 库、Strategies、Adapters、Evaluation、Lint/测试框架。详见上文「风格列表」。

🚧 Roadmap（按设计文档第 75/59 节）：

1. Core 40 Style 完整规格（紧凑版补齐 must/must_not/correction 等生产规格）
2. 每个 Style 5 类 Benchmark 实测 + 参考图 3–6 张采集评审
3. 跨模型 CMCS 数据回填（Seedream / GPT Image / Flux / MJ）
4. Baseline / Regression 实测（skill 行为测试）
5. Style Search / Similarity / Recommendation UI
6. 222 → 全量 Style 库（持续补全 DRAFT 规格）

## 质量指标

SSR（首轮通过）/ CMCS（跨模型一致性 ≥80）/ PICS（项目一致性 ≥85）/ FDR / CRR。详见 `SKILL-SYSTEM.md` 第 6/12 节。
