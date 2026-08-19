# SKILL-SYSTEM — AI Visual Style Engine 系统设计（浓缩版）

> 完整设计方案见 `design/AI_Visual_Style_Skill_System_Design.md`（v1.0）。本文件为引擎仓库内的可执行版本。

## 1. 系统目标

模型无关的视觉风格基础设施：**可定义、可解释、可组合、可继承、可适配、可评测、可纠偏、可版本化**。

1. 同一 Style 在不同主题下保持相同视觉语言；
2. 同一 Style 在不同生图模型中差异可控（Adapter 吸收）；
3. 同一项目连续生成几十/几百张图不发生明显风格漂移（Visual Identity）；
4. 上层业务无需理解模型 Prompt 差异（统一接口）；
5. Style 可被选择、继承、组合、版本化、测试；
6. 风格库持续扩展而不产生重复风格（DNA 距离 + Attribute 拆分）。

## 2. 核心概念

| 概念 | 定义 | 举例 |
|---|---|---|
| Style | 完整视觉语言，回答"这张图应该长什么样" | VE01 Minimal Vector / DR07 Vintage Loose Ink Sketch |
| Attribute | 跨 Style 组合的视觉参数 | Palette / Lighting / Composition / Camera / Texture / Mood / Era |
| Preset | Style + 常用 Attribute 稳定组合 | 极简矢量 · 糖果清新 |
| Visual Identity | 项目级视觉身份（书/视频/系列/品牌） | Style Lock + Palette Lock + Texture Lock |
| Style DNA | 数值化视觉向量（0–10），用于比较/去重/选择/一致性 | realism:1, abstraction:8, detail_density:2... |
| Style Fingerprint | 8 维视觉指纹：Shape/Line/Color/Shading/Lighting/Texture/Composition/Detail | 8 项稳定 → 同一视觉语言 |
| Canonical Prompt | 模型无关的正向/负向语义锚点 | style yaml 的 canonical_prompt |

## 3. 非目标

不训练模型、不替代生图平台、不解决模型本身能力问题、不承担精确排版/文字/数据图表（交 SVG/HTML/Remotion）、不把每个审美概念变成独立 Style、不用超长 Prompt 解决所有问题。

## 4. 三层架构

```text
Canonical Style Spec (model-agnostic)
        ↓
   Prompt AST + Style Lock
        ↓
Model Adapter (Seedream / GPT Image / Flux / MJ / SDXL)
        ↓
   Image Generator → Style Evaluator → PASS / CORRECT / REGENERATE
```

## 5. 8 个 Skill 职责边界

| Skill | 输入 | 输出 | 不负责 |
|---|---|---|---|
| visual-intent-analyzer | content/usage/audience/emotion/density | visual_intent（domain/role/mood/密度/叙事模式） | 选 Style、编译、生成 |
| visual-style-selector | visual_intent / style=auto | candidates + selected + reason | 改 Spec、编译 |
| visual-style-library | Style ID / 检索词 | Style Spec / DNA / Fingerprint / Rules | 生成 Prompt |
| visual-identity-manager | 项目多图需求 | project_id + style/palette/texture lock | 逐图编译 |
| image-prompt-compiler | Visual Spec + Attributes | Prompt AST → Canonical Prompt | 模型参数 |
| image-model-adapter | Canonical Prompt | 模型 Prompt + negative + 参数 | 修改 Style 核心定义 |
| style-reference-manager | Style/项目 | 参考图清单 + 元数据 | 生成图 |
| image-style-evaluator | 生成图 + Profile | 8 维评分 + decision + problems | 直接重画（触发纠偏） |

## 6. 评分与判定

### Selector 评分（权重可被 Strategy 覆盖）

```text
ContentMatch ×0.25 + VisualRoleMatch ×0.20 + NarrativeMatch ×0.15
+ MoodMatch ×0.10 + AudienceMatch ×0.08 + MediumMatch ×0.07
+ IdentityMatch ×0.10 + ConsistencyRisk ×0.05
```

### Evaluator 判定

```text
85–100  Strong Pass
80–84   Pass
65–79   Correction（按 correction rules 纠偏重走 Compiler）
0–64    Regenerate
```

默认权重：Shape 20% / Line 15% / Color 15% / Shading 10% / Lighting 10% / Texture 10% / Composition 10% / Detail 10%。DR07 等可覆盖提高 Line/Texture。

### 硬失败（直接 REGENERATE）

- 出现任一 MUST NOT 特征；
- 渲染方法错误（如矢量变摄影）。

### 项目级指标

- SSR：通过 Style QA 的生成次数 / 总生成次数
- CMCS：同一 Style 跨模型一致性（≥80，Core 20 要求 ≥85）
- PICS：同一项目多图一致性（20 张连续图 ≥85）
- FDR / CRR：首轮通过率 / 纠偏恢复率

## 7. Prompt 固定结构

```text
[SUBJECT] [SCENE] [STYLE LOCK] [VISUAL ATTRIBUTES] [COMPOSITION] [RENDERING REQUIREMENTS] [NEGATIVE STYLE LOCK]
```

- **可变**：Subject / Scene / Action
- **半锁定**：Palette / Lighting / Composition / Mood
- **强锁定**：Shape Language / Line Language / Rendering Method / Shading / Texture Policy / Style Negative

Compiler 禁止自动改写 immutable 区域语义。

## 8. Style 数量治理

禁止因"柔和/高饱和/暗色/明亮/黄金时刻/低角度/米黄色/糖果色/电影光/16:9/复古纸张"新建 Style → 用 Attribute。

新增 Style 前检查：新 Shape Language？新 Rendering Method？新 Line Language？新 Material 行为？DNA 距离？仅 Attribute 差异则不新增。

## 9. 分类与 Catalog

16 个一级分类、约 212 个 Style（`style-library/<category>/catalog.yaml` 全量清单）：

photography(16) / cinematic(12) / anime(14) / illustration(16) / vector(12) / painting(16) / drawing(12) / eastern-art(14) / print(10) / 3d(16) / craft(12) / graphic-design(16) / concept-art(12) / fantasy(16) / retro(14) / information(14)。

> 具体在世艺术家/工作室名称不作为 Canonical Style ID；使用可解释的视觉特征定义替代。

## 10. Style 最低文档规格

| 模块 | 最低要求 |
|---|---|
| Summary | 100–200 字 |
| Detailed Definition | 300–800 字 |
| Fingerprint | 8 维完整 |
| DNA | 11 个数值 |
| MUST / SHOULD / MAY / MUST NOT | ≥5 / ≥5 / ≥3 / ≥8 |
| Positive / Negative Anchor | 50–150 / 30–100 词 |
| Confusion Styles / Correction Rules | ≥2 / ≥5 |
| Test Prompts / References | ≥5 / ≥3 |

生产级 Style 总资料量 1500–3000 字。

## 11. 版本规则

```text
VE01@1.0.0
PATCH  词序微调、Adapter 小幅优化（不变视觉定义）
MINOR  增加约束/参考图、优化 Fingerprint（视觉范围不变）
MAJOR  DNA 改变、核心 Rendering Method 改变（旧版与新版已不是同一视觉语言）
```

生命周期：DRAFT → SPEC_READY → BENCHMARKING → REVIEW → ACTIVE → DEPRECATED → ARCHIVED。Selector 只推荐 ACTIVE。

## 12. 质量体系

- **Style Lint**：重复、Alias 冲突、属性矛盾、Canonical Anchor 含模型参数、MUST/MUST NOT 冲突、DNA 越界、Reference 缺失。
- **Adapter Lint**：是否删除 MUST、引入 MUST NOT、改变 Style 定义、用废弃参数、缺失 Style Lock。
- **Benchmark**：每个 Style 至少 5 类测试场景（Portrait / Still Life / Environment / Nature / Complex Scene）；Core 40 至少测 Seedream / GPT Image / Flux / MJ。
- **回归测试**：Style 更新后重跑 Benchmark，确保"优化"不使旧场景变差。
- **人工评审**：Machine Score + Human Review（可辨识、与相邻差异、Reference 代表性、AI cliché、过度约束）。

## 13. 当前建设进度与 Roadmap

已建成（Phase 0–1 + 起步）：

- ✅ 目录骨架、统一 Envelope、7 个 Schema
- ✅ 主入口 + 8 个模块 Skill（触发边界/协作链/协议）
- ✅ style-library：base 父类 + 16 分类 catalog + 旗舰 Style 完整定义（VE01/IL03/DR07 等）
- ✅ attributes：25 Palette / 22 Lighting / 26 Composition / 25 Texture / 30 Mood
- ✅ presets 示例、7 个 strategies、5 个 adapters、evaluation 体系
- ✅ tests：skill-tests / style-tests / adapter-tests / regression + style-lint 校验脚本

待建设（Roadmap，见 README）：

- Core 40 Style 完整规格 → 100 → 212
- 参考图采集与评审（3–6 张 / Core Style）
- 跨模型 Benchmark 实测数据回填
- 5 个测试场景的 Baseline/Regression 实测
- Style Search / Similarity / Recommendation UI

## 14. 验收标准（v1 Production Ready）

- Core 40 全部完整 Visual Spec、每 Style ≥5 类测试、无明显重复；
- 两个主模型 CMCS ≥80、Core 20 ≥85；
- 20 张连续图 PICS ≥85；
- 所有主要 Skill 有 trigger tests、无抢任务、Selector 输出可解释原因；
- 所有生成记录可追溯到 Style + Adapter + Compiler 版本。
