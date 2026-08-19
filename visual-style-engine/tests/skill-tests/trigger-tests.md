# Skill Trigger Tests — 各模块触发测试（第 37/40 节）

测试方法：Baseline（无 Skill）→ Skill → Regression。
验收：Agent 正确识别触发条件、使用 Style Library、输出结构化 Visual Spec、不越权、按协作链调用。

## visual-intent-analyzer

| # | 输入 | 期望 |
|---|---|---|
| T01 | 用户给一段章节内容，要求"设计一张配图" | 触发；输出 domain/visual_role/mood/密度/叙事模式 |
| T02 | 用户直接给了 Visual Intent YAML | 不触发；跳过 |
| T03 | 压力：用户说"高级一点"（模糊形容词） | 按内容语义提取，不猜风格 |

## visual-style-selector

| # | 输入 | 期望 |
|---|---|---|
| T01 | `style=auto` + 内容 | 触发；输出 candidates + score + reason |
| T02 | 用户问"适合什么画风" | 触发；reason 可解释 |
| T03 | 用户已给 Style ID（如 VE01） | 不触发；去 style-library |
| T04 | 压力：用户要求错误分类（"就要赛博朋克"给历史内容） | 输出 conflict 或按 Identity 提示 |

## visual-style-library

| # | 输入 | 期望 |
|---|---|---|
| T01 | 查 IL03 | 返回 Spec 切片 + 版本 |
| T02 | 别名检索"干净矢量" | 命中 VE01 |
| T03 | 压力：查询不存在的 Style | 返回最接近 + 差异说明 |
| T04 | 继承查询（VE01 挂 VECTOR_BASE） | 合并父类基线 |

## visual-identity-manager

| # | 输入 | 期望 |
|---|---|---|
| T01 | 一本书多章节配图需求 | 触发；建 Identity（primary/secondary/palette/texture/style_lock） |
| T02 | 单张一次性图片 | 不触发 |
| T03 | 压力：已有 Identity 用户要求随机换画风 | 拒绝或记录冲突，Identity 优先 |

## image-prompt-compiler

| # | 输入 | 期望 |
|---|---|---|
| T01 | 有 Style + Scene，要模型 Prompt | 触发；输出 AST + Canonical + Negative |
| T02 | 用户只在讨论风格理论 | 不触发 |
| T03 | 压力：用户场景要求与 MUST NOT 冲突 | 输出 conflict，不静默照做 |
| T04 | 压力：请求修改 Style Lock immutable 语义 | 拒绝改写 |

## image-model-adapter

| # | 输入 | 期望 |
|---|---|---|
| T01 | Canonical → seedream | 自然语言句式，保留强锁定语义 |
| T02 | Canonical → gpt-image | 句子化，负向用文字排除 |
| T03 | 压力：模型不支持复杂文字 | fallback（无字图 + 后置排版），不硬生成 |
| T04 | 压力：要求删除 MUST | 拒绝 |

## style-reference-manager

| # | 输入 | 期望 |
|---|---|---|
| T01 | 为 Style 选参考图 | 输出 ≥3 张，覆盖不同 subject，metadata 完整 |
| T02 | 压力：用户提供参考图未指定 Style | 提取特征 → 匹配 Style / 建议 Custom Style（scope=project） |
| T03 | 参考图含强角色 Identity | 标记不合格 |

## image-style-evaluator

| # | 输入 | 期望 |
|---|---|---|
| T01 | 生成结果 + Profile | 8 维评分 + decision |
| T02 | 压力：矢量图生成出摄影效果 | 硬失败 / 低分 + correction 指令 |
| T03 | 项目多图 | 输出 PICS |
| T04 | 纠偏 3 次仍失败 | 交人工评审，记录 retry_count |

## 常见 baseline 错误（Skill 应修正的）

- 只输出一个风格词（如 "cinematic"）；
- 混淆 Style / Palette / Era；
- 把年代当 Style；
- 修改 Style Lock；
- 忽略 MUST NOT；
- 直接复制一个 Prompt 给所有模型；
- 不评估生成结果。
