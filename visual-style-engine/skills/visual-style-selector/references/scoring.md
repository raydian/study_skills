# Selector 评分细则

## 八项维度说明

| 维度 | 权重 | 判定依据 |
|---|---|---|
| ContentMatch | 0.25 | Style 与 domain/content_type 的契合（看 style 的 use_cases.recommended + category） |
| VisualRoleMatch | 0.20 | Style 与 visual_role 的匹配（概念解释 → 概念/编辑类；叙事 → 叙事/剧照类） |
| NarrativeMatch | 0.15 | 叙事模式匹配（symbolic → 概念/象征类；literal → 纪实/写实类） |
| MoodMatch | 0.10 | Style 的 visual_intent/mood 与意图 mood 的交集 |
| AudienceMatch | 0.08 | 受众匹配（儿童 → 童书/手工类；成人知识 → 编辑/概念类） |
| MediumMatch | 0.07 | 画幅/媒介契合（横屏视频 → 适合宽幅的构图；海报 → 留白充足） |
| IdentityMatch | 0.10 | 与项目 Visual Identity 的一致性（无 Identity 时取中性 0.5） |
| ConsistencyRisk | 0.05 | 风格漂移风险（高细节密度 Style 跨图漂移风险高，分越低） |

## 匹配速查（示例）

| Intent | 首选 | 备选 |
|---|---|---|
| 历史概念解释 | IL03 / IL04 | CI08 / PR04 |
| 心理/哲学隐喻 | IL05 / FA05 | IL03 / VE03 |
| 商业管理 | IL02 / VE01 | VE11 / TD02 |
| 文学叙事 | IL04 / CI01 | PA08 / FA05 |
| 教育插图 | IN03 / IL16 | AN04 / TD05 |
| 数据/流程 | IN01 / IN13 | IN04 / VE02 |
| 严肃纪实 | PH12 / CI11 | PH01 / PA02 |
| 复古氛围 | DR07 / PR04 | PR07 / RT07 |

## 常见错误（baseline 记录）

- 只输出一个风格词（如 "cinematic"）→ 必须输出 Style ID + 版本 + 原因；
- 混淆 Style / Palette / Era → Style 是完整视觉语言，Palette 是颜色属性，Era 是时代属性；
- 用户说"高级一点"时猜测性选择 → 按内容语义评分，不按模糊形容词；
- 多个冲突 Style → 输出 conflict 建议，按冲突解决顺序处理。
