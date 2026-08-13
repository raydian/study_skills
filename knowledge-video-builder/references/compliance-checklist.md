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
- [auto] Subtitle tokens match the baseline: wide `54px`, `1.3` line-height, `82cqw` width, `21.6px` bottom; vertical `64.8px`, `1.5` line-height, `64.8px` side insets, `211.2px` bottom; light/dark three-layer shadow tokens are present. An intentional deviation must be machine-readable in the design config and documented in design/review/testing artifacts.
- [manual] Subtitle band has explicit `color` and `fontFamily` (never inherited), uses an actually loaded font, includes the reference three-layer shadow or a documented legibility-equivalent treatment, sits inside the reserved band, and uses the ≤6-frame cue micro-fade from `transition-playbook.md`.
- [manual] At most one `accent` keyword emphasis per cue band; dark text on any yellow pill.

## Motion And Transitions

- [auto] Source contains no CSS `transition:`/`animation:` declarations and no Tailwind animation classes.
- [auto] Every non-cover scene is wrapped in the shared SceneTransition component (paired enter/exit fades) — asserted by source inspection tests.
- [manual] Entrance ≤18 frames, exit ≤12 frames, bezier easing; no transition touches the subtitle band or frame 0.
- [manual] Ordered sibling series use one slide direction and one layout skeleton; a matched-element continuity anchor appears in every sibling scene and again (all-lit) in the closing scene.
- [manual] Reveals are one-way and frame-derived (`floor(elapsed/step)`), never looping highlight loops; every animation maps to a documented `motionPurpose` in the storyboard.

## Colors

- [manual] Only palette tokens from `visual-system.md` are used; the project uses exactly one palette — standard deep-blue for general knowledge videos, or the ink-wash (水墨留白) palette for 选科-related videos. Standard semantic roles stay stable (blue=structure/current, yellow=answer/key point, green=valid/corrected, red=risk/misconception, purple=secondary dimension, gray=inactive); ink-wash roles map to seal=answer/key point, ink=structure/current, inkSoft=secondary dimension, wash=inactive, success=valid/corrected, danger=risk/misconception.
- [manual] Standard distribution roughly 70/20/7/3; ink-wash distribution roughly 85/10/4/1; no large saturated red/yellow fields; `danger` used as text/outline/small fill only.
- [manual] Standard palette: text contrast on `bgDeep`/`panel` holds for muted labels and annotations; misconception pairs read danger→success. Ink-wash palette: light scenes keep `ink` on `paper` ≥ 7:1, `inkSoft` ≥ 4.5:1, `seal` text on `paper` ≥ 4.5:1, and no white text on `wash` panels; H01/V01 and H22/V22 use `paper` on `ink` with only a small `seal` accent.

## Layout Structure

- [auto] Vertical composition is an independent implementation: does not import wide scene files; `columns: 1`; `maxSimultaneousItems ≤ 2`.
- [auto] Every storyboard scene names a horizontal (H01-H22) and a vertical (V01-V22) layout tag from `references/page-layouts.md`, and layout components are named after the declared tags.
- [auto] Reference layout tokens are present in the centralized mode config: wide safe edge `90px`, standard inset `115.2px`, subtitle `54px`; vertical inset `75.6px`, content bottom `633.6px`, subtitle `64.8px` at bottom `211.2px`.
- [manual] Selected H/V layouts preserve their page-specific `cqw/cqh` typography, spacing, line-height, hierarchy, and element-count rules from `page-layouts.md`; generic framework typography ranges are not accepted as substitutes.
- [manual] Vertical scenes use the declared V01-V22 stacked/sequential structures: one primary unit at a time, teaching content confined above the bottom-third subtitle zone, no scaled or cropped horizontal board.
- [auto] Vertical scene containers use flow layout (outer `padding:170px 64px 640px`, header `flexShrink:0`, content `flex:1`, footer flowing) — no absolute-positioned header + content stacks that can overlap.
- [auto] Vertical card copy meets token floors: card name `≥42px`, description `≥32px` (and equivalent floors for list/step/spec text), asserted from the layout config or component source.
- [auto] Wide content boards center vertically and keep footers above the subtitle footprint (`bottom ≥250px`).
- [auto] Spec/table rows do not overlap: the table page is a flow column (header `flexShrink:0` → table `flex:1; justifyContent:center` → footer flowing); value cells use `whiteSpace:nowrap; overflow:hidden; textOverflow:ellipsis` so a long value never wraps into the next row (production bug fixed 2026-08, 选科 series).
- [auto] Vertical spec grid stays roomy: 2-column grid with `gridTemplateRows: repeat(3, 1fr)`, `gap ≥18px`, cell padding `≥24px`, label `≥34px`, value `≥28px` — six cells must not look cramped (production feedback 2026-08, 选科 series).
- [manual] One dominant focal element per frame; wide ≤3 peer items; vertical one primary + at most one compact supporting unit; no paragraph blocks or dense card grids; final reveal state no denser than the opening can support.
- [manual] Core scenes show conclusion (largest) → explanation (secondary) → evidence/action (compact); backgrounds stay low-contrast and behind content.

## Cover And Hook

- [auto] Cover contains no frame-driven code (no `useCurrentFrame`); hook does.
- [auto] Ink-wash (选科) cover is a dark surface: composition marks `cover` as dark (`sceneId === 'cover' || sceneId === 'closing'`), and the cover component uses `paper` title text on `ink` background; the cover has no series label such as `选科科普 · 01`.
- [auto] Dark covers carry wave-line texture: the shared scene shell renders low-opacity `paper` wave strokes (`rgba(245,242,233,0.10)`) with independent wide and vertical path geometry, so the ink field is not flat (asserted from the shell source).
- [auto] Cover component has no opaque background of its own: its root `AbsoluteFill` must not set `backgroundColor` (the ink surface + wave texture come from `SceneShell` dark; an opaque cover root would hide the texture and regress to a flat color cover).
- [manual] Cover is complete at frame 0: dominant large title, one accent key phrase, optional secondary meta line; hook page is visually distinct (different hierarchy/composition), runs ~5s, and answers or routes within 5-15s of video start.
- [auto] Closing page does not preview the next article's title: source contains no `下一篇` in the closing scene component or closing captions; it renders an action line instead (an intentional `下一篇` preview requires an explicit user request and a design note).

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
11. editorial script direction-word scan;
12. storyboard layout-tag coverage (every scene row names a valid H01-H22 tag and a V01-V22 tag).
13. exact baseline layout-token assertions for both formats, including subtitle size, line-height, width/insets, bottom position, vertical bottom-third exclusion, and loaded-font evidence.
14. ink-wash cover assertions: dark composition marking, `paper` title on `ink`, no series label, no `下一篇` preview in closing (source-scan driven).

Pitfall: source-assertion tests match raw text — keep the literal strings being asserted (e.g. `useCurrentFrame`, direction words, `transition:`) out of comments and doc strings, or the tests produce false failures.

## Recording Results

Record in `docs/superpowers/testing/YYYY-MM-DD-<主题>-verification.md`:

- each automated command and its result;
- manual items walked and their outcome;
- failures found, fixes applied, and recheck evidence;
- intentionally skipped items (e.g. Studio visual preview) with the reason.
