# Project Structure

Use this structure for each knowledge point:

```text
video/<学科>/<知识点工程目录>/
  口播稿.md
  storyboard.md
  content-design.md      # required knowledge analysis and video design
  source.md              # optional copy or summary of source knowledge file
  package.json
  src/
    Root.tsx
    Composition.tsx
    scenes/
    components/
    data/
  public/
    images/
  renders/
```

## Naming

- Use a readable Chinese slug when possible, such as `1.1-集合的概念`.
- Keep one knowledge-point file to one video project.
- Do not mix several unrelated knowledge points in one video unless the user asks for a unit-level video.

## Repository Templates

- Mathematics projects in this repository must come from `video/数学/数学视频模板/` through `scripts/create_math_video.py` and use `video/数学/node_modules` through a relative symlink.
- Chinese projects in this repository must come from `video/语文/语文视频模板/` through `scripts/create_chinese_video.py` and use `video/语文/node_modules` through a relative symlink.
- The Chinese template contains only the shared visual system, standard cover, and standard closing. Create article-specific content scenes after knowledge analysis; do not add generic content pages to the template.
- Do not run project-local dependency installation in a template-derived mathematics or Chinese project. Add shared dependencies at the subject root and retain direct declarations in the consuming project.

## Mathematics Data-Driven Layout

A mathematics project derived from `video/数学/数学视频模板/` does **not** follow the generic `Composition.tsx` + `scenes/` layout above. It uses the data-driven lesson engine described in `references/math-lesson-engine.md`:

```text
video/数学/<工程目录>/
  src/
    timeline.ts              # buildLesson compiler (auto scene starts + cue distribution + frame assertion)
    types/lesson.ts          # SceneSpec / NarrationCue / LessonInput
    data/
      lesson-inputs.ts       # PURE data: the single source of truth for timing + narration
      lessons.tsx            # attach renderer per slug -> typed LessonSpec
    shared/LessonVideo.tsx   # unified cover + scenes + closing engine
    lessons/
      *Scenes.tsx            # scene-specific inner content (no frame math)
      *Video.tsx             # ~4-line Composition wrapper
    Root.tsx                 # register composition ids
    __tests__/               # timeline / source-guard / script-sync guard suites
  scripts/gen-script.mjs     # regenerate 口播稿.md from lesson-inputs
```

Rules:

- Timing and narration live in `data/lesson-inputs.ts`; the engine derives everything else.
- Do not add `Composition.tsx` or a `scenes/` directory to a mathematics project.
- Keep the three `__tests__/` guard suites green (`tsc --noEmit && vitest run`).
- See `references/math-lesson-engine.md` and the `remotion-lesson-video` skill for the full contract.


## Remotion Defaults

- Width: `1920`
- Height: `1080`
- FPS: `30`
- Duration: `2-15` minutes as a soft range (3600-27000 frames at 30fps), but the actual length should be determined by the content and narration. Do not stretch scenes to fill time; avoid blank停留 with no explanation.
- Composition id: use a stable English id such as `KnowledgeLecture`.

## Asset Rules

- Copy note images into `public/images/`.
- Use `staticFile("images/<name>")`.
- Keep source note paths documented in `storyboard.md`.
- Do not reference assets outside the project from Remotion code.
