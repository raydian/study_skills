# Visual Intent 维度参考

用于 intent-analyzer 的输出取值。取值保持一致，供 selector 匹配 Style。

## domain（内容域）

history / science / literature / poetry / business / management / psychology / philosophy / education / biography / fiction / fantasy / health / finance / technology / travel / art / religion / sociology / data

## content_type

- nonfiction：非虚构知识/论述
- fiction：虚构叙事
- poetry：诗歌/文学
- data：数据/图表导向
- procedure：流程/操作说明
- argument：论证/观点

## visual_role

| role | 含义 | 典型页面 |
|---|---|---|
| conceptual_explanation | 解释抽象概念 | 章节概念页、方法论 |
| narrative_scene | 讲述具体场景 | 故事、事件、传记情节 |
| metaphor | 比喻性表达 | 抽象关系具象化 |
| symbolic | 象征性表达 | 文化/心理意象 |
| decorative | 装饰性（低信息） | 章节分隔、引言页 |
| data_viz | 数据可视化 | 图表、地图、流程 |
| portrait | 人物呈现 | 人物专栏、封面 |
| product_show | 产品/物品呈现 | 产品图、物件图 |

## information_density

- low：纯情绪/氛围，几乎无信息
- medium：一个核心概念 + 少量支撑元素
- high：多元素、关系、标注（地图/流程图）

## narrative_mode

symbolic（象征） / literal（写实陈述） / abstract（抽象） / documentary（纪实） / persuasive（说服）

## mood 词表（与 attributes/mood/ 一致）

calm / healing / warm / romantic / poetic / dreamy / mysterious / dark / lonely / melancholic / hopeful / joyful / playful / energetic / epic / majestic / serious / intellectual / elegant / luxury / minimal / futuristic / nostalgic / sacred / tense / introspective / documentary / youthful / whimsical / meditative
