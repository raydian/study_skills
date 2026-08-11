# Visual System

Use a two-layer visual system:

1. **Course-series constants**: stable layout, subtitle position, progress bar, title chrome, typography scale, transition rhythm, frame-driven motion rules, and teaching-board density.
2. **Subject visual profiles**: subject-specific background texture, accent palette, diagram language, icons, and visual metaphors.

`video/数学/sets-concept/` is the math reference implementation, not the universal look for every subject. Future math videos should stay close to it. Other subjects should preserve the shared course skeleton while visibly belonging to physics, chemistry, biology, geography, history, etc.

## Course-Series Constants

All videos should feel like one coherent high-school knowledge course:

- horizontal `1920x1080`, `30fps`;
- light, pleasant, precise, and structured learning feeling;
- knowledge diagrams first, decorative motion second;
- consistent title/header, progress bar, subtitle, safe areas, and transition rhythm;
- brisk but readable pacing, with a clear visual payoff after questions, examples, and conclusions;
- no marketing hero pages, loud gradients, poster-like title cards, lifeless textbook-recitation boards, or unrelated decorative scenes.

Shared elements required in every project:

- top progress bar: `5px`, frame-driven, visible but quiet;
- scene title header: top-left scene index + title + subtitle/context text, with a short underline reveal;
- bottom subtitle: centered near bottom, usually a semi-transparent dark panel, `maxWidth` about `82%`, bottom around `32px`, and at most two rendered lines; for geography, follow `geography-visual-design.md` and use a light white-safe panel with deep-teal text;
- scene transition: short fade in/out, usually `10-14` frames;
- main content safe area: `left/right 90`, `top 160`, with the bottom reserve adjusted to the actual two-line subtitle panel height;
- subtitle safe area: reserve enough height for two rendered lines and avoid placing critical diagram labels, formulas, evidence, or answer steps behind that band.
- cover/opening page: a brief pre-start screen before teaching begins, with the topic as the first-viewport signal and no dense explanation;
- cover/opening page: use the dedicated hierarchy, left-right layout, topic SVG, and cover QA in `cover-design.md`;
- closing page: a final recap screen after teaching ends, summarizing the route and one concise takeaway.

## Shared Token Roles

Use a common token shape, but allow subject profiles to provide values:

```ts
export const COLORS = {
  bgDeep: string,
  bgBase: string,
  bgPanel: string,
  bgPanelSoft: string,
  textPrimary: string,
  textSecondary: string,
  textMuted: string,
  line: string,
  lineStrong: string,
  primary: string,
  primaryDeep: string,
  primaryLight: string,
  accent: string,
  accentDeep: string,
  accentSoft: string,
  success: string,
  danger: string,
  auxiliary: string,
};
```

Role rules:

- `bg*`: subject-appropriate learning surface; it may be a dark board or a white background when the subject profile requires it;
- `primary`: normal structure and current focus;
- `accent`: key judgment, conclusion, transformation point, or易错提醒;
- `success`: correct path, valid result, successful check;
- `danger`: wrong path, contradiction, invalid condition;
- `auxiliary`: secondary classification or supporting layer.

Do not make each video a completely new design. Change subject profile values deliberately; keep token names, component behavior, and layout rules stable.

## Course Energy And Mood

The default mood is a pleasant, lively study session led by a capable teacher, not a沉闷课堂 or a textbook-reading recording.

- Use friendly contrast, quick reveal, light emphasis, and clean transitions to keep attention moving.
- Prefer scene changes every time the teaching purpose changes: hook, concept, example, misconception, method, practice, and summary should feel visually distinct.
- Keep boards alive with progressive reveal, focus highlights, small motion cues, and before-after comparisons.
- Use brighter accents, gentle warmth, and occasional curiosity moments inside the subject palette, while preserving readability and academic credibility.
- Avoid long static pages of text, over-serious archive/lab/blackboard atmospheres, and slow empty holds unless students need thinking time.
- Do not chase entertainment for its own sake. Every lively motion, color shift, or reveal must clarify a concept, method, evidence path, or answer step.

## Typography

Use local CJK fonts when available:

- sans: `NotoSansSC.ttf` for body text, subtitles, labels, tables, controls;
- serif: `NotoSerifSC.ttf` for scene index, major titles, formal headings.

Recommended sizes:

- scene index: `56-72`;
- scene title: `38-48`;
- subtitle: `28-32`;
- board body text: `28-36`;
- diagram labels: `22-30`;
- small metadata: `18-22`.

For formula- and proof-dense mathematics scenes at `1920x1080`:

- primary formula: usually `46-58`;
- worked-step label: `28-34`;
- reason/explanation text: `30-36`;
- compact formula in a question header: `32-40`.

Treat these as starting points, not substitutes for rendering. Do not shrink a long derivation until it becomes technically fitted but practically unreadable; split it into semantic steps instead.

Keep text concise on screen. Put long explanation in `口播稿.md`.

For bottom subtitles, keep the approved font size and safe width stable. The complete verbatim cue may use at most two rendered lines and should use one when it fits. Do not solve a third line by shrinking the font, expanding beyond the safe area, clipping, or hiding text. Split the matching narration cue into multiple authored cues at semantic boundaries, keeping each cue identical to the script text.

## Subject Visual Profiles

### 数学

Reference: `video/数学/sets-concept/`.

- Atmosphere: dark blue teaching board / coordinate paper / formula notebook.
- Background texture: subtle grid or coordinate lines with very slow frame-driven drift.
- Palette: deep blue base, orange emphasis, green/red correctness, purple auxiliary classification.
- Visual language: structure maps, formula boards, set diagrams, number lines, coordinate systems, graphs, geometric constructions, proof flows.
- Motion: line drawing, formula step reveal, object-to-symbol transformation, graph/domain reveal.

### 语文

Use `chinese-visual-design.md` as the source of truth for the Chinese course background, local fonts, exact palette tokens, page hierarchy, cover alternatives, reading/evidence boards, worked-example pages, subtitle treatment, motion, genre adaptation, and visual QA. Its baseline is extracted from `video/语文/01-短歌行/` without copying lesson-specific content.

Keep these shared constraints:

- show selected text, evidence labels, interpretation paths, structure/theme synthesis, and answer-building steps instead of full-page paragraphs;
- rebuild information-structure images as native video elements unless the image itself is evidence or artwork students must inspect;
- bind active-line reading focus and evidence/answer reveals to authored narration cue ranges;
- use the complete worked-example sequence from `chinese-video-structure.md`, not a template-only answer card;
- show exact classical quotations and explain their source and citation function when known.

### 物理

- Use `physics-video-structure.md` for the physics teaching arc, route selection, assessment emphasis, mother-problem transfer, and semantic transition contract.
- Atmosphere: dark lab board plus real-world motion space.
- Background texture: faint measurement grid, vector field hints, motion trace lines, apparatus silhouettes when relevant.
- Palette: deep blue/charcoal base, cyan or electric blue for physical quantities, amber/orange for energy or key conclusion, green/red for valid/invalid force or motion reasoning.
- Visual language: object models, force diagrams, vectors, motion trails, v-t/a-t graphs, experimental apparatus, measurement data panels.
- Motion: object motion derived from frame, vector growth, trajectory tracing, graph line drawing, experiment step reveal.
- Stable teaching semantics: cyan/electric blue for the current object and physical quantities; amber/orange for energy, key transitions, and conclusions; green for valid reasoning; red for invalid reasoning and misconceptions.
- Visual continuity: preserve or transform the same object, vector, apparatus, trajectory, graph, law card, or misconception cue across adjacent scenes. Do not replace the whole board when only the representation changes.
- Assessment emphasis: show one current assessment label at a time and re-light the matching law, condition, or misconception during the mother-problem step where it matters.

### 化学

- Atmosphere: dark lab notebook plus macro-micro-symbol triad.
- Background texture: subtle molecular lattice, beaker/flask outline, reaction path grid; avoid decorative bubbles unless tied to particle explanation.
- Palette: deep blue/teal base, cyan/green for particles or ions, orange for reaction condition/energy/electron transfer, red for dangerous operation or wrong conclusion.
- Visual language: macro phenomenon panels, microscopic particles, symbolic equations, apparatus flow, reaction classification, electron/ion transfer arrows.
- Motion: macro-to-micro zoom, particle rearrangement, reaction path reveal, apparatus operation sequence, equation balancing step reveal.

### 生物

- Atmosphere: dark biological atlas / microscope field.
- Background texture: subtle cell membrane, tissue mesh, ecological flow lines, microscope vignette when useful.
- Palette: deep blue/green base, life green as primary, warm yellow/orange for regulation or key process, red for inhibition/disease/error, purple for genetic or molecular layers.
- Visual language: structure-function diagrams, cell/organelle labels, physiological process cycles, genetic information flow, experiment evidence chains, ecology networks.
- Motion: label reveal, process cycle progression, material/energy flow arrows, before-after comparison, evidence-to-conclusion highlighting.

### 地理

- Atmosphere: white background / clean earth-system atlas.
- Background texture: white base with low-opacity contour lines, graticule, terrain cross-section, or local map-grid traces; keep the texture subordinate to images and labels.
- Palette: deep teal/navy text on white, water/atmosphere blue, vegetation/land green, climate and human activity amber, hazard/risk red, pale blue-gray support panels.
- Visual language: source/article images, generated conceptual geographic illustrations when needed, maps, regional location, layered spatial elements, terrain/climate/water cross sections, human-land system flows, resource-transport-management diagrams.
- Motion: image crop and callout, map pan/zoom controlled by frame, layer reveal, flow arcs, cross-section build-up, raster reveal, and cause-process-result chain.
- Component route: read `references/geography-visual-design.md`; select `d3-geo`, Turf.js, GeoTIFF.js, PixiJS, Three.js, or CesiumJS by the geographic need rather than using a fixed library stack.

### 历史

- Atmosphere: dark archive / timeline wall.
- Background texture: subtle paper grain, timeline ruler, map grid, document edge; keep it quiet and modern.
- Palette: deep navy/ink base, muted gold for key turning points, blue for institutions/actors, red for conflict/crisis, green for reform/result.
- Visual language: timelines, cause networks, actor/institution maps, comparison tables, historical maps/routes, background-turning point-result-impact boards.
- Motion: timeline progression, node/link reveal, cause chain highlighting, map route tracing, before-after institutional comparison.

## Layout Patterns

Prefer these shared scene layouts, then adapt the diagram type by subject:

- overview scene: central knowledge structure map, 3-5 branches, progressive reveal;
- definition/concept scene: left intuitive example, right formal definition/rule/model;
- method scene: left step flow, right worked board or subject diagram;
- example scene: question at top, reasoning path in center, answer/check at bottom-right;
- contrast scene: wrong path and correct path side by side;
- summary scene: return to the structure map and highlight final links.

Avoid arbitrary floating elements. Arrows, labels, and objects should align to a grid or a clear visual relationship.

## Page Structure And Text Hierarchy

Every scene should have one dominant teaching focus and a small number of supporting anchors. Do not make a scene feel like a dense slide dump.

Recommended structure:

- primary board: the currently explained quote, concept, diagram, example step, or question;
- support panel: route map, key terms, evidence labels, answer path, or common trap comparison;
- bottom subtitle: narration only, not a duplicate of the whole board;
- header chrome: scene index, title, context, and global progress.

Text hierarchy rules:

- screen text should be phrase-level and task-level: selected quotes, keywords, method steps, evidence labels, and answer stems;
- keep long explanation in `口播稿.md` and subtitles, not in the teaching board;
- break dense material into progressive states, tabs, rows, or paired cards instead of showing all content at once;
- use visual grouping to make the student's eye path obvious: left-to-right for reasoning, top-to-bottom for steps, center-to-side for close reading;
- avoid placing critical body text in the bottom subtitle band.

For reading-heavy scenes, especially Chinese lessons, prefer a two-zone structure: a focused text/quote area plus a compact interpretation route or emotional/structural map. The focus area should update with the active narration segment, while the support area should keep the larger reading route visible.

## Clipping And Layering Rules

Dense educational scenes often fail because the first/middle state looks fine but the final revealed state clips or overlaps. Design for the final state first.

- Avoid placing expanding labels, cards, or text nodes against the bottom or side edge of a container with `overflow: hidden`.
- If a board needs `overflow: hidden` for a framed visual style, keep an inner padding buffer and test every revealed state.
- Do not stack a text card on top of another card unless the relationship is intentional and both remain readable.
- Keep bottom subtitles outside the main explanation band, or reserve enough vertical space so subtitles never cover key labels.
- For pages with curves, maps, timelines, or node-link diagrams, test the anchor points, labels, and callouts at multiple frames after animation completes.

## Motion Language

All motion must be Remotion frame-driven. Use `useCurrentFrame()`, `interpolate()`, `Easing`, and props such as `frame`, `progress`, and `durationFrames`.

Standard motion:

- scene fade: `10-14` frames;
- title slide/fade: `16-24` frames;
- card reveal: opacity + slight translate/scale over `10-18` frames;
- diagram line draw: `18-36` frames;
- arrow travel or highlight sweep: `20-45` frames;
- pause state: hold important conclusions long enough for students to read.

Default easing:

```ts
export const EASE_OUT = [0.16, 1, 0.3, 1] as const;
export const EASE_IN_OUT = [0.65, 0, 0.35, 1] as const;
```

Avoid spins, bounces, random particle effects, decorative loops, CSS animations, CSS transitions, autoplaying charts, and library-owned playback.

## Shared Components

Each project should implement or reuse equivalents of:

- `Background`: subject-profile background using the shared safe areas and subdued texture;
- `ProgressBar`: global frame progress;
- `SceneTitle`: scene index, title, small context text, underline reveal;
- `Subtitle`: bottom narration text;
- `Callout`: key point / warning / success / danger box;
- `DefinitionCard` or subject equivalent: term/model/process + explanation with accent rule;
- `Formula`, `Diagram`, `Map`, `Timeline`, or subject equivalent with consistent emphasis;
- timeline subtitle mapping when timed narration exists.

Keep component APIs simple and content-driven. Components should accept text/data/style props instead of baking in one lesson's labels.

## Timeline And Narration Sync

For polished videos, use one timeline source for:

- scene start/end;
- per-line narration text;
- subtitle display;
- scene animation checkpoints.

The `sets-concept` pattern uses `timeline.json` and `timeline.ts` for centralized scene, cue, and animation timing. Future projects may simplify this, but should still keep scene timing centralized rather than scattering magic frame numbers across components.

When a scene's main visual follows timed narration segments, handle pauses deliberately. During intentional gaps between subtitle segments, keep the previous meaningful visual state or show an intentional reading pause state; never flash back to a generic fallback or the first segment.

## Quality Checklist

Before finishing a video project:

- the first screen clearly belongs to the same course series, while the subject identity is visible;
- the cover follows `cover-design.md`: dominant white title on the left, concise subject/range labels, and one topic-specific SVG on the right unless an approved alternative layout is documented;
- the cover page appears before the first teaching scene and the closing page appears after the final recap;
- math videos are consistent with `sets-concept`; other subjects use their own visual profile;
- subtitles are below the main teaching board and do not cover critical labels;
- every subtitle renders in at most two lines at final resolution and matches the exact authored narration cue;
- each scene has a clear teaching purpose and at least one meaningful visual structure;
- diagrams reveal progressively rather than appearing as dense final boards;
- all motion is frame-driven and deterministic;
- text fits on 1920x1080 without overlap, clipping, or hidden final-state labels;
- color use follows the shared token roles and the selected subject profile;
- render or still checks confirm the page is nonblank and readable.
- inspect stills at the final composition resolution even when a scaled preview is used for quick review; confirm that formula commands, superscripts, fractions, and small annotations remain readable;
- for proof scenes, inspect the first operation, a middle transformation, sign analysis, and the final conclusion rather than one convenient frame;
- confirm the global progress bar and subtitles use global timing even when scene components run inside `<Sequence>` with local frames.
