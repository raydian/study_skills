# Mathematics Data-Driven Lesson Engine

When producing a mathematics lecture video in this repository, derive the project from `video/数学/数学视频模板/` through `scripts/create_math_video.py`. That template already implements the **data-driven lesson engine**. This document is the canonical contract for the architecture. The complete, copy-paste-ready implementations (compiler, schema, engine, guard tests) live in the `remotion-lesson-video` skill: `references/timeline-compiler.md`, `references/data-schema.md`, `references/lesson-engine.md`, `references/guard-tests.md`, and `references/scaffold.md`.

The engine exists to fix the failure mode it replaces: hand-written fat components with hardcoded frame offsets. Once any scene duration changes, the old approach silently desynchronizes every later scene and the subtitle track. The engine makes that a compile-time error.

## Four-Layer Architecture

```text
src/types/lesson.ts        ← SceneSpec / NarrationCue / LessonInput types
src/data/lesson-inputs.ts  ← PURE data: per-lesson title, scope, scenes[], cues[], targetFrames
        ↓  (single source of truth)
src/timeline.ts            ← buildLesson(): accumulate scene starts, distribute cues, ASSERT total frames
        ↓
src/lessons/*Scenes.tsx    ← thin scene components (render ONLY SceneFrame inner content)
src/data/lessons.tsx       ← attach renderer per slug → typed LessonSpec
src/lessons/*Video.tsx     ← ~4-line Composition wrappers
src/shared/LessonVideo.tsx ← unified engine: cover + scenes + closing, frame-driven subtitles
```

Rules:

- **No per-video fat components.** Each `Exp*` composition is a ~4-line wrapper that binds data to the shared engine. Scene-specific visuals live in `lessons/*Scenes.tsx` and only render the inner content of a `SceneFrame`.
- **All timing is derived.** Never write `const FROM = 420` style magic offsets in scene files. `buildLesson` computes every scene start frame from the declared `duration` of the preceding scenes plus the cover duration.
- **Cues are distributed, not placed.** `buildLesson` spreads each scene's narration cues across its duration with a lead-in pad and center-out jitter. Do not hardcode `{at: ...}` frame numbers.

## The `buildLesson` Timeline Compiler Contract

`buildLesson(input: LessonInput): BuiltLesson` must:

1. Start the first scene at `coverFrames`.
2. Accumulate each subsequent scene start as `previousStart + previousDuration`.
3. Within a scene, distribute its `cues` across `[sceneStart + pad, sceneStart + duration - pad]`; keep each cue inside its own scene.
4. After building, **assert `totalFrames === input.targetFrames`**. If not, throw — the data is internally inconsistent and the render would be wrong.

The `targetFrames` value is `coverFrames + Σ(scene.duration) + closingFrames`. Mismatches are caught by the compiler test, not by eyeballing keyframes.

## Single Source Of Truth For Narration

- `src/data/lesson-inputs.ts` holds every cue as `{ id, text, sceneSlug, index }`. This is the only place narration text is authored.
- `口播稿.md` is **generated**, never hand-maintained: `node scripts/gen-script.mjs` reads `lessonInputs` + `buildLesson` and writes every `cueId：text` entry grouped by lesson.
- `src/__tests__/script-sync.test.ts` asserts that every compiled cue `id:text` appears verbatim in `口播稿.md`. Hand-editing the script file breaks this test — fix the data instead.

## Guard Tests (must pass before the task is finished)

Run `tsc --noEmit && vitest run`. These four guard suites must be green:

1. **CSS animation/transition ban** — recursively scan `src/**/*.{ts,tsx}`; reject any `animation:` or `transition:` CSS property. Remotion must be frame-driven (`interpolate`), not CSS-driven.
2. **Composition registration correctness** — `src/Root.tsx` registers exactly the expected set of composition ids; no leftover template/old-lesson references.
3. **KaTeX formula guard** — any `.tsx` file containing LaTeX tokens (`\frac`, `^{`, `\sqrt`, …) must render the formula through the `<MathFormula>` component, never as raw text.
4. **口播稿 ↔ subtitle consistency** — every compiled cue `id:text` appears in `口播稿.md`; every scene referenced by a cue exists and the cue stays inside the scene boundary.

## Validation Commands

```bash
tsc --noEmit                       # type safety
vitest run                         # guard tests (4 suites)
node scripts/gen-script.mjs        # regenerate 口播稿.md from data
remotion still <ExpId> out.png 0   # at least one still to confirm the cover renders
```

## Do NOT

- Hand-write per-video fat components with hardcoded `HOOK=420`, `DEF=600` offsets.
- Maintain `口播稿.md` by copy-paste from the narration; regenerate it.
- Skip `buildLesson`'s total-frame assertion by padding durations "until it looks right".
- Add generic content pages to the empty template; design lesson-specific scenes after knowledge analysis.

## Reference Implementation

- `video/数学/4.2-指数函数/` — full data-driven lesson series (concept / image-props / compare / application) with all guard tests green.
- `video/数学/数学视频模板/` — the neutral template every new mathematics project is derived from.
