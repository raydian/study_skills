# Project Structure And Workflow

## Contents

1. Directory Contract
2. Stage Artifacts
3. Content Artifacts
4. Implementation Contract
5. Validation Checklist
6. Completion Report

## Directory Contract

Create one project per source topic under the workspace video directory:

```text
/Users/yxy/document/jay/hs_knowledge/video/<内容分类>/<编号-主题>/
  docs/
    superpowers/
      specs/
        YYYY-MM-DD-<主题>-video-design.md
      plans/
        YYYY-MM-DD-<主题>-video.md
      tasks/
        YYYY-MM-DD-<主题>-video-tasks.md
      reviews/
        YYYY-MM-DD-<主题>-code-review.md
      testing/
        YYYY-MM-DD-<主题>-verification.md
  content-design.md
  storyboard.md
  口播稿.md
  captions.json
  timeline.json
  package.json
  src/
    Root.tsx
    compositions/
      KnowledgeWide.tsx
      KnowledgeVertical.tsx
    components/
    layouts/
      WideSceneLayout.tsx
      VerticalSceneLayout.tsx
    data/
    config/
      layout.ts
    styles/
  public/
    images/
  tests/
```

Do not create `public/audio/`, generated voice files, or an automatic `output/` render directory. Keep the source article, note, chapter, or reference material outside the video project and record its path in `content-design.md`.

## Stage Artifacts

The five Superpowers document artifacts provide evidence that Brainstorm, Plan, Task Breakdown, Review, and Testing were completed. Implementation is evidenced by source code and checked task items. Do not delete or replace these artifacts with a summary-only README.

## Content Artifacts

### `content-design.md`

Include:

- source path, version, and date when relevant;
- audience, learning problem, and desired outcome;
- core question and direct answer or learning objective;
- selected narrative route and two to four key ideas;
- representative example, analogy, demonstration, or case;
- misconception and takeaway, memory aid, or action checklist;
- claims, data, or time-sensitive facts requiring verification;
- exact one-frame cover title and hierarchy;
- separate frame-1 hook copy, hook type, and reveal plan;
- explicit exclusions: no generated voice and no automatic render.

### `storyboard.md`

Use one row per shared scene:

| Scene | Purpose | Script/caption cues | Horizontal visual | Vertical visual | Motion purpose | Transition out | Visual cue ids |
|---|---|---|---|---|---|---|---|

### `口播稿.md`

Write subtitle-sized semantic cues rather than long paragraphs. Include scene id, cue id, editorial tone, suggested pause, and visual cue id. Treat this as editorial text only; do not generate audio from it.

### `captions.json` And `timeline.json`

- Store subtitles as Remotion `Caption[]` JSON.
- Author cue durations explicitly and keep them synchronized with scene frames.
- Keep frame `0` caption-free and start the hook at frame `1`.
- Use the same files in both compositions.
- Measure subtitle layout for both aspect ratios. Split any cue that exceeds two lines into multiple semantic cues with different consecutive frame ranges.
- Never shrink, compress, clip, or truncate a subtitle to avoid splitting it.

## Implementation Contract

- Use `$remotion-best-practices`, `rules/video-layout.md`, `rules/subtitles.md`, `rules/timing.md`, and `rules/transitions.md` before editing Remotion code.
- Scaffold an empty project with `npx create-video@latest --yes --blank --no-tailwind <工程名>` when required.
- Centralize color tokens, typography, safe areas, content, captions, and timing.
- Share semantic components and data; split layout components by aspect ratio where necessary.
- Centralize adaptive layout tokens, but give wide and vertical scenes independent flow, geometry, density, and reveal cadence.
- Use time-based reveals, focus changes, diagrams, and semantic transitions instead of paragraph blocks or dense card grids.
- Build every key scene as conclusion → explanation → evidence/action. Do not substitute title-only cards for source reasoning.
- Use SVG icons and diagrams where they explain a relationship; pair them with readable labels and explanatory copy. Use low-contrast structural backgrounds behind content, never as a replacement for it.
- Use named `Sequence` ranges matching the storyboard so Studio offers a usable scene timeline.
- Explicitly set subtitle text color and font. For vertical videos, prefer 48-52px subtitles with a correspondingly enlarged bottom reserve.
- Drive every animation from Remotion frames and deterministic interpolation.
- Forbid CSS transitions, CSS animations, and Tailwind animation classes.
- Keep assets in `public/` and use `staticFile()`.
- Display required readable text as HTML or SVG overlays.
- Do not add audio components, TTS dependencies, render scripts, or post-render tooling.

## Validation Checklist

Before claiming engineering completion:

- [ ] All seven workflow stages were executed in order.
- [ ] Design, plan, task, review, and testing artifacts exist.
- [ ] Source claims, definitions, data, and scope boundaries are accurate.
- [ ] Frame `0` is a finished one-frame cover with a large readable title in both formats.
- [ ] Frame `1` begins a visually independent hook page.
- [ ] Both compositions share fps, frame count, scene ids, captions, and timing.
- [ ] Captions use the Remotion `Caption` shape and do not overlap.
- [ ] Frame `0` has no caption; every other caption stays within its scene.
- [ ] Every visible subtitle contains no more than two lines in both formats.
- [ ] Every overlong source sentence was split at semantic boundaries into separate cues assigned to different consecutive playback frames.
- [ ] No subtitle was forced to fit by shrinking, compressing, clipping, masking, ellipsizing, or hiding overflow.
- [ ] Horizontal and vertical layouts communicate the same meaning.
- [ ] Horizontal and vertical layouts use aspect-specific composition rather than identical fixed geometry.
- [ ] Vertical scenes use one primary content unit and no more than one compact supporting unit at a time unless the approved design documents a justified exception.
- [ ] Dense source material is distributed across frames or scenes instead of being reduced through smaller text.
- [ ] Every core scene contains conclusion, explanation, and evidence/action layers; no key scene is title-only.
- [ ] SVG icons, diagrams, and background structures clarify hierarchy or relationships rather than serving as empty decoration.
- [ ] Decision and process scenes advance in a narrative direction; they do not use a context-free repeating highlight loop.
- [ ] Timeline contains named `Sequence` ranges for all shared scenes; expectations about Studio thumbnail strips are accurate.
- [ ] Every animation and transition has a documented teaching or semantic purpose.
- [ ] Typecheck, lint, unit tests, caption checks, and timeline checks pass.
- [ ] Review has no unresolved Critical or Important issue.
- [ ] No TTS, generated voice, audio component, or audio file exists.
- [ ] No still, screenshot, or video rendering was run automatically.
- [ ] No generated MP4 is claimed or required for completion.

## Completion Report

Report:

- source path and project path;
- design, plan, task, review, and test artifact paths;
- wide and vertical composition ids;
- authored duration and caption count;
- checks performed and their results;
- unresolved Minor review findings, if any;
- confirmation that no voice was generated and no render was performed.

End with:

```text
工程与字幕已完成，未生成配音，未执行视频或单帧渲染，等待人工预览或渲染指令。
```
