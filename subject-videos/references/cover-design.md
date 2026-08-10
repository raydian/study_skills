# Cover Design

Use this reference for the first screen of every subject video.

## Default Structure

Build the cover as a clear left-right composition inside the `1920x1080` safe area:

- left content zone: about `55%` of the usable width;
- right visual zone: about `45%`;
- horizontal gap: usually `60-90px`;
- vertically center both zones above the bottom subtitle band;
- keep key content at least `90px` from the left/right edges and outside the bottom `150px` subtitle reserve.

Use flex or grid to reserve both zones. Do not position the headline and SVG with unrelated absolute coordinates.

## Left-Side Information Hierarchy

Show three levels in this order:

1. subject label, such as `高中数学`, `高中语文`, or `高中物理`;
2. exact knowledge-point title;
3. immediate chapter, section, or knowledge range.

Rules:

- Use only the subject name in the subject label by default. Do not append generic phrases such as `核心精讲` unless the user explicitly requests them.
- Make the current core knowledge-point title the largest and first visual focus: white, very bold, high contrast, and supported by a restrained dark shadow or subject-color glow.
- At `1920x1080`, start major cover titles around `128-160px`; render and adjust by actual width. The cover title must remain visibly larger than all other page text.
- For long titles, use this fallback order: semantic line break, column-ratio adjustment, line-height adjustment, then modest font reduction. Two or, when necessary, three balanced lines are allowed. Never reduce the title to scene-title or body-text scale.
- Keep the subject label readable but secondary, usually `28-36px`.
- Keep the range line secondary, usually `34-44px`.
- Show only the nearest meaningful range, such as `函数的基本性质`. Omit textbook volume labels and chapter-number prefixes such as `必修第一册 · 第三章` unless the user requests them.
- Avoid repeating the same title in the shared scene header. A dedicated cover component may suppress the normal scene header while retaining quiet global course chrome.

## Right-Side Topic Visual Requirement

Use one subject-relevant inline SVG, deterministic vector illustration, or an approved subject-specific equivalent. It must explain or foreshadow the current course, not merely decorate the page.

Examples:

- mathematics: coordinate system, function graph, geometric construction, number line, highlighted maximum/minimum, or proof relationship;
- Chinese: selected text, imagery relationship, character/plot route, evidence-to-interpretation path, or the text-led literary composition defined in `chinese-visual-design.md`;
- physics: object, trajectory, vector, apparatus, or graph;
- chemistry: apparatus, particle change, reaction path, or macro-micro-symbol relationship;
- biology: structure-function diagram, process cycle, or information flow;
- geography: map, cross-section, circulation, or spatial flow;
- history: timeline, route, actor relationship, or cause-result structure.

Visual rules:

- Keep the graphic readable as one visual idea, with no dense board text.
- Use subject palette tokens and sufficient contrast against the background.
- Use lowered-opacity axes, grids, and guides; reserve the brightest accent for the key concept.
- Animate drawing, labels, points, highlights, and callouts from Remotion frames.
- Do not use CSS animation, CSS transition, timers, random state, or SVG-owned autoplay.
- Prefer a focused reusable cover component rather than embedding a large SVG block inside the main scene switch.

For `学科=语文`, a `video/语文/01-短歌行/`-style right-side vertical quotation, imagery pair, character pair, argument relation, or evidence cue may replace the SVG. Keep lesson-specific words configurable, supporting characters low-opacity, and the active words readable. Do not copy `建安风骨` or another lesson's topic mark into a shared component.

## Motion Sequence

Use a calm, deterministic entrance:

1. subject label fades/slides in;
2. headline enters and its shadow/glow settles;
3. range line appears;
4. SVG panel enters;
5. key SVG path draws;
6. conclusion points or labels appear.

Keep the cover alive long enough for narration, but do not add idle time. Cover motion must not change established subtitle, cue, scene-start, or total-frame timing unless the script also changes.

## Cover QA

Render a representative frame after all cover elements have appeared and verify:

- the title is the unmistakable first focal point;
- the title states the current core knowledge point and remains the largest text on screen;
- subject and range are readable at normal video viewing distance;
- the title, SVG, global chrome, and bottom subtitle do not overlap;
- the SVG directly relates to the course topic;
- the left and right zones remain visually balanced;
- the frame can be understood in about one second;
- no title line is clipped, compressed, or reduced to body-text size;
- the cover remains correct at the start, mid-entrance, and completed states.

If the user asks to enlarge the title, increase it and re-render a still. Preserve a safe gap before the SVG; adjust semantic line breaks, column ratio, and line height before reducing the title again.
