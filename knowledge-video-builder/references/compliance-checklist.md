# Compliance Checklist (Final Gate)

## Contents

1. When And How To Run
2. Fix-And-Recheck Loop
3. Subtitles
4. Motion And Transitions
5. Colors
6. Layout Structure
7. Cover And Hook
8. Dual-Format Consistency
9. Teaching Content
10. Forbidden Patterns
11. Required Automated Test Suite
12. Recording Results

## When And How To Run

Run this checklist inside **Stage 6 (Testing)**, after the project's own automated checks pass, and again after every fix. It is the final conformance pass against this skill's constraints — subtitles, motion, colors, and layout structure — before Stage 7 may report completion.

Two layers:

- **Machine layer**: the project's automated checks (`typecheck`, `lint`, `vitest`, `validate-video`) must encode every check marked `[auto]` below. A project missing a required `[auto]` check must add it to `tests/`.
- **Manual layer**: design-review items marked `[manual]` are verified by reading the storyboard and source, and recorded in the review and verification artifacts.

## Fix-And-Recheck Loop

Any failed item, whether found by machine or manual review:

1. Fix the production code or data — never weaken the check to match the code.
2. Re-run the **entire** automated suite (not only the failed check).
3. Re-walk the affected manual items.
4. Update `docs/superpowers/testing/...-verification.md` with the failure, the fix, and the recheck result.

Stage 6 may not close with open failures. Intentional deviations must be documented in the design spec and the review artifact with reasons.

## Subtitles

- [auto] Every cue matches the Remotion `Caption` shape exactly (`text`, `startMs`, `endMs`, `timestampMs`, `confidence`).
- [auto] Cues are ordered, non-overlapping, and within total duration; first cue starts no earlier than frame 1 (`≥ 1000/30` ms); frame 0 has no caption.
- [auto] Every cue belongs to exactly one scene and its end frame does not cross the scene boundary.
- [auto] Deterministic two-line fit for **both** formats: wide `subtitle px / (1920 - 2*safeX - padding)` and vertical `subtitle px / (1080 - 2*safeX - padding)`. Width factors: full-width char `1.0em`, CJK punctuation `0.7em`, space `0.3em`, other ASCII `0.58em`.
- [auto] No shrunk font, negative tracking, clipping, masking, ellipsis, or hidden overflow used to avoid splitting; overlong sentences exist as multiple consecutive, non-overlapping cues.
- [manual] Subtitle band has explicit `color` and `fontFamily` (never inherited); sits inside the reserved band; cue switches use the ≤6-frame micro-fade from `transition-playbook.md`.
- [manual] At most one `accent` keyword emphasis per cue band; dark text on any yellow pill.

## Motion And Transitions

- [auto] Source contains no CSS `transition:`/`animation:` declarations and no Tailwind animation classes.
- [auto] Every non-cover scene is wrapped in the shared SceneTransition component (paired enter/exit fades) — asserted by source inspection tests.
- [manual] Entrance ≤18 frames, exit ≤12 frames, bezier easing; no transition touches the subtitle band or frame 0.
- [manual] Ordered sibling series use one slide direction and one layout skeleton; a matched-element continuity anchor appears in every sibling scene and again (all-lit) in the closing scene.
- [manual] Reveals are one-way and frame-derived (`floor(elapsed/step)`), never looping highlight loops; every animation maps to a documented `motionPurpose` in the storyboard.

## Colors

- [manual] Only palette tokens from `visual-system.md` are used; semantic roles stay stable (blue=structure/current, yellow=answer/key point, green=valid/corrected, red=risk/misconception, purple=secondary dimension, gray=inactive).
- [manual] Distribution roughly 70/20/7/3; no large saturated red/yellow fields; `danger` used as text/outline/small fill only.
- [manual] Text contrast on `bgDeep`/`panel` holds for muted labels and annotations; misconception pairs read danger→success.

## Layout Structure

- [auto] Vertical composition is an independent implementation: does not import wide scene files; `columns: 1`; `maxSimultaneousItems ≤ 2`.
- [manual] Safe areas honored (wide 90px sides, ≥150px bottom subtitle reserve; vertical 56-72px sides, ≥260px bottom reserve); typography within token ranges (wide title 42-52/board 28-36/subtitle 28-32; vertical title 52-64/board 38-48/subtitle 38-52).
- [manual] One dominant focal element per frame; wide ≤3 peer items; vertical one primary + at most one compact supporting unit; no paragraph blocks or dense card grids; final reveal state no denser than the opening can support.
- [manual] Core scenes show conclusion (largest) → explanation (secondary) → evidence/action (compact); backgrounds stay low-contrast and behind content.

## Cover And Hook

- [auto] Cover contains no frame-driven code (no `useCurrentFrame`); hook does.
- [manual] Cover is complete at frame 0: dominant large title, one accent key phrase, secondary series label; hook page is visually distinct (different hierarchy/composition), runs ~5s, and answers or routes within 5-15s of video start.

## Dual-Format Consistency

- [auto] Both compositions registered with same fps and `durationInFrames` from shared timeline; scene ids mapped in both layouts.
- [auto] Identical caption JSON for both; no vertical-only re-edit.
- [manual] Vertical scenes reflow meaning (stack/sequence), never scale or crop the wide geometry.

## Teaching Content

- [auto] Every core scene's shared content has non-empty conclusion, explanation, evidence, and next-step fields.
- [manual] No title-only scenes; one representative case present and labeled 示例 when illustrative; time-sensitive claims tied to source/date or removed; no invented jargon, no absolute guarantees.
- [manual] Editorial script (`口播稿.md`) has no direction-dependent wording (左/右/上/下 references).

## Forbidden Patterns

- [auto] No `<Audio>`, `@remotion/media`, `.mp3/.wav` imports, TTS calls, render scripts, or FFmpeg integration in source; no audio/video files in the project tree (symlink-aware `find`).
- [auto] `package.json` scripts contain no render/still command.
- [manual] `node_modules` is a symlink to the workspace-shared dependency directory per workspace convention; no project-local `npm install` was run.

## Required Automated Test Suite

Every project ships `tests/video-contract.test.ts` (or equivalent) plus `tests/validate-video.mts`, covering at minimum:

1. timeline fps/totalFrames/scene count/contiguity, cover at frames 0-1, hook start at frame 1;
2. caption shape, ordering, non-overlap, frame-0 exclusion, scene-bound containment;
3. two-line fit in both formats for every cue;
4. core-scene content completeness (conclusion/explanation/evidence/nextStep);
5. dual composition registration parity (ids, fps, duration);
6. vertical independence (no wide imports, column/item limits);
7. cover-static / hook-frame-driven source assertions;
8. subtitle band explicit color/font assertions;
9. transition wrapper and continuity anchor presence;
10. forbidden-pattern source scan (audio, CSS animation/transition, render);
11. editorial script direction-word scan.

Pitfall: source-assertion tests match raw text — keep the literal strings being asserted (e.g. `useCurrentFrame`, direction words, `transition:`) out of comments and doc strings, or the tests produce false failures.

## Recording Results

Record in `docs/superpowers/testing/YYYY-MM-DD-<主题>-verification.md`:

- each automated command and its result;
- manual items walked and their outcome;
- failures found, fixes applied, and recheck evidence;
- intentionally skipped items (e.g. Studio visual preview) with the reason.
