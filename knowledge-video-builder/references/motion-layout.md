# Motion And Adaptive Layout

## Contents

1. Video-Native Content Density
2. Motion As Explanation
3. Semantic Transitions
4. Wide Layout Strategy
5. Vertical Layout Strategy
6. Adaptive Architecture
7. Quality Gates

## Video-Native Content Density

Design every scene around one dominant message and one supporting visual relationship. Do not reproduce article paragraphs on screen.

Prefer:

- one short headline;
- one diagram, comparison, example, number, or visual metaphor;
- one active emphasis state;
- subtitles in their reserved band.

Avoid:

- paragraph blocks;
- full article sentences repeated above the subtitles;
- dense dashboards, large tables, many badges, or grids of small cards;
- multiple equally prominent focal points;
- keeping all steps, branches, or examples visible at once.

When content is crowded, solve it in this order:

1. remove duplicate on-screen wording already present in subtitles;
2. shorten labels without changing meaning;
3. reveal items sequentially;
4. replace prose with a diagram, icon, path, or comparison state;
5. split the content into additional scenes.

Never solve crowding by shrinking text below the approved size.

## Motion As Explanation

Give every animation a teaching purpose. Useful patterns include:

- progressive reveal for ordered ideas;
- focus shift that dims context and highlights the current concept;
- path or connector drawing for process and causality;
- before/after transformation for change;
- matched movement for continuity between related scenes;
- count-up or chart growth for quantities;
- staged comparison that introduces a shared baseline before differences;
- replace-in-place for alternatives that should not appear simultaneously.

Drive motion with Remotion frames and `interpolate()`. Prefer Bézier easing and deterministic ranges. Keep continuous decorative movement minimal; it competes with reading and explanation.

## Semantic Transitions

Choose transitions by meaning:

- hard cut: decisive contrast, frame-0 cover to frame-1 hook, or fast correction;
- fade: topic boundary, summary, or calm reset;
- slide: ordered progression or moving to the next step;
- wipe: revealing a layer, condition, or before/after state;
- matched element movement: continuing the same concept in a new layout.

Use a small, consistent transition vocabulary across the video. Avoid a different effect for every scene. Keep transitions short enough that the content remains primary.

When using `TransitionSeries`, account for overlapping transition frames in total duration and keep shared caption timing valid. Do not let transitions obscure subtitles or change the exact one-frame cover rule.

For concrete implementations — the shared SceneTransition wrapper (paired enter/exit fades), slide relay for sibling scenes, matched-element continuity anchors, one-way staggered reveals, hook staging, and the transition safety budget — follow `transition-playbook.md`. When scenes are dispatched by frame lookup rather than `TransitionSeries`, the playbook's paired-fade pattern is the default way to get smooth cross-fades without breaking caption math.

## Wide Layout Strategy

Use horizontal space for relationships, not for filling every available region. Horizontal page structures come from `references/page-layouts.md` H01-H22; pick one per scene and record its tag in the storyboard.

Suitable patterns:

- two clearly prioritized comparison panels (H08 Compare);
- left-to-right process or timeline (H09 Process Steps);
- primary explanation plus one supporting visual (H04 Concept + Visual);
- route map with two or three nodes;
- chart with a focused annotation region (H12 Data + Insight).

Default simultaneous density:

- one headline;
- one primary visual structure;
- up to three short peer items only when comparison requires simultaneous visibility (H06 Pillars, H11 KPIs).

Move detailed explanation into time-based reveals rather than extra columns.

## Vertical Layout Strategy

Treat vertical as an independently composed mobile video, not a narrow version of the wide scene. Vertical page structures come from `references/page-layouts.md` V01-V22 — each is a separate stacked or sequential layout for the 1080x1920 canvas with a bottom-third subtitle zone; never scale or crop the horizontal page.

Implementation constraint — vertical scene containers must use **flow layout**, not absolute-positioned header/content stacks:

- Outer container: `position:absolute; inset:0; padding:170px 64px 640px; display:flex; flexDirection:column`.
- Header (kicker + title): `flexShrink:0`. Content board: `flex:1; justifyContent:center` (or top-aligned when the V-layout says so). Footer/insight line: flowing `marginTop`, never `position:absolute; bottom:...`.
- Reason: an absolute `top:150/170` header plus an absolute `top:200/230` content board overlap when the title wraps to two lines (production bug, 2026-08 选科 series). Flow layout makes overlap impossible and keeps content out of the bottom-third subtitle zone.
- Footer/insight text must stay above the subtitle footprint: in wide scenes `bottom ≥ 250px` (1080-high canvas), in vertical scenes flowing above the `640px` bottom padding.

Prefer:

- centered or strongly aligned single-column flow (V01, V03, V05, V14, V15, V18, V22);
- one main card, node, example, or chart focus at a time (V04, V06, V07, V12);
- top-to-bottom process and milestone rails (V08, V09, V17);
- sequential replacement instead of side-by-side comparison (V08, V17 replace H08, H17 columns with stacked panels + down arrows);
- two-column grids only when the grid is the teaching point, and only as the 2x2/2-column pattern (V10 Matrix, V16 Icon Features, V19 Spec Grid);
- larger labels, shorter copy, larger gaps, and more empty space;
- persistent summary or progress indicator only when it does not compete with the focal content;
- a reserved bottom-third subtitle zone that teaching content never enters.

Default simultaneous density:

- one headline;
- one primary visual or card;
- at most one compact supporting element.

If a wide scene has two or three columns, convert vertical to steps, alternating states, or a vertical sequence (per the V-layout mapping). Do not preserve the column count by shrinking cards. Split a vertical scene when its final state remains crowded after sequential reveal.

### Subject-Selection Series Rules

For 选科 series (e.g. six 选考科目), enforce these density rules on top of the defaults:

- Wide: the series map uses a `3+3` grouped grid or a subject-vs-dimension matrix, capped at six cards total; `SubjectNav` node rail stays on top across every sibling scene. A compare scene may show two subjects side by side, never more.
- Vertical: show **exactly one** subject card at a time with the `SubjectNav` progress dots pinned at the top; the completed subject collapses to a compact checkmark row and the next subject enters. Never render all six subject cards as a vertical grid — that violates the one-primary-unit rule.
- The closing scene reuses the nav anchor with all nodes lit (all-subjects state), which is the only scene allowed to display all six names — as compact lit labels, not six full cards.

## Adaptive Architecture

Share semantic data and timing, then adapt presentation through explicit layout configuration. The layout configuration picks the horizontal H-layout and the vertical V-layout per scene from `references/page-layouts.md`; the storyboard row records both tags.

Use tokens or helpers such as:

```ts
type LayoutMode = "wide" | "vertical";

type LayoutConfig = {
  mode: LayoutMode;
  safeAreaX: number;
  safeAreaTop: number;
  safeAreaBottom: number;
  gap: number;
  headlineSize: number;
  bodySize: number;
  columns: 1 | 2 | 3;
  flow: "row" | "column";
  maxSimultaneousItems: number;
};
```

Derive these values from the composition dimensions or an explicit composition mode. Use normal flex/grid flow for readable content. Use absolute positioning mainly for backgrounds and deliberate layering.

Share:

- content, scene ids, cue ids, timing, color semantics, and reusable primitives.

Adapt or split:

- scene composition, flow direction, column count, card size, gaps, font scale, item visibility, reveal cadence, and diagram orientation.

A responsive component is acceptable only when it produces genuinely different geometry and density for each mode. A global scale transform, fixed 1920-pixel canvas, or CSS-only squeeze is not adaptive layout.

## Quality Gates

Reject a scene when:

- it contains paragraph-like text or repeats the subtitle verbatim without visual purpose;
- two or more elements compete as the primary focal point;
- vertical shows more simultaneous content than it can comfortably hold;
- the storyboard does not name a horizontal and a vertical layout tag from `references/page-layouts.md`;
- wide and vertical use the same fixed coordinates or card grid;
- the vertical version is produced by scaling or cropping the wide version;
- the vertical content board extends into the bottom subtitle zone;
- animation is decorative and does not reveal meaning;
- transitions obscure text, collide with captions, or vary without semantic reason;
- the final reveal state is denser than the opening state can support.

Review each storyboard row for a separate `horizontalVisual`, `verticalVisual`, `motionPurpose`, and `transitionOut` definition before implementation.

## Hierarchy And Non-Looping Explanations

When a scene teaches a decision framework, reveal it in a one-way narrative: establish a first layer, retain it as context, add the next layer, then show the completed relationship. Do not use a repeating active-state loop when it disconnects visual state from spoken explanation.

Require one dominant conclusion, one readable explanation block, one supporting SVG diagram/icon group/comparison/example/action cue, and a subordinate background structure. Reject a scene that is only headline plus cards, only an icon plus label, or only decorative lines with no information relationship.
