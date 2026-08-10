# Physics Video Structure

Use this reference for every `学科=物理` knowledge-point video before designing `content-design.md`, `storyboard.md`, narration, or Remotion scenes.

The default audience is a high-school student learning the topic for the first time. Build conceptual understanding first, then connect it to assessment. The stages in this file are teaching stages, not fixed pages, scenes, or Remotion components. Split, merge, or omit concrete scenes only when the complete learning loop remains intact.

## Content Budget

One video should normally contain:

- one core physical model or law;
- at most two core assessment points;
- one primary conceptual difficulty;
- one related cluster of error points and misconceptions;
- one representative mother problem;
- one single-condition variation.

Split the lesson when independent models, unrelated mother problems, or more than two assessment points compete for attention. Do not compensate by rushing narration, shrinking text, skipping reasoning, or stacking several teaching purposes into one scene.

## Unified Teaching Arc

Use this learning path:

```text
现象 → 建模 → 规律 → 考点 → 难点 → 易错纠偏 → 母题 → 变式 → 复盘
```

The following ten stages implement that path. They are flexible teaching stages, not a required ten-page layout.

### 1. Phenomenon Hook

Start from one real phenomenon, experimental result, prediction conflict, or counter-intuitive judgment. Ask one question that can remain visible throughout the lesson. Do not reveal the complete law or formula before students have a reason to need it.

### 2. Learning Route

Show a compact route containing:

- the object or phenomenon being studied;
- the core model or law;
- the core assessment points;
- the primary difficulty;
- the misconception to correct;
- the problem type students will solve by the end.

Keep the current node highlighted during the lesson. Route nodes indicate progress, not page count.

### 3. Object And Process Modeling

Transform the real situation into a physical model in this order when applicable:

```text
研究对象 → 物理过程 → 状态划分 → 已知条件 → 忽略因素 → 参考系/正方向
```

Make each modeling decision visible. State what is retained, what is ignored, and why the simplification is valid. For multi-object or multi-stage problems, show object switching and process boundaries explicitly.

### 4. Law Formation

Build the law in this order:

```text
直观含义 → 现象/数据/推理证据 → 规范表述 → 公式 → 适用条件
```

Bind every symbol, vector, sign, unit, graph feature, and condition to the visible object or process. Keep the original physical conditions visible when a formula transformation could hide them. Plain language comes first; formal expression follows.

### 5. Core Assessment Points

For each assessment point, answer:

1. What is assessed?
2. How does it usually appear?
3. Which words, conditions, diagrams, or data are recognition signals?
4. What judgment, diagram, equation, or explanation must the student produce?
5. What is the scoring-critical expression?

Show one current assessment label at a time. Re-light the matching law or condition when it is used later in the mother problem.

### 6. Difficulty Breakthrough

A difficulty explains why the concept is hard to understand. Use:

```text
学生直觉 → 直觉失效 → 冲突原因 → 正确模型 → 判断方法
```

Common physics difficulty families include:

- abstraction from a real scene to an idealized model;
- vector direction, sign, and reference direction;
- state quantity versus process quantity;
- instantaneous versus average quantity;
- graph slope, area, intercept, and physical process;
- multiple objects, stages, constraints, or reference frames.

Do not solve a conceptual difficulty by repeating the definition. Show the conflict that makes the correct model necessary.

### 7. Error Point And Misconception Correction

Keep these concepts distinct:

- **难点**: why students find the idea difficult to understand;
- **易错点**: where students make a concrete mistake in judgment, modeling, equations, calculation, or expression;
- **认知误区**: an incorrect physical model or causal relationship already held by the student.

Correct each misconception with:

```text
错误说法/步骤 → 错误直觉来源 → 冲突证据 → 正确依据 → 防错提醒
```

Expose an important error once during concept formation, then revisit it at the exact mother-problem step where the error would occur. Do not leave all misconceptions on a detached warning page.

### 8. Representative Mother Problem

A mother problem is not the hardest available question. It is the smallest complete problem that reveals the core model and a reusable solution path.

Use:

```text
读题 → 识型 → 画图 → 建模 → 选规律 → 列式 → 求解 → 检查
```

At every step, answer:

- What are we doing now?
- Why is this step valid?
- Where do students commonly go wrong?

Label every equation with its object, process, condition, and physical basis. Check the result with the relevant combination of unit, direction, sign, magnitude, graph, boundary case, conservation relation, or real-world meaning.

Prefer textbook examples, exercises, and recurring exam prototypes. If the lesson creates a problem, label it `本课设计母题` in planning files and independently verify that it is complete and solvable.

### 9. Single-Condition Variation

Change exactly one meaningful condition, such as the studied object, process stage, direction, initial state, graph representation, or question form. Ask students to decide:

- whether the model changes;
- whether the original law remains applicable;
- which solution step must change;
- whether the same misconception appears again.

If the variation requires a different core model, route it to another lesson instead of treating it as near transfer.

### 10. Closed-Loop Review

Return to the opening question and learning route. Compress the lesson into:

- one model;
- one law;
- one or two assessment points;
- one difficulty judgment;
- one misconception-prevention cue;
- one mother-problem path.

The closing page summarizes the path and method cue; it does not repeat the full lecture.

## Four Physics Routes

Choose one primary route from the main learning goal. Add at most one secondary route when it supports the same goal. The presence of an experiment, graph, or calculation does not determine the primary route by itself.

### Concept Or Law

Use for a physical quantity, definition, law, or theorem.

```text
认知冲突 → 物理量建立 → 规律形成 → 条件边界 → 多种表征
→ 考点 → 难点纠偏 → 母题 → 变式
```

Requirements:

- start from a conflict the previous model cannot explain;
- keep one situation consistent across verbal, diagram, formula, vector, and graph representations;
- use positive examples, counterexamples, and boundary states to define applicability;
- choose a mother problem that tests concept use, representation translation, or condition judgment rather than only substitution.

### Experiment Or Inquiry

Use when the learning goal is how evidence establishes or tests a relationship.

```text
提出问题 → 作出猜想 → 设计实验 → 控制变量 → 操作测量
→ 数据处理 → 形成结论 → 误差分析 → 考点 → 实验母题
```

Requirements:

- identify the variables and relationship being studied;
- explain the purpose of every essential apparatus choice and operation;
- show the path from measurement to table, graph, fit, interpretation, and conclusion;
- distinguish an operational mistake, random uncertainty, and systematic error;
- keep the experimental conclusion within the evidence actually shown;
- cover apparatus, procedure, variable control, data/graph interpretation, error, and improvement in the mother problem when relevant.

### Calculation Or Method

Use when the learning goal is a stable modeling and solution method for a problem family.

```text
题型识别 → 对象选择 → 过程分段 → 画图建模 → 规律选择
→ 母题精解 → 易错分支 → 条件变式 → 方法压缩
```

Requirements:

- derive the method from a complete mother problem instead of presenting a context-free routine;
- use a situation diagram, process/state diagram, and relationship diagram when they clarify different decisions;
- show time axes or state chains for multi-stage problems;
- label every formula with its object, process, and condition;
- return the numerical or symbolic result to the physical situation for checking.

### Phenomenon Or Mechanism

Use when the learning goal is explaining why a phenomenon occurs or predicting how it changes.

```text
观察现象 → 提出矛盾 → 分层拆解 → 建立因果链 → 规律解释
→ 条件变化预测 → 实例验证 → 考点纠偏 → 机制母题
```

Requirements:

- distinguish the observed appearance from the physical process that produces it;
- make every arrow in the causal chain answer “why”;
- switch among force, motion, energy, field, wave, or microscopic layers only when the explanation requires it;
- ask for a prediction before revealing the changed result;
- convert everyday language into a precise physical statement before the review.

## Time And Emphasis

A focused lesson commonly lasts 6–10 minutes, but narration and teaching content determine the actual duration.

| Module | Suggested share |
|---|---:|
| cover and phenomenon hook | 5%–8% |
| modeling and law formation | 25%–30% |
| core assessment points | 12%–15% |
| difficulty breakthrough | 10%–15% |
| errors and misconceptions | 8%–12% |
| mother problem | 20%–25% |
| variation and review | 8%–12% |

These percentages are content budgets, not fixed scene durations. Experiment routes may spend more time on design and data; calculation routes may spend more on the mother problem. Neither may remove necessary modeling.

## Scene Focus

Each scene has:

- one dominant teaching purpose;
- one primary diagram, formula, experiment state, graph, or problem step;
- at most three supporting anchors;
- one highlighted reasoning step at a time;
- narration, formula, diagram, and subtitle describing the same physical state.

Do not show the full prompt, complete diagram, all equations, all errors, and final answer at once. Reveal semantic steps in reasoning order.

## Transition Contract

Every adjacent scene must preserve at least one of:

```text
问题、研究对象、物理过程、结论、图形、视觉位置
```

Use these transition patterns:

- **Question continuity**: the previous scene ends with the question the next scene answers.
- **Object continuity**: a real object becomes an idealized model; a trajectory becomes axes; a force arrow moves into a force diagram; data points become a fitted graph.
- **Conclusion continuity**: a law, condition, or misconception card moves to the side and re-lights when used.
- **Narration continuity**: use causal bridges instead of mechanical announcements.
- **State continuity**: during pauses, keep the latest meaningful model or evidence visible.

The visual chain should feel like one problem being progressively resolved:

```text
真实现象 → 简化对象 → 过程图 → 物理量 → 规律图示 → 考点标签
→ 错误分支 → 母题模型 → 条件变式 → 总结路线
```

## Physics Narration Cycle

Organize each short explanation as:

```text
问 → 察 → 释 → 验 → 收
```

1. ask for a prediction or judgment;
2. direct attention to the current object, process, force, graph, quantity, or evidence;
3. explain the physical meaning in plain language;
4. verify with a formula, graph, experiment, counterexample, unit, direction, or boundary case;
5. compress the result into a formal conclusion or reusable method cue.

Do not use “显然” or “很简单” to dismiss a genuine learning obstacle. When a formula appears, state the object, process, direction convention, quantity meaning, and applicability condition.

## Planning Contract

### `content-design.md`

Record:

- primary route and optional secondary route;
- core question and core model/law;
- prerequisites, assumptions, reference frame, and direction convention;
- at most two assessment points with recognition signals and scoring actions;
- the primary difficulty and why the incorrect intuition feels plausible;
- errors, misconceptions, conflict evidence, and correction cues;
- mother-problem source, selection reason, model path, and result checks;
- the single-condition variation and whether the model remains valid;
- scene-to-scene object, conclusion, and visual-continuity plan.

### `storyboard.md`

For every scene, record:

- scene id and teaching stage;
- teaching purpose and current question;
- object, result, or visual anchor inherited from the previous scene;
- physical state and visual change formed in this scene;
- assessment, difficulty, or misconception tag when applicable;
- narration cues and pause;
- causal bridge to the next scene;
- component and source material.

### `口播稿.md`

Keep scene ids and stable `visualCueId`/`stepId` values. Multiple narration cues may explain one unchanged visual step. Narration, subtitle, formula, and diagram must describe the same state. Use the authored cue to drive the corresponding Remotion frames; a formula, conclusion, vector, graph state, or answer step must not appear before its explanatory cue.

## Fallback Rules

### Ambiguous Route

Choose the route from the primary learning goal. If the goal is understanding a law, experimental evidence may support a concept/law route without turning the lesson into an experiment/inquiry route.

### Excessive Content

Split the lesson when it contains independent models, more than two assessment points, or unrelated mother problems. Do not skip modeling or reasoning to fit a target duration.

### No Suitable Source Problem

Create a complete, solvable problem and label it `本课设计母题`. Verify the conditions, solution, units, directions, boundaries, and physical meaning independently.

### No Reliable Experimental Data

Do not fabricate evidence. Use a qualitative demonstration, theoretical reasoning, or clearly labeled illustrative data, and state that illustrative data does not reproduce a measurement.

### Simulation Disagrees With Physics

The verified law and calculation take priority. A simulation is an explanatory tool: deterministic, frame-controlled, reproducible, and checked at representative frames and boundary conditions.

### Variation Changes The Core Model

Move it to a follow-up lesson. A near-transfer variation must preserve the core model while changing one meaningful condition.

## Physics QA

### Content

- One core model or law is unmistakable.
- The assessment points, difficulty, error points, misconceptions, mother problem, and variation are explicit.
- The law includes meaning, evidence, formal expression, formula, and applicability conditions.
- The mother problem completes modeling, solution, correction, and checking.

### Teaching

- Students know the lesson question and route within the opening minute.
- Understanding is built before assessment transfer.
- Every abstract idea has a phenomenon, diagram, graph, experiment, or model.
- Every corrected misconception shows why it fails.
- The variation changes one condition only.
- Students can restate the model and problem-solving path after the closing.

### Physics Accuracy

- Object, process, reference frame, direction convention, and assumptions are clear.
- Formula conditions, vector directions, signs, graph meanings, and units are correct.
- Experimental conclusions do not exceed the evidence.
- Results are checked by relevant physical criteria.
- Simulations are deterministic and reproducible.

### Visual And Transition

- One frame has one primary focus.
- The current assessment point is identifiable within three seconds.
- The core law is recovered during formation, application, and review.
- Every adjacent scene has a semantic or visual bridge.
- Formula, diagram, highlight, narration, and subtitle remain synchronized.
- Start, middle, and fully revealed states have no overlap or clipping.
- Subtitles match the spoken cue verbatim, remain within at most two rendered lines, and do not cover physical labels.
- Silent viewing still reveals the reasoning path.
