# Teaching Script

Create `口播稿.md` after the knowledge analysis and video structure have been designed.

For `学科=语文`, read `chinese-video-structure.md` first. It controls module decomposition, evidence units, formal theme/core-idea placement, genre routes, and real worked-example transfer. This file controls narration tone, reading delivery, cue size, pauses, and script-to-timeline consistency.

## Length

The script length should be determined by the actual content, not by a fixed duration target. As a soft reference:

- 2-3 minutes: about 400-700 Chinese characters plus pauses, suitable for a focused single concept or short reading.
- 5 minutes: about 900-1200 Chinese characters plus pauses.
- 8-12 minutes: about 1800-3200 Chinese characters plus pauses.
- 15 minutes: up to about 4200 Chinese characters plus pauses.

Do not add filler or stretch the script just to reach a duration. Each scene should have matching narration and visual explanation; remove or shorten scenes that would otherwise become blank停留.

## Tone

Write like an experienced high-school teacher:

- warm, clear, and calm;
- light, pleasant, and lively, so the lesson feels enjoyable instead of stiff or沉闷;
- professional, mature, knowledgeable, and able to guide students from shallow understanding to deeper reading or reasoning;
- ask questions before revealing rules;
- explain why a method works;
- give students thinking time;
- connect informal understanding to formal notation;
- use examples and exercises as teaching turns.
- sound like the teacher is teaching a class, not reading a prepared article.
- use comparison, analogy, concrete examples, counterexamples, and step-by-step拆解 when they make the knowledge easier to understand.

## Course Energy

All subject videos should feel brisk, friendly, and intellectually enjoyable:

- Open with a small hook, question, phenomenon, contradiction, image, or relatable scene before entering formal knowledge.
- Keep explanations conversational but precise; use short turns such as “先别急着背”, “我们换个角度看”, “这一步很关键”, or “你会发现”.
- Alternate explanation, observation, question, reveal, and mini-summary so the pacing does not become a one-way lecture.
- Use light humor or gentle curiosity only when it supports learning; do not make the teacher childish, noisy, or unserious.
- Give students a sense of progress: after each small concept, show what problem they can now solve or what misunderstanding they can now avoid.

## Chinese Reading Opening

For Chinese lesson videos (`学科=语文`), if the source text or selected excerpt is not too long, start with an overall expressive reading before formal explanation.

Rules:

- Match the reading tone to the genre and emotion: lyrical and measured for prose, rhythmic and image-rich for poetry, clear and slightly formal for classical Chinese, steady and logical for argumentative texts, vivid and suspenseful for narratives or novels, concise and objective for expository or practical texts.
- The reading is not filler. It should help students quickly form a whole-text impression: topic, scene, rhythm, emotion, and basic atmosphere.
- Keep the reading brief when the text is long: select the most representative paragraph, stanza, or key passage instead of reading everything.
- After reading, immediately guide students into a first question, such as “这段文字最先让我们感到什么？” “作者真正想写的是人、景，还是情？” “这篇文章想说服我们相信什么？”
- In `storyboard.md`, mark the reading scene separately as `整体朗读/片段朗读`, with matching visual design such as text spotlight, line-by-line reveal, imagery background, or annotation-free reading mode.

## Chinese Reading: Answer Transfer and Classical Quotes

### 答题迁移

For Chinese videos that teach exam-answer transfer, follow the complete worked-example contract in `chinese-video-structure.md`. Use a real source/exercise/exam problem when available or a clearly labeled lesson-created complete problem. Show the full prompt, task parsing, evidence location, reasoning, answer construction, and score check. When substantively different approaches exist, teach their different entry points and show how valid points combine into the final answer.

Do not end with a vague method summary or a template without a solved problem. The example should appear in `storyboard.md` and `口播稿.md` as paired narration/visual steps; one complex example may require several scenes and several cues.

### 经典名句

When the source text cites a classical work (经典), the video must:

- show the exact quote, not just a paraphrase;
- state the classical source if known (e.g., 《论语·学而》);
- explain the citation context: what concept the quote supports and how the author uses it in the argument.

Keep the quote on screen long enough to be read, and bind the highlight to its spoken subtitle/audio segment.

## Screen Text Structure

Design on-screen text separately from narration. The board should help students see structure, not transcribe everything the teacher says.

Use this screen-text hierarchy:

- primary focus: one quote, one question, one conclusion, one diagram, or one answer step;
- annotations: keywords, short margin notes, arrows, cause/effect labels, emotional turns, or method labels;
- route map: the current learning path, such as `结构 -> 意象 -> 情感 -> 手法 -> 答法`;
- subtitle: the exact spoken text, split before TTS into short timed segments that render in at most two lines.

For Chinese videos, avoid generic pages like “课文简介 + 中心思想 + 写作手法” as the main visual structure. Prefer genre-specific routes and evidence-based boards: selected text, evidence labels, interpretation paths, theme formation, weak/strong answer contrast, and complete worked-example solution paths.

## Physics Narration Cycle

For `学科=物理`, read `physics-video-structure.md` first. Organize each short explanation as `问 → 察 → 释 → 验 → 收`:

1. ask for a prediction or judgment;
2. direct attention to the current object, process, graph, force, quantity, or evidence;
3. explain the physical meaning in plain language;
4. verify it with a formula, graph, experiment, counterexample, unit, direction, or boundary case;
5. compress it into a formal conclusion or reusable method cue.

When a formula appears, identify the object, process, direction convention, quantity meaning, and applicability condition. In a mother problem, narrate what the current step does, why it is valid, and where students commonly go wrong. Use causal bridge sentences between scenes instead of mechanical announcements.

## Script-To-Timeline Contract

- Write the script in the same scene order as `storyboard.md` and the composition timeline.
- Give each teaching scene multiple subtitle-sized narration segments. Each complete verbatim cue may render in at most two lines; one static subtitle for an entire scene is not acceptable.
- Store a stable scene id on every cue. Test that the scene exists and that `scene.from <= cue.start < cue.end <= scene.from + scene.duration`.
- For worked examples, create one or more cues for every visible semantic step. The cue must explain the formula, reason, or warning currently highlighted on screen.
- Keep the full teacher explanation in `口播稿.md`; split it into spoken cues and use each cue verbatim as its subtitle. Require `subtitle === text`; never summarize, shorten, omit, paraphrase, or rewrite the spoken wording, and do not let the subtitle introduce a conclusion before the board has reached it.
- Prefer one rendered line when the complete cue fits. If a cue would exceed two rendered lines at the approved font size and safe width, split the spoken sentence at a semantic boundary and assign separate measured timeline ranges.
- Update `口播稿.md`, `storyboard.md`, cue data, scene durations, and visual step boundaries together when content expands or contracts.
- Once audio exists, use `measured audio cue -> subtitle cue -> visualCueId/stepId -> Remotion frame state` as the canonical timing chain. A visual conclusion must not appear before the cue that speaks it, and the active visual step must advance with the measured narration unless consecutive cues intentionally share one stable visual id.

### Remotion Frame Coordinates

`useCurrentFrame()` inside a `<Sequence>` returns a scene-local frame. Do not use it directly to query a global subtitle table or draw a global progress bar.

Choose one consistent pattern:

1. Convert local frame to global frame with the scene start before querying global cues; or
2. Store cues in scene-local coordinates and query only the current scene's cues.

Add tests for cue containment and scene continuity. During silent gaps, hold the latest meaningful state from the same scene; never fall back to a cue from the previous scene.

## Pause Markers

Use visible pause markers in the script:

```text
（停顿 2 秒，给学生观察图）
（停顿 3 秒，先让学生自己判断）
（板书停顿）
```

## Structure

Use this outline unless the source requires a different order:

1. 开场定位：本节解决什么问题，为什么重要。
2. 旧知连接：学生已经知道什么。
3. 核心概念：用通俗语言解释。
4. 结构图讲解：带学生读图，不只是展示图。
5. 方法流程：遇到题目怎么想、怎么做。
6. 例题精讲：审题、转化、步骤、检查。
7. 易错提醒：错在哪里，如何避免。
8. 练习题点拨：选择典型题讲思路。
9. 收束复盘：用 3-5 句话总结本节。

For a worked-example explanation, cover all of these turns unless the problem genuinely does not need one:

1. Restate the task and interval/domain.
2. Explain why the chosen method fits.
3. Show each algebraic or logical transformation.
4. State the condition used to determine each sign or branch.
5. Translate the intermediate result back to the definition or theorem.
6. Identify the most likely wrong step and show how to avoid it.

For Chinese videos, do not use this generic outline as a scene list. Use the flexible seven-module arc and genre route in `chinese-video-structure.md`, then split modules according to the actual article, evidence, real example, and learning goal. The teaching should not feel like a generic “课文简介 + 中心思想 + 写作手法”; it should show a mature teacher leading students through reading, evidence-based interpretation, formal theme/core-idea formation, method extraction, and answer transfer when relevant.

## Avoid

- Do not write a dense encyclopedia-style explanation.
- Do not rush from definition to conclusion without student thinking time.
- Do not only repeat screen text.
- Do not make it sound like an advertisement or course trailer.
- Do not follow the source file paragraph by paragraph unless that order is truly the best teaching order.
- Do not simply paraphrase or朗读 the provided file.
- Do not sound like a dull textbook recitation, a lifeless classroom reading, or a mechanically serious lecture.
- Do not keep the same rhythm for several minutes; vary sentence length, questions, pauses, examples, and reveals.
