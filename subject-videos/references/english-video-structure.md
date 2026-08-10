# English Course Video Structure

Use this reference for high-school English videos whose main learning loop is listening, shadowing, noticing language, and speaking. Keep the structure content-driven; the three parts are a reusable route, not three fixed lesson lengths or three mandatory page counts.

## Contents

1. [Learning format](#learning-format)
2. [Vocabulary and phrase route](#vocabulary-and-phrase-route)
3. [Three-part route](#three-part-route)
4. [Build independently, then merge](#build-independently-then-merge)
5. [Script and subtitle contract](#script-and-subtitle-contract)
6. [Narration handoff](#narration-handoff)
7. [Visual and motion rules](#visual-and-motion-rules)
8. [Validation checklist](#validation-checklist)

## Learning Format

Prefer a listenable, repeatable, content-first video over a conventional lecture. Use the narration script to model English, give a short explanation, leave thinking or repeating time, and return the learner to a usable sentence.

Keep these defaults unless the user requests another format:

- Use English for page copy and narration script text.
- Render bilingual subtitles: exact English on the first line and a natural Chinese translation on the second line.
- Explain vocabulary in context: word, meaning, useful chunk, and example.
- Explain grammar quickly through contrast, examples, and a short retrieval prompt.
- Ask a question before revealing an answer or model sentence.
- Keep shadowing and speaking pauses intentional. During a pause, hold the meaningful sentence or chunk on screen.
- Use large typography and a simple content-first layout. Avoid dense courseware chrome, decorative cards, and long teacher monologues.

## Vocabulary and Phrase Route

Use this route when the source or request focuses on a unit's core vocabulary and core phrases rather than the complete English course structure. It is a dedicated learning route, not a shortened version of reading, shadowing, and spoken output.

### Route selection and scope

- Inventory the complete source scope before designing scenes: all core vocabulary, all core phrases, explicitly included supplementary vocabulary or chunks, relevant derivatives or word-family forms, and required collocation/form variants.
- Treat the source scope as the coverage boundary. Do not silently drop a word because it is repetitive, easy, or part of a word family. Related forms may share a visual explanation, but every required form must have an explicit meaning, form, or usage check.
- Build a coverage matrix with at least `itemId`, `itemType`, `sourceSection`, `primaryModule`, `meaningCue`, `collocationOrFrame`, `contrastCue`, `retrievalCue`, and `mixedReviewCue`.
- Give every item one primary module. Add cross-links for polysemy, word families, or phrases that connect two modules, but do not duplicate a full explanation without a learning reason.

### Semantic module boundary

Do not group by word-list order, alphabetical order, or isolated Chinese translation. A semantic module is bounded by:

> `scene + communicative function + usage frame`

Use a module when the items can appear in a coherent micro-situation, support a shared expressive task or language behavior, and fit one complete practice loop. The module title should use `typical scene + communicative task + language handle`, for example “course choices and joining activities: expressing recommendation, choice, and sign-up”.

Split a proposed module when the items only share a broad topic but need different situations, sentence frames, or error checks. Merge modules only when the merge strengthens a common scene or retrieval task and does not overload the learner.

The five Unit 1 groupings are examples, not a universal taxonomy. Other chapters may produce modules about training and competition, problems and solutions, travel planning and experience, scientific phenomena and evidence, or health habits and advice. The reusable rule is the boundary test, not the module name.

### Module contract

Each module must contain the following sequence:

```text
context trigger
→ vocabulary network
→ item explanation
→ collocation and sentence frame
→ contrast/error check
→ immediate retrieval
→ contextual transfer
→ module checkpoint
```

Keep the load manageable. As a default planning range, use 6–10 core words, 3–6 phrases, and one or two word-family or contrast groups per module. These are planning ranges, not mandatory counts; split or merge according to source coverage and teaching density.

For each word, cover:

1. the meaning in the module's situation;
2. part of speech and useful form or word family;
3. a high-value collocation;
4. a sentence frame and natural example;
5. one likely error or contrast;
6. one active retrieval prompt.

For each phrase, cover:

1. the whole-chunk meaning;
2. the structure and replaceable slots;
3. the typical situation;
4. one complete sentence frame;
5. one completion, choice, transformation, or short production task.

### Learning loop and recycling

Every module must move through three levels of practice:

| Level | Typical forms | Purpose |
|---|---|---|
| Recognition | meaning match, picture or situation choice, form identification | confirm initial understanding |
| Retrieval | Chinese-to-English recall, cloze, phrase completion, form choice | strengthen active memory |
| Transfer | scenario choice, sentence transformation, micro-dialogue, short advice or response | make the item usable |

Each item should reappear at least three times: first in the triggering context, immediately after explanation, and later in mixed review. Do not place all review at the very end and assume a single answer-key screen is enough.

### What this route deliberately omits

Do not force the full reading, shadowing, or spoken-output section into a vocabulary-and-phrase lesson. Omit long reading passages, a dedicated shadowing chapter, extended listening input, an independent speaking chapter, and full writing tasks unless the user explicitly asks for them. Keep only short sentence-level application and contextual transfer that are necessary to turn the target words and phrases into usable English.

The route still needs a cover, a short goal/diagnostic, a visual map, module checkpoints, mixed retrieval, and a closing recap. It does not need the three chapter pages used by the general three-part route.

### Recommended episode packaging

Do not compress complete unit coverage into one short file when that would remove retrieval or transfer. Prefer:

```text
unit vocabulary map and diagnostic
→ semantic module 01
→ semantic module 02
→ semantic module 03 ...
→ mixed retrieval and integrated challenge
```

Keep each semantic module independently previewable and testable. If the user requests one final video, merge the modules after their content, cue ids, and durations are validated. Let the actual inventory and learning loop determine the duration; never pad a fixed target or omit items to meet it.

## Three-Part Route

Design three independently testable parts. Adapt the number of scenes and cues to the source text.

### Part 01 — Input and Shadowing

Build understanding from a short context, text, dialogue, or listening passage.

Recommended route:

1. Hook with a real question or situation.
2. Present the passage or key sentences one cue at a time.
3. Shadow high-value sentences by meaning chunks: listen, pause, repeat.
4. Use a short retrieval, fill-in, or retelling task.
5. Close with one transfer prompt.

Keep the spoken model visible during the repeat pause. Do not advance the visual state merely because a cue has ended.

### Part 02 — Language in Context

Turn the same or a closely related passage into rapid vocabulary and grammar noticing.

Recommended route:

1. State the language goal with a compact example.
2. Revisit sentences containing the target language.
3. Explain vocabulary through meaning, collocation, and an example sentence.
4. Compare grammar forms that students commonly confuse.
5. Ask short completion or correction questions.
6. Close by previewing the speaking task.

Avoid isolated word lists. Keep the sentence context visible whenever a word or pattern is explained.

### Part 03 — Spoken Output and Review

Move from comprehension to useful English production.

Recommended route:

1. Present a relatable problem or decision.
2. Model a short dialogue or a set of useful responses.
3. Shadow the highest-value advice or response chunks.
4. Explain only the grammar needed to produce the response.
5. Give several prompts: speak first, then reveal or confirm a model.
6. Review the unit routine and one reusable speaking frame.

Do not turn the final part into a silent answer key. Leave time for the learner to speak before the model appears.

## Build Independently, Then Merge

Keep one project directory for the final lesson unless separate deliverable directories are requested. Inside the project, author three independent episode data sets or compositions first.

For each part:

- Give every scene a stable prefix such as `e1-`, `e2-`, or `e3-`.
- Give each part its own local cover, hook, core scenes, practice, and closing while authoring.
- Keep each part independently previewable and testable with its own scene order, cue ids, and duration.
- Render at least one still from the part's cover, densest content scene, and closing before merging.

Create the final master only after the three parts are coherent. The canonical sequence is:

```text
unit-cover
chapter-01
part-01 content without its local cover
chapter-02
part-02 content without its local cover
chapter-03
part-03 content without its local cover
```

Merge rules:

- Make `unit-cover` a complete first frame. Do not fade from black into a blank or partially populated page.
- Give each chapter page its own stable id (`chapter-01`, `chapter-02`, `chapter-03`), title, part number, learning route, and bilingual cue.
- Remove the three local episode covers from the master sequence; keep them available for independent previews if useful.
- Build one master narration/subtitle cue list in exactly the same order as the master scene list.
- Expose one final master composition by default. Keep the individual part compositions only when they help authoring, testing, or the user explicitly wants separate exports.
- Recompute all global starts, chapter preview frames, progress, and total duration after the merge. Never add independently rounded episode durations to create the master timeline.

## Script and Subtitle Contract

Create `口播稿.md` for the human-readable script and a machine-readable cue list for scene and subtitle planning. Do not put bilingual labels into the English narration text.

For the English route, each cue should carry:

```json
{
  "id": "e1-shadow-01",
  "scene": "e1-shadow",
  "textEn": "Going from junior high school to senior high school is a really big challenge.",
  "subtitleZh": "从初中升入高中是一个很大的挑战。",
  "tone": "listen, pause, repeat",
  "pauseIntent": "repeat the sentence",
  "visualCueId": "e1-shadow-01"
}
```

Rules:

- Keep `textEn` as English-only narration text. Never include `EN:`, `中:`, Markdown markers, or Chinese translation in it.
- Render `textEn` as the first subtitle line and `subtitleZh` as the second line. The English subtitle must equal the authored English text: `subtitleEn === textEn`.
- Keep the complete English subtitle within two rendered lines at the final safe width. Split the cue before the layout boundary when it would exceed two lines.
- Bind every cue to a real scene and stable visual cue. Multiple cues may share one visual state during explanation or a shadowing pause.
- Keep cue ids stable when the script or scene data is revised.

## Narration Handoff

This skill ends at the validated script, subtitle, and visual-cue plan.

- Do not select a speaker, call a synthesizer, generate audio files, create an audio timeline, or attach audio to the Remotion composition here.
- If narration audio is requested, pause and ask the user to confirm the separate voiceover skill and its additional process.
- Hand off cue ids, scene ids, English text, Chinese subtitle translations, visual cue ids, and pause intent. The separate process may return approved timing data later; until then, keep the visual timeline based on authored cue data.

## Visual and Motion Rules

- Keep the global cover and chapter pages simpler than teaching boards. Use a large title, part number, short learning route, and a bilingual bottom cue.
- Keep page text English-only except for the Chinese subtitle line.
- Prefer one dominant visual focus per scene: one sentence, one word/chunk, one grammar contrast, or one speaking prompt.
- Use Remotion frame-driven fades, cue switches, chunk highlights, and answer reveals. Do not use CSS animations or internal playback loops.
- Align a sentence highlight, vocabulary card, grammar reveal, or answer model to the authored cue that explains it.
- Keep the bottom subtitle band in the safe area and verify that it does not cover the main English teaching content.
- Render long vocabulary, grammar, and speaking prompts at actual resolution; never solve overflow by shrinking all typography.

## Validation Checklist

Before declaring the English video complete:

- For the vocabulary-and-phrase route, confirm the coverage matrix contains every source-scope item and every item has a primary module, explanation cue, immediate retrieval cue, and mixed-review cue.
- For the vocabulary-and-phrase route, confirm every module passes the semantic boundary test: coherent micro-situation, shared communicative function or usage frame, manageable load, and a complete recognition → retrieval → transfer loop.
- For the vocabulary-and-phrase route, confirm every word has meaning, form, collocation, example, contrast/error cue, and active retrieval; confirm every phrase has chunk meaning, structure, slots, sentence frame, and a use task.
- For the vocabulary-and-phrase route, confirm no full reading, dedicated shadowing, independent spoken-output, or full writing section was added unless the user explicitly requested it.
- Confirm the three independent parts pass their own tests and still-frame checks.
- Confirm the master begins with `unit-cover` at frame 0 and contains exactly three chapter pages.
- Confirm local episode covers are absent from the master sequence.
- Confirm every cue scene id exists, cue ids are ordered, and English text contains no Chinese or Markdown labels.
- Confirm `subtitleEn === textEn` for every cue and the Chinese translation is present for every screen cue.
- Confirm every subtitle stays within two rendered lines and no key text overlaps the subtitle band.
- Confirm shadowing and speaking pauses hold the intended visual state.
- Confirm the master scene/cue order and total frames use one consistent authored timeline.
- Confirm no audio-generation or speaker-selection step is included in this skill; request the separate voiceover process only after user confirmation.
- Run project tests, typecheck/lint, and `npx remotion compositions src/index.ts`.
- Render frame 0, all chapter starts, representative dense cues, and the final frame.
