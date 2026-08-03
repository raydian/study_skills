# Superpowers Workflow Gates

## Contents

1. Mandatory Order
2. Stage 1: Brainstorm
3. Stage 2: Plan
4. Stage 3: Task Breakdown
5. Stage 4: Implementation
6. Stage 5: Review
7. Stage 6: Testing
8. Stage 7: Complete
9. Forbidden Shortcuts

## Mandatory Order

Run every video project through this exact sequence:

```text
User request
  ↓
Brainstorm
  ↓
Plan
  ↓
Task Breakdown
  ↓
Implementation
  ↓
Review
  ↓
Testing
  ↓
Complete
```

Do not start a later stage until the current stage artifact exists and its exit gate passes. When the user already supplied a decision, record it instead of asking the same question again; do not silently skip the stage.

## Stage 1: Brainstorm

Use `$brainstorming` to clarify and design before code.

Required work:

- inspect the complete source and related references;
- identify audience, learning objective, scope, target duration, content route, evidence boundaries, cover, hook, motion strategy, transitions, and dual-format needs;
- resolve material ambiguities one question at a time;
- compare viable content or visual approaches and record the recommended choice;
- present the design and obtain the user’s approval when the skill requires it.

Artifact:

```text
docs/superpowers/specs/YYYY-MM-DD-<主题>-video-design.md
```

Exit gate:

- no `TODO` or unresolved material choice;
- scope includes video code and subtitles only;
- design states that voice generation and rendering are excluded;
- design has been reviewed as required by `$brainstorming`.

## Stage 2: Plan

Use `$writing-plans` after the approved design and before production code.

Required work:

- map exact files and responsibilities;
- plan shared data, independent wide and vertical layouts, adaptive tokens, motion, transitions, subtitles, timing, and validation;
- include exact checks and expected results;
- keep rendering and voice generation out of the plan.

Artifact:

```text
docs/superpowers/plans/YYYY-MM-DD-<主题>-video.md
```

Exit gate:

- every design requirement maps to an implementation task;
- every task names exact files and verification steps;
- no placeholder or automatic render command exists.

## Stage 3: Task Breakdown

Turn the approved plan into ordered, trackable tasks. This is a separate gate even when the plan already contains task headings.

Artifact:

```text
docs/superpowers/tasks/YYYY-MM-DD-<主题>-video-tasks.md
```

Each task must contain:

- task id and objective;
- dependencies;
- exact files to create or modify;
- acceptance criteria;
- non-rendering test command or inspection method;
- status checkbox.

Recommended task order:

1. scaffold and configuration;
2. shared content, scene, timing, and caption types;
3. frame-0 cover and frame-1 hook;
4. shared semantic components;
5. horizontal composition;
6. vertical composition;
7. subtitle presentation;
8. validation utilities and tests;
9. documentation and final checks.

Exit gate:

- all tasks are small enough to implement and review independently;
- dependencies are acyclic and explicit;
- the list contains no TTS, audio generation, still rendering, or video rendering task.

## Stage 4: Implementation

Load `$remotion-best-practices`, `rules/video-layout.md`, `rules/subtitles.md`, `rules/timing.md`, and `rules/transitions.md` before implementation.

Required implementation rules:

- scaffold a blank, no-Tailwind Remotion project when needed;
- place the project under `/Users/yxy/document/jay/hs_knowledge/video/<内容分类>/<编号-主题>/`;
- store captions as JSON using the Remotion `Caption` type;
- use shared scene, caption, and timing data for both aspect ratios;
- use separate wide and vertical layout components;
- use adaptive layout tokens while preserving independent scene composition and density;
- distribute dense content across frames or scenes and use motion for progressive explanation;
- use transitions only when they express continuity, progression, contrast, reveal, or topic change;
- use frame-driven Remotion animation only;
- implement conclusion → explanation → evidence/action layers for every core teaching scene;
- register human-readable `Sequence` ranges for scene navigation in Remotion Studio;
- use semantic SVG icons/diagrams and restrained structural backgrounds where they improve hierarchy;
- update task status as each task completes.

Do not invoke TTS, voiceover, audio-duration, audio-visualization, silence-detection, or FFmpeg workflows. Do not run `remotion still` or `remotion render`.

Exit gate:

- all implementation tasks are checked complete;
- no known production-code failure remains;
- no generated audio or rendered output exists.

## Stage 5: Review

Use `$requesting-code-review`. Review against the design, plan, task list, Remotion practices, and project boundaries.

Review at least:

- requirement and scene coverage;
- frame-0 cover and frame-1 hook separation;
- horizontal and vertical semantic parity;
- independent aspect-ratio composition and adaptive layout behavior;
- absence of paragraph blocks, dense card grids, and overloaded vertical scenes;
- absence of title-only explanations, unexplained invented labels, repetitive active-state loops, and SVG/line decoration without teaching purpose;
- explicit subtitle color/font and an appropriately enlarged vertical subtitle reserve;
- named scene ranges in Studio and accurate expectations about code-generated timeline thumbnails;
- teaching purpose for motion and semantic purpose for transitions;
- subtitle type, timing, safe area, and two-line limit;
- semantic splitting of overlong subtitles into separate, non-overlapping playback ranges;
- frame-driven deterministic animation;
- absence of CSS animation and automatic rendering;
- absence of TTS, voiceover, audio embedding, or generated audio files;
- maintainability, duplicated layout logic, and unused assets.

Artifact:

```text
docs/superpowers/reviews/YYYY-MM-DD-<主题>-code-review.md
```

Exit gate:

- fix all Critical and Important findings;
- record Minor findings that are intentionally deferred;
- update the review artifact with resolution status.

## Stage 6: Testing

Testing validates the project without rendering media.

Run the checks supported by the project, such as:

- unit tests;
- TypeScript typecheck;
- ESLint;
- caption JSON schema and ordering checks;
- deterministic two-line fit checks for every caption in both aspect ratios;
- checks that split subtitle cues use distinct, consecutive, non-overlapping frame ranges;
- timeline bounds, overlap, duration, and scene-id checks;
- horizontal/vertical composition metadata parity;
- layout-policy checks for aspect-specific component selection and vertical simultaneous-item limits;
- storyboard checks for motion purpose and transition definitions;
- source scan for forbidden CSS animation, TTS, audio, and render integration.
- inspect representative stills only after an explicit user preview instruction; otherwise do not render stills or video.

Do not run `remotion render`, `remotion still`, FFmpeg export, or an automated screenshot/still render as a test.

Artifact:

```text
docs/superpowers/testing/YYYY-MM-DD-<主题>-verification.md
```

Exit gate:

- all required non-rendering checks pass;
- no subtitle exceeds two lines in either composition;
- failures are fixed and rechecked;
- the verification artifact records commands, results, and intentionally skipped visual/render checks.

## Stage 7: Complete

Completion means the Remotion engineering project and subtitles are ready for human preview or a later render instruction.

Report:

- source and project paths;
- design, plan, task, review, and test artifact paths;
- wide and vertical composition ids;
- authored duration and caption count;
- validation results;
- explicit status: no voiceover generated and no render performed.

Use this completion statement:

```text
工程与字幕已完成，未生成配音，未执行视频或单帧渲染，等待人工预览或渲染指令。
```

## Forbidden Shortcuts

- Do not combine Brainstorm, Plan, and Task Breakdown into one undocumented step.
- Do not write production code during Brainstorm or Plan.
- Do not mark Review complete with unresolved Critical or Important findings.
- Do not replace Testing with “代码看起来没问题”.
- Do not generate audio because a script exists.
- Do not render because implementation or testing is complete.
- Do not treat an explicit request to create a video project as permission to render it.
