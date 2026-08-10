---
name: subject-videos
description: Create high-school subject knowledge-point lecture videos as Remotion projects. Use when the user asks to make 学科视频, 知识点讲解视频, Remotion 学习视频, 核心精讲版 videos, teacher-style narration scripts, or 1920x1080 educational video projects under the project video directory, including English listening, shadowing, vocabulary, grammar, speaking, bilingual-subtitle, or three-part-build-then-merge workflows.
---

# Subject Videos

## Overview

Create one Remotion video project for one high-school knowledge-point file. The output is a 1920x1080 horizontal core-lecture project, a teacher-like narration script, a bilingual subtitle/cue plan when needed, and a silent Remotion composition. Audio generation and audio attachment are outside this skill.

Always use `$remotion-best-practices` as the core Remotion implementation guide before writing or editing Remotion code.

If the user asks to update the skill itself after a project-level improvement, extract only reusable video-production rules. Do not write course-specific content, plot points, or subject-matter details into the skill.

## Output Contract

Create video projects under:

```text
video/<学科>/<知识点工程目录>/
```

Rules:

- One knowledge-point file maps to one video project directory.
- Use subject subdirectories such as `video/语文/`, `video/数学/`, `video/物理/`, `video/化学/`, `video/生物/`, `video/地理/`, `video/历史/`.
- Use horizontal `1920x1080`, `30fps`.
- Target duration: `2-15` minutes, determined by the actual content. Do not stretch or pad to reach a fixed length; avoid long blank/idle scenes with no narration or explanation. Each scene should have corresponding teaching content and visual support.
- Create a “核心精讲版”: focused, complete, clear, and suitable for high-school students.
- Include a cover/opening page before the first teaching scene. The cover should establish the course topic and "未开始/即将开始" state briefly, not jump directly into the knowledge explanation on frame 0.
- Build the cover with `references/cover-design.md`: default to a left-side subject/title/range hierarchy and a right-side topic-specific SVG. Make the current core knowledge point the largest white bold text and first visual focus on the frame; keep the subject label, nearest chapter/range, illustration, and course chrome secondary unless the user requests otherwise.
- Include a closing page after the final teaching scene. The closing page should summarize the whole video's learning path, key takeaways, and final method cue instead of ending abruptly on the last content board.
- Create `口播稿.md` for narration/script planning. Do not generate or attach audio in this skill.
- Keep the Remotion source silent in this workflow. If narration audio is requested, hand off only after the user confirms a separate voiceover workflow.
- Assets from notes, images, exercises, and text may be copied into `public/` and referenced with `staticFile()`.
- If the user asks for a high-fidelity 4K deliverable, keep the master timeline and sync unchanged and export an additional `3840x2160` file under `output/`.

## Mathematics Template And Shared Dependencies

When working in this repository, create mathematics lecture projects with:

```bash
python3 scripts/create_math_video.py "<工程目录名>" --composition-id <CompositionId>
```

Apply these repository-specific mathematics rules:

- Derive every new mathematics lecture project from `video/数学/数学视频模板/`. Do not run the generic Remotion scaffold for mathematics in this repository.
- Use the generated relative `node_modules -> ../node_modules` symlink to `video/数学/node_modules`.
- Never run a project-local install that replaces the symlink with a real dependency directory.
- Add new mathematics dependencies to `video/数学/package.json`, retain direct dependency declarations in the consuming project, and keep all Remotion packages on one exact version.
- Keep the real shared dependency directory and every child `node_modules` symlink ignored. Never commit either path.
- Treat `video/数学/` as the only Git repository for mathematics videos. Never initialize or preserve nested `.git` directories in templates or lesson projects.
- Start from the template typography, sizing, background, palette, subtitle, cover, and closing configuration. Design lesson-specific content pages separately; do not add generic content pages to the empty template.
- Use the **data-driven lesson engine** the template already provides. Do not write per-video fat components with hardcoded frame offsets.

  Use `references/math-lesson-engine.md` as the contract. In short:

  - Follow the four-layer architecture: `types/` → `data/` (pure lesson inputs, the single source of truth) → `timeline.ts` (`buildLesson` compiler with a total-frame assertion) → `lessons/*.tsx` (thin wrappers + scene components) → `shared/LessonVideo.tsx` (unified engine).
  - Let `buildLesson` compute every scene start frame and distribute every narration cue from declared durations; never hardcode `FROM`/`HOOK` frame constants inside scene files.
  - Author narration only in `src/data/lesson-inputs.ts`. Generate `口播稿.md` with `node scripts/gen-script.mjs`; never maintain it by hand. The script-sync guard test fails on any drift between data and script.
  - Run `tsc --noEmit && vitest run` and keep the four guard suites green before finishing: CSS animation/transition ban, composition registration, KaTeX formula guard, and 口播稿↔subtitle consistency. The full compiler, schema, engine, and guard-test code live in the `remotion-lesson-video` skill.

## English Video Routing

For `学科=英语`, read `references/english-video-structure.md` before designing the storyboard, script, scene data, or Remotion composition.

### Vocabulary and Phrase Specialization

When the source or request is specifically about core vocabulary and core phrases, use the dedicated vocabulary-and-phrase route. The vocabulary-and-phrase route takes precedence over the three-part English course route below.

- Inventory the full source scope before authoring: all core vocabulary and core phrases, supplementary vocabulary or chunks explicitly included by the source, relevant word families, and required collocation/form variants. Give every learning object one primary semantic module and keep a coverage matrix linking it to explanation, practice, and review cues.
- Divide content by `scene + communicative function + usage frame`, not by word-list order, isolated Chinese meaning, or fixed textbook page order. A semantic module must be coherent as a micro-situation, share an expressive task or usage pattern, and fit a complete learning loop.
- Use the module loop `context trigger → vocabulary network → item explanation → collocation and sentence frame → contrast/error check → immediate retrieval → contextual transfer → module checkpoint`.
- Include recognition, active retrieval, and transfer in every module. Recycle each learning object at initial exposure, immediate practice, and later mixed review.
- For each word, explain core meaning, part of speech, useful collocation, sentence frame, one error point, one natural example, and one active retrieval task. For each phrase, explain whole-chunk meaning, structure, replaceable slots, typical context, sentence frame, and a production task.
- Do not force the full reading, shadowing, or spoken-output section into a vocabulary-and-phrase lesson. Do not add long listening input, shadowing pauses, independent speaking chapters, or full writing tasks unless the user explicitly requests them. Keep only short sentence-level application and contextual transfer needed to make the vocabulary usable.
- Treat module names as content-dependent. Use `typical scene + communicative task + language handle`; do not hard-code the five Unit 1 example modules as a universal taxonomy.
- Keep each module within a manageable load, normally 6–10 core words, 3–6 phrases, and one or two word-family or contrast groups. Split or merge only after checking semantic coherence, training completeness, and cognitive load.
- Prefer a module series plus a final mixed-retrieval episode when all unit vocabulary cannot be taught and recycled well in one short file. Duration is driven by the inventory and learning loop, not by the default 2–15 minute target.

### General English Course Route

For English lessons whose main goal is listening, shadowing, language noticing, and spoken output, use three independently authored parts: input and shadowing, language focus in context, and spoken output and review. Build and validate the three parts independently first, then merge them into one final master composition with a complete unit cover and one chapter page before each part. The final master should expose one complete composition unless the user explicitly requests separate episode deliverables.

English-specific defaults:

- Use English-only narration/script text and English for page text; render bilingual subtitles with English on the first line and Chinese on the second line.
- For the general course route, use short listening, shadowing, quick vocabulary-in-context, grammar-noticing, speaking, and retrieval cues instead of a long conventional lecture. For the vocabulary-and-phrase route, use micro-contexts, semantic modules, item-level explanation, contrast, retrieval, and transfer instead of shadowing or an independent speaking section.
- Use `unit-cover` as the complete first frame, then `chapter-01`, `chapter-02`, and `chapter-03` before the three content blocks. Do not show a blank frame before the cover.
- Author each part as an independently testable episode data set/composition, then build `COMBINED_EPISODE` (or the project equivalent) by removing local episode covers and inserting the global cover and chapter pages in sequence.
- Do not select a voice, invoke a synthesizer, generate audio files, or update the video timeline from measured audio here. Treat narration audio as a separate, user-confirmed handoff.

## Chinese Template And Shared Dependencies

When working in this repository, create Chinese lecture projects with:

```bash
python3 scripts/create_chinese_video.py "<工程目录名>" --composition-id <CompositionId>
```

Apply these repository-specific Chinese rules:

- Derive every new Chinese lecture project from `video/语文/语文视频模板/`. Do not run the generic Remotion scaffold or copy an existing lesson project for Chinese in this repository.
- Treat `video/语文/语文视频模板/` as the direct implementation baseline for fonts, typography, background, palette, safe areas, subtitle, cover, closing, and motion. `video/语文/01-短歌行/` remains the visual source from which the template was extracted, not the project to clone.
- Keep the template content-neutral. It contains only shared visual infrastructure, the standardized cover, and the standardized closing page. Do not add a generic reading, close-reading, structure, theme, exercise, or answer page to the template.
- Design every lesson's content scenes after analyzing the actual text with `references/chinese-video-structure.md`. The seven Chinese modules are not template pages.
- Use the generated relative `node_modules` symlink to the single real dependency directory at `video/语文/node_modules`. First-level projects use `../node_modules`; nested projects must compute the correct relative target.
- Never run a project-local install that replaces the symlink with a real dependency directory.
- Add new Chinese dependencies to `video/语文/package.json`, retain direct dependency declarations in the consuming project, and keep all Remotion packages on one exact version.
- Keep the real shared dependency directory and every child `node_modules` symlink ignored. Never commit either path.
- Treat `video/语文/` as the Git repository for Chinese videos. Never initialize or preserve nested `.git` directories in the template or lesson projects.
- Configure lesson-specific cover title, scope, reading question, and topic mark; configure the closing theme/core idea, evidence path, and transferable method cue. Do not leave placeholder content in a finished lesson.

## Physics Template And Shared Dependencies

When working in this repository, create physics lecture projects with:

```bash
python3 scripts/create_physics_video.py "<工程目录名>" --composition-id <CompositionId>
```

Apply these repository-specific physics rules:

- Derive every new physics lecture project from `video/物理/物理视频模板/`. Do not run the generic Remotion scaffold or copy an existing physics lesson project.
- Treat the template as the source of truth for Graphite Blue colors, local fonts, typography, background texture, safe areas, subtitle, course chrome, cover, closing, and motion behavior. Read `references/physics-visual-design.md` before designing or editing physics scenes.
- Keep the template content-neutral. It contains only the standardized cover and closing page plus shared visual infrastructure. Do not add generic teaching/content pages or specific concepts, laws, formulas, quantities, examples, or assessment points to the template.
- Configure the generated lesson's title, chapter/range, opening cue, closing route, and takeaway. Do not leave template placeholders in a finished lesson.
- Use the generated relative `node_modules -> ../node_modules` symlink to the single real dependency directory at `video/物理/node_modules`.
- Never run a project-local install that replaces the symlink with a real dependency directory. Add shared physics dependencies at `video/物理/`, retain direct dependency declarations in the consuming project, and keep all Remotion packages on one exact version.
- Keep the real shared dependency directory and every child symlink ignored. Never preserve dependency backups such as `node_modules.local-backup` or `_node_modules_backups` after migration verification.
- Do not initialize or copy nested `.git` directories into the template or generated lesson project.
- Run tests, typecheck/lint, and `npx remotion compositions src/index.ts` for IDE/Remotion loading validation. Do not render unless the user explicitly asks; a request for a render command authorizes only returning the command.

## Workflow

1. Read the source knowledge-point file and identify subject, chapter, core concepts, examples, exercises, and available images.
2. Read `references/content-design.md`, `references/project-structure.md`, `references/visual-system.md`, `references/cover-design.md`, `references/teaching-script.md`, and the relevant subject section in `references/subject-components.md`. For `学科=英语`, also read `references/english-video-structure.md` before designing content, the three independent parts, storyboard, narration, or Remotion scenes. For `学科=语文`, also read `references/chinese-video-structure.md` and `references/chinese-visual-design.md` before designing content, storyboard, narration, or Remotion scenes. For mathematics, also read `references/math-video-patterns.md` before designing formulas, graphs, or logic-comparison pages. For `学科=物理`, also read `references/physics-video-structure.md` and `references/physics-visual-design.md` before designing content, assessment emphasis, misconceptions, the mother problem, storyboard, narration, Remotion scenes, or project scaffolding.
3. Use `$remotion-best-practices` before creating or editing Remotion code.
4. Create or scaffold the project directory:
   - For mathematics in this repository, run `python3 scripts/create_math_video.py "<工程目录名>" --composition-id <CompositionId>` and keep its shared dependency symlink intact.
   - For Chinese in this repository, run `python3 scripts/create_chinese_video.py "<工程目录名>" --composition-id <CompositionId>` and keep its shared dependency symlink intact.
   - For physics in this repository, run `python3 scripts/create_physics_video.py "<工程目录名>" --composition-id <CompositionId>` and keep its shared dependency symlink intact.
   - For subjects other than mathematics, Chinese, and physics, use `scripts/init_subject_video.py` to create the directory and starter planning files.
   - For subjects other than mathematics, Chinese, and physics with no Remotion app yet, run `npx create-video@latest --yes --blank --no-tailwind <project-dir-name>` inside `video/<学科>/`, then adapt it.
   - For English, keep the selected route inside one project directory unless separate project deliverables are requested. For the general course route, keep the three independently authored parts and expose or preview them while authoring; for the vocabulary-and-phrase route, keep semantic modules independently previewable and expose only the merged master by default after the route is validated.
5. Create the knowledge analysis and video content design first. Do not convert the source file directly into narration.
6. Write `storyboard.md` with time ranges, teaching purpose, visual effect design, source material, and Remotion component names.
7. Write `口播稿.md` from the designed teaching structure and storyboard, not by reading the source file line by line.
   - Give every teaching scene multiple short narration/subtitle cues.
   - Write each narration cue at subtitle-sized semantic granularity. Subtitles may use at most two rendered lines and should use one line when the complete verbatim cue fits.
   - If one narration thought exceeds two rendered lines at the approved font size and safe width, split it at a semantic boundary into consecutive cues before any later voiceover handoff. Do not replace a long teaching thought with a shorter summary subtitle.
   - Assign every cue to a scene and keep its range inside that scene.
   - Align worked-example visual steps with the cue that explains the same step.
8. If the user asks for final narration audio, pause after the script and bilingual subtitle/cue plan are validated. Confirm the separate voiceover skill and its additional process before any audio action. This skill does not select voices, invoke a synthesizer, generate audio files, or derive timing from audio.
9. Build the Remotion composition:
   - define the composition in `src/Root.tsx`;
   - use `1920x1080`, `30fps`, and duration in frames;
   - implement scenes as frame-driven React components;
   - implement the shared visual system before subject-specific scenes;
   - For `学科=数学`, do not hand-write fat per-video components. Derive the project from the math template and use its data-driven engine: author lesson data in `src/data/lesson-inputs.ts`, let `buildLesson` compute the timeline, register the composition in `src/Root.tsx`, and run `tsc --noEmit && vitest run` (see `references/math-lesson-engine.md` and the `remotion-lesson-video` skill).
   - keep theme, layout, subtitle, progress, scene transition, and motion timing consistent with `references/visual-system.md`;
   - copy required images to `public/`.
10. Validate with Remotion:
   - run typecheck or lint if available;
   - render at least one still frame when practical;
   - inspect that text fits and key diagrams are readable.
   - render the start, middle, and end of formula-, proof-, graph-, and text-dense scenes;
   - check that visible formula commands render as symbols, not words such as `Rightarrow`, `quad`, or `dfrac`;
   - check narration/subtitle cue text against the current visual step rather than only checking scene-level timing.
11. Do not perform audio generation or audio-stream validation in this skill. The separately confirmed voiceover workflow owns those checks.
12. If the user reports a page-level issue, reproduce it with still frames or a final render check, fix the exact scene, then re-render the deliverable if an output video already exists.
13. If the user requests 4K, export the 4K deliverable after the approved master version is stable.
14. Finish with paths, duration, status, and any skipped validation.

## Formula, Logic, And Data Visualization Rules

Apply the following rules whenever a lesson uses formal notation, symbolic transformations, graphs, tables, or a multi-condition judgment:

- Render mathematical expressions, domains, sets, intervals, equations, inequalities, and derivations with KaTeX. Do not use plain Unicode approximations such as `√x`, `x²/x`, or `D=R` in a formula board.
- Keep a formula's original domain visible when simplification could hide a restriction. Treat an algebraic simplification and a function identity as separate claims.
- For comparisons requiring several conditions, give each condition its own visible check and give the final conclusion separately. Do not collapse multi-step reasoning into one ambiguous “correct/incorrect” badge.
- Store worked-example cases and verdicts as typed data, then render from that data. Add a focused test for the rule or derivation before implementing a corrected logic page.
- Store each worked-example step with at least `formula`, `reason`, and `detail`/`warning`; do not show a formula without explaining why the transformation and sign judgment are valid.
- In TSX formula props, use a safe LaTeX string form such as `String.raw` when commands contain backslashes. In TypeScript data strings, escape commands correctly or use `String.raw`. Render a still to catch commands displayed as plain text.
- Use SVG for diagrams and graphs. Use D3 for scales, axes, and deterministic path construction; use Math.js to parse/sample expressions when graphing an expression; use KaTeX for every associated formula.
- Drive all reveals, emphasis, line drawing, graph-domain exposure, and card focus from Remotion frames. Bind explanation-state changes to authored subtitle/cue data rather than stale fixed frame offsets.
- Remember that `useCurrentFrame()` inside `<Sequence>` is scene-local. Convert it to the centralized global frame before looking up global subtitle cues or global progress, or store cues scene-locally and keep the coordinate system consistent. Add a test that every cue belongs to a real scene and stays within its boundaries.

Use `references/math-video-patterns.md` for the full mathematics component and QA patterns.

## Content Design Rule

Use `references/content-design.md`.

The source file is teaching material, not a teleprompter. Before writing `口播稿.md` or Remotion scenes:

- analyze the knowledge point;
- split it into teaching units;
- identify conceptual obstacles and likely student misconceptions;
- decide the video narrative arc;
- design diagrams, animations, examples, pauses, and exercise moments;
- decide which source text, images, and exercises are useful as materials.

Never simply read, paraphrase, or mechanically summarize the given file in order.

Scene duration must be driven by actual teaching content and narration, not by a fixed target length. Avoid long blank/idle scenes where nothing is explained or animated. If a scene has little to say, shorten it or merge it with the next scene. Every scene should have corresponding narration and visual explanation.

For poetry or classical recitation scenes, the visual pacing should reflect the emotional rhythm: line-by-line reveal, highlighting the current line, and appropriate pauses.

## Scene Structure Requirements

Every video should have a complete viewing arc:

- cover/opening page: brief pre-start state, title, topic cue, subject/unit cue, and calm entry into the lesson;
- opening question or learning hook: move from the cover into the first real teaching problem;
- overview/map scene: reconstruct the knowledge route as a video-native structure;
- core explanation scenes: each scene has one dominant teaching focus, a visible evidence/method path, and matching narration;
- review/misconception scene: summarize traps, corrections, or transfer method when the knowledge point needs it;
- closing page: final learning-path recap and one concise takeaway, with enough time for the last narration and subtitle to finish.

Do not use a source image as a shortcut for the overview. When the source includes an information structure diagram, read it as design input, then rebuild it as animated video structure: cards, nodes, links, routes, timelines, answer paths, or focus states. Directly placing an image in the video is allowed only when it is a genuine visual scene, object, artwork, experiment, map, chart, or illustration that students need to inspect.

### Chinese Subject Routing

For `学科=语文`, use `references/chinese-video-structure.md` as the source of truth for the teaching arc and scene decomposition.

- Treat its seven modules as teaching stages, never as seven scenes, seven pages, or seven Remotion components.
- Split each module into as many concrete scenes as the target text, evidence groups, conceptual obstacles, real examples, and learning goal require; merge or omit optional stages only when the teaching loop remains complete.
- Organize core explanation around visible text evidence rather than separate background, imagery, technique, emotion, and theme inventories.
- Explain the article's theme or core idea after enough evidence has been established. Build local interpretations first, give the formal evidence-backed theme in late close reading or synthesis, then compress it in the closing.
- If method transfer is included, use a real source/exercise/exam question when available or a clearly labeled lesson-created complete question. Show task parsing, evidence location, reasoning, answer construction, and checking. When substantively different solution paths exist, explain their entry points, evidence, trade-offs, and synthesis.
- Use `references/chinese-visual-design.md` for the Chinese background, local fonts, color tokens, literary/teaching typography split, page hierarchy, worked-example layouts, and visual QA. Lesson-specific words and motifs must remain configurable rather than being hard-coded into shared components.

### Physics Subject Routing

For `学科=物理`, use `references/physics-video-structure.md` as the source of truth for the teaching arc and route selection.

- Choose one primary route: concept/law, experiment/inquiry, calculation/method, or phenomenon/mechanism. Add at most one secondary route when it supports the same learning goal.
- Build first-time understanding through phenomenon, model, evidence, law, and conditions before assessment transfer.
- Explicitly teach at most two core assessment points, one primary conceptual difficulty, related error points and misconceptions, and one representative mother problem.
- Revisit misconceptions inside the matching mother-problem step instead of collecting them only on a detached warning page.
- Use a single-condition variation to test whether the model transfers. If the changed condition requires a different core model, route it to another lesson.
- Preserve a question, object, process, conclusion, diagram, or visual position across adjacent scenes so transitions carry the reasoning forward.

## Remotion Hard Rules

- Use Remotion frame control: `useCurrentFrame()`, `useVideoConfig()`, `interpolate()`, `Easing`, and `<Sequence>`.
- Do not use CSS transitions or CSS animations.
- Do not use Tailwind animation classes.
- Do not let embedded libraries run their own playback loops.
- All dynamic visual components must accept props such as `frame`, `progress`, `durationFrames`, `data`, and `theme`.
- For p5.js, Matter.js, Three.js, Rapier, ECharts, Leaflet, MapLibre, OpenLayers, deck.gl, Cytoscape, vis-timeline, Mermaid, 3Dmol.js, Kekule.js, JSXGraph, and similar libraries:
  - initialize deterministically;
  - disable internal autoplay, clocks, timers, requestAnimationFrame-driven progression, or user interaction playback;
  - derive every visible state from Remotion frame/progress;
  - keep rendering deterministic for the same frame.
- Put assets in `public/` and reference them with `staticFile()`.
- Use `<Img>` for images and Remotion media components for media.

## Teaching Script Requirements

Use `references/teaching-script.md`.

The narration script should feel like a senior teacher explaining in class:

- complete knowledge coverage, not a short promo;
- light, pleasant, and lively without becoming childish or unserious;
- clear section transitions;
- short pauses for thinking;
- questions before answers;
- examples and exercises used as learning moments;
- plain language first, formal expression second;
- enough time for students to observe diagrams and reason;
- subtitles must be segmented with the narration cues, not written as a single static line per scene. Every scene should have multiple subtitle changes matching the teaching content.
- for shorter texts, a full expressive read-through may come first, but it still needs cue segmentation and emotional pacing rather than a single text block.

Do not write a fast knowledge announcement. Write a teaching script.
Do not use the source file as a direct read-aloud script. The narration must come from the knowledge analysis and video design.

## Narration Handoff Boundary

Subject-videos owns narration wording and bilingual subtitle/cue planning, not audio production.

- Create and validate `口播稿.md` plus scene-level cue data. Each cue should have a stable id, scene id, English text when applicable, Chinese subtitle translation when applicable, and a visual cue id.
- Do not select a voice, invoke a synthesizer, generate audio files, create speech-marker or audio-timeline files, attach audio to Remotion, or validate audio streams from this skill.
- If narration audio is requested, stop at the validated script/subtitle handoff and ask the user to confirm the separate voiceover skill and its additional process before continuing.
- Keep visual timing deterministic from authored scene/cue data until the separate audio workflow explicitly returns approved timing data.

## Visual Design Requirements

Use `references/visual-system.md` as the baseline for every subject video. All projects should feel like one coherent course series, while each subject keeps its own visual identity and knowledge-diagram language.

- Favor knowledge structure maps, process diagrams, formula derivations, worked-example boards, exercise analysis, timelines, maps, microscopic views, and real-world mechanism diagrams.
- Keep scenes dense enough for learning but readable on 1920x1080.
- Keep the course feeling brisk, pleasant, and engaging: use clean rhythm, friendly emphasis, small moments of curiosity, and clear visual payoff after questions.
- Use existing images from the note when they help understanding.
- Do not make a marketing-style title video.
- Avoid decorative scenes that do not explain a concept, method, mechanism, or evidence path.
- Avoid a dull textbook-recitation classroom style: no lifeless full-page text, no long static boards, no monotonous lecture pacing, and no overly solemn "reading the textbook" tone.
- Keep shared course elements consistent: composition size, subtitle placement, title/progress chrome, scene transition rhythm, typography scale, and frame-driven motion rules.
- Use the dedicated cover rules in `references/cover-design.md`; do not reuse a dense teaching-board layout as the first screen.
- Allow subject-specific differences in background texture, accent palette, diagram style, iconography, and visual metaphor according to `references/visual-system.md`.
- Dense text scenes must be laid out so that body text, annotation text, and subtitle text never overlap. Check multi-column and layered text scenes frame-by-frame where needed.
- Bottom subtitles are capped at two rendered lines in the final render. Prefer one line when the complete verbatim cue fits. If a cue would produce a third line, split the corresponding authored cue at a semantic boundary instead of shrinking the font, widening outside the safe area, clipping text, or showing a summary.
- Avoid clipping hidden text with `overflow: hidden`, tight fixed-height containers, or cards placed too close to scene boundaries. If a scene uses `overflow: hidden` for a framed board, verify every revealed label, node, and annotation remains fully visible at its final state.
- For reading-heavy Chinese scenes, show selected lines, active highlights, and compact interpretation routes. Keep the active line highlighted through the authored cue range.

## Visual QA Requirements

Before considering the video done:

- inspect any scene with dense text, poem/classical recitation, worked-example steps, or layered labels for collisions, overlap, and clipping;
- check that text layers do not occupy the same screen band as bottom subtitles unless intentionally designed and still fully readable;
- verify subtitle line count in the actual render, not only in source data;
- compare every final subtitle cue against the authored English/Chinese cue data and fail validation on any mismatch;
- render the longest subtitle cues and reject any third line, clipping, hidden text, unsafe font shrinkage, or overlap;
- add automated checks for cue ids, scene ids, exact authored text, two-line rendered limit, cue ordering, and scene boundaries;
- verify the final rendered video, not only preview frames, when the user explicitly reports a page-level display issue.
- for reported page issues, render still frames near the start, middle, and end of the relevant narration segment, not just one convenient frame;
- after changing a project that already has an output video, re-render the visual deliverable when the user asks for that update; audio validation belongs to the separate voiceover workflow.

## 4K Delivery Rule

When the user asks for a 4K version:

- keep timing, subtitle sync, and approved content identical to the validated master version;
- prefer exporting from the approved master pipeline or creating a high-quality 4K deliverable from the approved master when that is more reliable and faster;
- place the final file under `output/` with a clear `-4k` suffix;
- confirm final resolution, frame rate, and duration; handle audio validation in the separate voiceover workflow.

## Subject Component Routing

Use `references/subject-components.md` for allowed libraries and patterns.

Required principle: every component is a pure frame-driven visualization controlled by Remotion. Components receive props and render a state for the current frame; they do not “play” by themselves.

## Deliverables

Each project should contain at least:

```text
video/<学科>/<知识点工程目录>/
  content-design.md
  口播稿.md
  storyboard.md
  package.json
  src/
  public/
```

If rendering is completed, place output files under:

```text
video/<学科>/<知识点工程目录>/output/
```

Name the default MP4 after the project directory:

```text
video/<学科>/<知识点工程目录>/output/<知识点工程目录>.mp4
```

For parallel Remotion rendering, pass an explicit `--concurrency=<N>` value appropriate to the machine. If the user asks only for the render command, provide the command without executing it. A compatible H.264 template is:

```bash
npx remotion render src/index.ts <CompositionId> \
  "output/<知识点工程目录>.mp4" \
  --codec=h264 \
  --crf=18 \
  --pixel-format=yuv420p \
  --concurrency=8
```

## Resources

- `references/project-structure.md`: directory and file conventions.
- `references/content-design.md`: knowledge analysis and video structure design rules.
- `references/visual-system.md`: shared course-series visual identity plus subject-specific visual profiles; `video/数学/4.2-指数函数/` (data-driven series) and `video/数学/数学视频模板/` (neutral template) are the mathematics reference implementations.
- `references/math-lesson-engine.md`: the data-driven lesson engine contract for mathematics — four-layer architecture, `buildLesson` timeline compiler, single-source narration, and the four guard suites.
- `remotion-lesson-video` skill: complete, copy-paste-ready compiler/schema/engine/guard-test code and the scaffold steps for the mathematics data-driven architecture.
- `references/cover-design.md`: required first-screen hierarchy, left-right structure, title sizing, subject/range labels, topic-specific SVG, animation, and QA.
- `references/teaching-script.md`: teacher-style narration rules.
- `references/english-video-structure.md`: English route selection, vocabulary-and-phrase semantic modules, complete coverage and retrieval loop, three-part independent build, merge sequence, bilingual subtitle convention, and English-specific QA.
- `references/subject-components.md`: subject-specific animation libraries and frame-driven component constraints.
- `references/math-video-patterns.md`: required mathematics formula, graph, logic-comparison, and visual QA patterns.
- `references/physics-video-structure.md`: physics-only teaching arc, four route types, assessment/difficulty/misconception rules, mother-problem transfer, transitions, and QA.
- `references/physics-visual-design.md`: physics template creation, shared dependency contract, Graphite Blue tokens, background texture, cover/closing baseline, collision prevention, IDE validation, and render authorization boundary.
- `references/chinese-video-structure.md`: Chinese-only flexible teaching modules, evidence units, theme placement, genre routes, real worked examples, and structure QA.
- `references/chinese-visual-design.md`: Chinese-only visual identity derived from `video/语文/01-短歌行/`, including reusable background, fonts, palette, layouts, motion, and visual QA.
- `scripts/create_chinese_video.py` at the workspace root: create a Chinese lesson from `video/语文/语文视频模板/` and link the shared dependencies.
- `scripts/create_physics_video.py` at the workspace root: create a physics lesson from `video/物理/物理视频模板/` and link the shared dependencies.
- `scripts/init_subject_video.py`: create project directory and starter planning files.
