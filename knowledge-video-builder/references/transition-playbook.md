# Transition And Motion Playbook

## Contents

1. Why This Playbook Exists
2. The SceneTransition Wrapper Pattern
3. Slide Relay For Sibling Scenes
4. Matched-Element Continuity Anchors
5. One-Way Staggered Reveal
6. Hook Page Evolution
7. Subtitle Cue Micro-Fade
8. Transition Budget And Safety Rules
9. Scene-To-Transition Mapping
10. Review Checklist Additions

Distilled from the `video/选科/04-六门选考科目分别学什么/` production (2026-08). Apply these patterns to every knowledge video; they answer the recurring requirement "动效自然、场景切换平滑、上下承接、分镜流畅".

## Why This Playbook Exists

`motion-layout.md` defines *which* transition means *what*. This playbook defines *how* to implement smooth, connected scene changes with plain frame-driven Remotion code — without `TransitionSeries`, without CSS transitions, and without breaking the frame-based scene timeline or caption math.

Key architectural reason: when scenes are dispatched by `getScene(frame)` (instant switch, no overlap), smoothness must come from **paired exit/entrance fades** inside each scene, not from overlapping sequences.

## The SceneTransition Wrapper Pattern

Wrap every non-cover scene's content in one shared `SceneTransition` component:

- **Entrance**: 18 frames, `opacity 0→1` + `translateY 24→0px`, easing `Easing.bezier(0.16, 1, 0.3, 1)`, both sides clamped.
- **Exit**: final 12 frames of the scene, `opacity 1→0`, clamped.
- Combined opacity is `min(enter, exit)`: fully visible mid-scene, fading at both edges.

Because the previous scene ends at opacity 0 and the next begins at opacity 0 and fades in, adjacent scenes read as a **cross-fade** even though they never overlap in the timeline. This is the default "topic boundary / calm reset" transition.

Rules:

- Exactly one wrapper per scene, at the scene's root content container.
- Never wrap the frame-0 cover. The cover is static and hard-cuts to the hook at frame 1.
- Never apply entrance/exit fades to the subtitle band; subtitles live above scenes (higher z-index) and have their own micro-fade (see below).

Reference implementation (`src/components/SceneTransition.tsx` in project 04):

```tsx
const enter = interpolate(e, [0, 18], [0, 1], {easing: EASE, extrapolateLeft: "clamp", extrapolateRight: "clamp"});
const exit = interpolate(e, [dur - 12, dur], [1, 0], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
const opacity = Math.min(enter, exit);
const ty = (1 - enter) * 24;
```

## Slide Relay For Sibling Scenes

For an ordered series of sibling scenes (e.g. six subject scenes physics→geography), add a **unidirectional horizontal relay** on top of the wrapper:

- entrance: `translateX 60→0px` (new scene slides in from the right);
- exit: `translateX 0→-40px` (old scene slides out to the left).

All sibling scenes must use the **same direction and the same layout skeleton** so the viewer reads "next item in one sequence", not "a new unrelated page". Never alternate directions within one series.

## Matched-Element Continuity Anchors

Smooth 上下承接 needs a persistent visual anchor that survives scene changes at a constant position:

- Build a series-level navigation element (e.g. `SubjectNav`): one node per sibling scene; states = current (accent, enlarged, glow) / completed (primary, lit) / upcoming (muted).
- Render it at the **identical coordinates** in every sibling scene and in the summary/closing scenes (with all nodes lit) so the series opens and closes as a loop.
- Wide: horizontal node rail with dot + label. Vertical: compact progress-bar dots at the top — same data, different geometry, never a shrunk copy.
- In the closing scene, reuse the anchor with all nodes lit to "回收路线图", forming a narrative loop.

## One-Way Staggered Reveal

Within a scene, reveal lists one item at a time, driven by the scene-local frame:

- `step = floor(sceneDuration / itemCount)`; `currentIndex = floor(elapsed / step)` clamped.
- Each item enters with the same 18-26 frame bezier fade+rise as scenes.
- Current item highlighted (accent border/glow); previously revealed items stay visible but dimmed or compact; unrevealed items hidden or ghosted.
- **Never** use a repeating active-state loop for teaching sequences — narrative state must match the spoken progression (see `motion-layout.md` "Hierarchy And Non-Looping Explanations").
- Vertical layouts show one card at a time plus a compact progress rail; wide layouts may keep up to three peer items visible.

## Hook Page Evolution

The hook page is one scene with internal staging, roughly five seconds:

1. Present the question/conflict lines with staggered entrances (~20 frames apart).
2. Dim them to ~30-35% opacity once the correction arrives.
3. Bring the correction in with fade + rise + slight scale-up (`0.92→1.0`), in `accent`, as the largest element.

This creates an internal "立→破" beat without a scene change.

## Subtitle Cue Micro-Fade

At each caption cue start, fade the subtitle band in over ~6 frames (`min(1, elapsedCueFrames / 6)`). This removes the "hard pop" between consecutive cues while keeping cue timing and two-line limits untouched. Do not animate cue exit; the next cue's fade-in is sufficient.

## Transition Budget And Safety Rules

- Transition frames cost attention: keep entrance ≤18 frames and exit ≤12 frames; total transitional time per boundary ≤1s.
- Transitions must never cover, dim, or move the subtitle band.
- Transitions must never alter the exact one-frame cover rule.
- Use one small vocabulary per video (cross-fade + slide relay + staggered reveal covers most explainers). A different effect per scene is a defect.
- All motion is `useCurrentFrame()` + `interpolate()`/`spring()`; no CSS transitions, CSS animations, or Tailwind animation classes.
- Avoid the literal strings `transition:` and `animation:` in source and comments — validation scans reject them.

## Scene-To-Transition Mapping

| Scene relationship | Transition | Implementation |
|---|---|---|
| frame-0 cover → frame-1 hook | hard cut | no wrapper on cover; hook has own staged reveals |
| topic boundary (intro→framework, body→summary) | cross-fade | default SceneTransition enter/exit |
| ordered sibling series (subjects, steps) | slide relay | SceneTransition with `slide` + shared skeleton + nav anchor |
| layer/condition reveal inside a scene | staggered reveal | frame-derived index, one-way |
| before/after, label→ruler, wrong→right | replace-in-place | old content dims to ~30%, new content fades/scales in same region |
| scene → case/example | slide | progression to next beat |
| action → closing | cross-fade | calm reset; closing reuses nav anchor all-lit |

## Review Checklist Additions

During Stage 5 review and Stage 6 testing, additionally verify:

- every non-cover scene is wrapped in the shared transition component (no ad-hoc per-scene fades);
- sibling series share one slide direction and one layout skeleton;
- a matched-element anchor exists for every multi-scene series and reappears in the closing scene;
- reveals are one-way and frame-derived, never looping;
- subtitle band is outside and above all scene transitions;
- transition frames ≤18 in / ≤12 out; no transition touches frame 0.
