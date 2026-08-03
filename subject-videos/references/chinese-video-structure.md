# Chinese Video Structure

Use this reference for every `学科=语文` project before writing `content-design.md`, `storyboard.md`, or `口播稿.md`.

## Contents

- [Core Principle](#core-principle)
- [Required Planning Fields](#required-planning-fields)
- [Seven Teaching Modules](#seven-teaching-modules)
- [Scene Decomposition](#scene-decomposition)
- [Evidence Units](#evidence-units)
- [Theme And Core-Idea Instruction](#theme-and-core-idea-instruction)
- [Worked-Example Transfer](#worked-example-transfer)
- [Genre Routes](#genre-routes)
- [Suggested Time Balance](#suggested-time-balance)
- [Structure QA](#structure-qa)

## Core Principle

Build a reading journey:

`先感受 -> 提问题 -> 找证据 -> 建解释 -> 成结构 -> 会作答 -> 再理解`

The seven modules below are teaching stages, not seven scenes, seven pages, seven `<Sequence>` blocks, or seven Remotion components. Split, merge, or omit optional stages according to the target text, genre, evidence load, conceptual difficulty, and learning goal. Never force one module into one page.

Keep one primary learning goal per video and at most one secondary goal. Choose among:

- 文本鉴赏型: understand the text through evidence, structure, language, and theme;
- 考点方法型: teach one answer type through a real text and worked problem;
- 文言疏通型: connect language obstacles to sentence, plot, argument, character, and theme;
- 思辨阅读型: reconstruct concepts, claims, evidence, reasoning, and real-world implications.

Do not make one video carry a complete text explanation, literary history survey, every technique, every exam type, and a full unit review unless the source and requested scope genuinely require it.

## Required Planning Fields

Add these fields to the Chinese `content-design.md`:

```markdown
## 课程定位

- 主要学习目标：
- 次要学习目标（可选）：
- 文体路线：
- 核心阅读问题：
- 主旨形成位置：
- 方法迁移：包含 / 省略（说明理由）

## 模块与场景映射

| 教学模块 | 场景 id | 场景任务 | 文本证据/例题 | 学生认知变化 |
|---|---|---|---|---|
```

In `storyboard.md`, give every concrete scene a `moduleId` or explicit `所属模块`. Several scenes may belong to one module. One scene may bridge two adjacent modules when the transition is pedagogically natural.

## Seven Teaching Modules

### 0. 封面定位

Establish the title, genre, nearest learning range, and course atmosphere. Keep a brief pre-start state. Do not explain the theme on frame 0.

### 1. 初遇文本

Create a first encounter through expressive reading, a representative excerpt, a narrative scene, a contradiction, a concept conflict, or a real reading task.

- Poetry, ci, and short lyrical prose may use a full expressive reading.
- Long prose and novels should use a representative excerpt or conflict rather than reading the whole text.
- Classical Chinese should pair a short reading with an immediate comprehension obstacle or narrative question.
- Argumentative, expository, practical, and non-continuous texts may open with a problem or claim instead of an expressive reading.

The first encounter must create an observation or question that the rest of the video resolves. It is not decorative recitation.

### 2. 核心问题

State one or two reading questions and show a compact route map. Questions should expose a genuine interpretive obstacle, such as a contradiction between surface wording and deeper meaning, a character decision, an argument gap, or the relationship between form and effect.

Do not reveal an unsupported standard theme answer here. A theme may appear only as a hypothesis or suspense question.

### 3. 证据细读

Use two to four major evidence groups as the main teaching body. A long or difficult text may need more groups; a focused method video may need only one deeply developed group.

Each evidence group may become multiple scenes, for example:

1. show and read the selected text;
2. locate keywords, syntax, images, actions, claims, or material clues;
3. explain expression, structure, or reasoning;
4. compare a plausible weak reading with a stronger reading;
5. form a local conclusion and connect it to the core question.

Introduce author background, historical context, literary knowledge, allusions, and techniques exactly where they explain the current evidence. Do not create a long detached background or technique-list scene unless that knowledge is itself the lesson target.

### 4. 结构统整

Recombine the evidence into a text-level model: emotion curve, imagery web, character relationship, plot route, narrative perspective, argument chain, concept hierarchy, or multi-material comparison.

This module must synthesize rather than repeat. It should answer what the evidence means when viewed together and prepare the formal theme/core-idea explanation.

### 5. 方法迁移

Include this module when the requested goal involves appreciation, reading strategy, or exam answering. Use a real worked example tied to the target text. Pure recitation, literary-culture, or very short single-point videos may omit it and record the reason in `content-design.md`.

The number of scenes follows the problem's complexity. A full transfer may use separate scenes for the prompt, task parsing, evidence location, path A, path B, answer synthesis, and score check.

### 6. 回望收束

Return to the opening question and route map. Finish all three layers:

1. 文本结论: what the text ultimately expresses or argues;
2. 阅读方法: how the evidence led to that understanding;
3. 迁移提示: what to inspect first in a similar text or question.

Do not end with an inventory of disconnected facts.

## Scene Decomposition

Determine scene boundaries by teaching action, not module count.

Split a module when:

- the visual focus changes from one quote, paragraph, character, claim, or evidence group to another;
- a new reasoning step needs its own observation time;
- a real example moves from task parsing to evidence search or answer construction;
- text density would force body text below the approved size or cause subtitle overlap;
- the narration introduces a new local conclusion that should remain visible.

Merge scenes when:

- a background fact only explains one sentence and can appear as a side note;
- a technique label and its effect belong to the same evidence chain;
- a route overview would merely repeat the next board;
- a summary repeats the preceding conclusion without adding synthesis or transfer.

Avoid both extremes: one page per module and one page per paragraph. A scene should have one dominant teaching focus and enough narration, evidence, and visual change to justify its duration.

## Evidence Units

Use this reasoning chain for every major interpretation:

`原句或文本现象 -> 关键词/关系观察 -> 表达方式 -> 阅读效果 -> 局部结论 -> 核心问题`

Store or document for each unit:

- exact quote, paragraph, event, claim, chart, or material clue;
- what the student should notice;
- the inference connecting evidence to interpretation;
- the relevant technique, structure, context, or language knowledge;
- the local conclusion;
- its contribution to theme, character, argument, or answer construction.

Do not start with a technique name and search for proof afterward. Do not show an interpretation that cannot point back to visible textual evidence.

## Theme And Core-Idea Instruction

Every complete text-lecture video must explain the article's 主旨、主题或核心思想. Place the formal explanation where the evidence becomes sufficient, not on a fixed page.

- Opening: pose the theme as a question, tension, or provisional hypothesis.
- Evidence scenes: build local meanings, emotional turns, character attitudes, or subclaims.
- Late close reading or synthesis: state the formal theme/core idea and trace every part back to evidence.
- Closing: compress the theme and connect it to a transferable reading cue; do not repeat the previous board word for word.

A complete theme explanation should answer:

1. 写了什么或论述了什么；
2. 作者如何组织这些材料；
3. 表达了怎样的情感、态度、人物认识或中心观点；
4. 作品如何完成深化、转折、批判、升华或现实指向；
5. 哪些关键证据支撑以上判断。

For ambiguous or open texts, distinguish `文本可证的核心理解` from `有依据的延伸理解`. Present multiple interpretations only when each has textual support, and explain their shared evidence and point of divergence.

## Worked-Example Transfer

If method transfer is included, use an actual question from the source/exercise/exam when available. Otherwise write a complete question based on the target text; label it as a lesson-created question rather than inventing an exam source.

Never use only a slogan, formula, answer template, or abstract card. Every worked example must show:

1. **完整题目**: prompt, target passage, task verb, scope, and score information when known;
2. **审题定向**: identify the answer type and what the task verb requires;
3. **原文定位**: select evidence and explain why it is relevant;
4. **推理展开**: transform evidence into an interpretive or analytical claim;
5. **答案组织**: assemble a complete answer by score point;
6. **检查修正**: detect missing evidence, repetition, scope drift, empty labels, or unsupported theme claims.

Use this visible route:

`题目 -> 任务拆解 -> 证据定位 -> 推理路径 -> 答案合成 -> 得分检查`

### Multiple Solution Paths

When genuinely different approaches exist, teach two or three substantive paths, such as:

- poetry: imagery progression, emotional turns, or expression technique;
- character analysis: action/plot, descriptive method, or relationships;
- theme inquiry: title, key sentences, structural ending, or relevant context;
- argument analysis: claim chain, evidence function, reasoning method, or paragraph relation;
- multi-material reading: material-by-material extraction or issue-by-issue integration.

For each path, explain:

- its entry point and suitable question types;
- the evidence it prioritizes;
- the reasoning steps it makes visible;
- its blind spots or likely omissions;
- how its valid points merge into the final answer.

Do not manufacture multiple paths from synonymous labels. If one path is clearly best, teach it deeply and compare only the most likely wrong path.

## Genre Routes

Use the route that matches the text; expand each node into as many scenes as the evidence requires.

- 散文: 物象/事件 -> 内容线与情感线 -> 语言证据 -> 结构作用 -> 主旨深化 -> 例题迁移.
- 诗歌/词: 朗读入境 -> 核心张力 -> 关键诗句 -> 意象/情感/手法统整 -> 主旨 -> 例题迁移.
- 文言文/古文: 语境与朗读 -> 阅读障碍 -> 句意 -> 情节/观点 -> 人物/主旨 -> 题型迁移.
- 记叙文/小说: 场景或冲突 -> 情节证据 -> 人物关系与描写 -> 环境/叙述作用 -> 主题 -> 探究/鉴赏题.
- 议论文: 现实问题 -> 中心论点 -> 论据与推理链 -> 结构与语言 -> 核心思想 -> 论证题迁移.
- 说明文: 说明对象与任务 -> 特征证据 -> 说明顺序与方法 -> 语言准确性 -> 核心认识 -> 信息题迁移.
- 实用类/非连续性文本: 任务问题 -> 信息定位 -> 关键词提取 -> 多材料整合 -> 观点提炼 -> 分点作答.

Routes decide reading order; they are not universal scripts or fixed scene tables.

## Suggested Time Balance

Use these as diagnostics, not rigid quotas:

- cover, first encounter, and context: usually no more than `15%`;
- evidence close reading: usually `50-65%`;
- synthesis and formal theme instruction: usually `10-15%`;
- worked-example transfer when included: usually `15-25%`;
- closing: around `5%`.

If close reading is not the largest part of a complete text lecture, check whether background, technique lists, or summaries have displaced evidence-based teaching.

## Structure QA

Before finalizing `storyboard.md`, verify:

- the seven modules were not mapped mechanically to seven scenes or pages;
- the scene count follows the target text, evidence units, and learning goal;
- one clear core question drives the video;
- every major conclusion points to visible text or material evidence;
- background and technique knowledge appears where it explains evidence;
- close reading occupies the main teaching time;
- the formal theme/core idea appears after sufficient evidence and is revisited concisely at the end;
- no sequence explains the text paragraph by paragraph and then repeats the same content by emotion, imagery, and technique;
- every transfer section uses a complete real or clearly lesson-created question;
- the worked solution shows task parsing, evidence, reasoning, answer construction, and checking;
- multiple solution paths differ substantively and state how they combine;
- deleting any scene would remove a real teaching step, piece of evidence, reasoning transition, practice moment, or synthesis.

