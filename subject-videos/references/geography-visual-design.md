# Geography Video Visual Design

Use this reference for every `学科=地理` Remotion project. Geography videos use a white background and an image-rich teaching canvas: source images, real geographic evidence, and useful generated illustrations carry the explanation, while deterministic geographic components add precise spatial structure and motion.

## Visual Contract

- Canvas: `1920x1080`, white base `#FFFFFF`; use quiet pale-blue/gray panels and low-opacity graticules, contour lines, coastlines, or raster hints as structure, never as a dark full-screen texture.
- Text: deep teal/navy for titles and body text (`#123B52`, `#0F2F3D`), muted slate for secondary labels (`#5B6B73`). Avoid pure black when a softer high-contrast teal is available.
- Semantic accents: water/atmosphere `#177EAD`; vegetation/land `#2F7D5A`; climate, population, and human activity `#C96B1F`; hazard, risk, and incorrect reasoning `#B83B3B`; pale surfaces `#F3F8FA` and `#EAF2F4`.
- Fonts: CJK-friendly sans for body/subtitle (`PingFang SC, Noto Sans SC…`), serif for display titles (`Songti SC, Noto Serif SC…`).

## Page Layout Contract (user-confirmed)

These rules were confirmed through repeated user feedback and apply to every geography project:

1. **One page = one image, full-bleed.** Each image scene shows exactly ONE source figure. Render it as `<Img>` stretched over the whole 1920×1080 canvas with `object-fit: contain` (centered, never cropped, legend/scale/north-arrow/labels stay intact). No card border, radius, or box shadow around the image — it is the page, not a card on the page.
2. **Image pages have no chrome header.** No scene index, no scene title, no progress bar on an image page. The top of the canvas is the image itself. Avoid the PPT-style "title bar + figure + subtitle bar" three-band structure.
3. **Non-image pages get a title header.** Concept, misconception, worked-example, comparison, and closing pages render the standard chrome header (scene index + title + context + progress bar) so the viewer always knows which page they are on.
4. **Subtitle floats on top of the image.** The bottom subtitle is a translucent light panel — `rgba(255,255,255,0.85)` background, rounded corners, thin cool-gray border, soft shadow — placed over the image's bottom edge. The user explicitly allows subtitles to cover the image.
5. **Panel translucent, text opaque.** The subtitle *background* is semi-transparent (alpha ≈ 0.85); the subtitle *font* is fully opaque deep teal (`#123B52`, weight 700, `textShadow: 0 1px 3px rgba(255,255,255,0.85)`). Never set opacity on the text layer itself.
6. **Geography subtitles may use up to three rendered lines** to carry annotation-based detail (the global two-line cap is relaxed for geography). Verify the third line in an actual render; do not let it climb toward mid-image content.
7. **Detailed, annotation-driven narration.** Every image scene gets 5–7 narration/subtitle cues, not one or two. Cue text comes from the source note's figure annotation (图注): narrate every element, legend, label, arrow, callout, and data value the image shows (e.g., "月地距离约38.4万千米", "太阳距银河系中心约2.6万光年", "一拳约10°", "碎片监测→轨道规避→主动清除→寿命末端离轨"). Cues of 40–55 characters render as ~2 lines; scale scene durations (roughly 35–45s per image scene) so each cue gets reading time.
8. **Avoid adjacent-scene image reuse.** If two adjacent scenes would show the same source image, do not reuse it. Either pick a different image for the second scene or convert it into a text page (comparison cards, causal chain, summary board) that carries the concept without the picture.
9. **First frame is the cover.** The cover is scene 0 and must read as a cover at frame 0: subject label + large display title are visible immediately (no fade-in); secondary elements (range line, right SVG, bottom pre-start bar) fade in shortly after; the bottom bar shows the pre-start state ("即将开始 · 章节 · 核心精讲版") with the same translucent-panel style.
10. **Text-page typography stays large and non-overflowing.** Misconception cards ≈ 24/28px, worked examples ≈ 24/33/34px, card height ≈ 148px, spacing ≈ 160–170px so four stacked cards end above the subtitle band. Big display sizes are reserved for cover/hook/closing.
11. **IDE timeline segmentation.** Wrap every scene that has a component in `<Sequence from={start} durationInFrames={duration} name={title}>` so Remotion Studio's timeline shows one segment per scene (readable, seekable). Scene-local frames come from `useCurrentFrame()` inside the sequence; global chrome/subtitle lookups use the global frame. Keeps the flat 10k-frame strip from hiding the scene structure.
12. **Grid only on text pages.** The faint graticule background renders only behind non-image pages; image pages get a clean white canvas so the full-bleed figure is uncluttered.

## Image-First Material Strategy

Before writing the storyboard, inventory the source note/article for:

- article photographs, satellite or remote-sensing images, maps, charts, climate diagrams, terrain profiles, and other visuals that show the place or process;
- the image's source, caption, legend, orientation, date, and whether it is suitable for direct display;
- **the specific knowledge point each image actually explains** — its labels, legend, arrows, callouts, and built-in annotations, not just its topic;
- missing visual links: spatial relations, scale, terrain form, atmospheric process, human-land interaction, or before/after change that the text cannot make clear.

Use a source image as a teaching element when students need to inspect the actual place, pattern, evidence, map, chart, landscape, or process. Copy it to `public/images/` and reference it with `<Img>` and `staticFile()`. Keep the source credit/provenance in `content-design.md` or `storyboard.md`; do not silently detach an image from its article context.

### Source Image Integrity Rules

When a source image is chosen, three integrity rules apply on top of provenance:

1. **Preserve the explanatory completeness of the image.** A source image is a teaching artifact with its own legend, labels, scale bar, north arrow, annotations, and surrounding caption that together form its explanation. Do not crop away the parts that carry meaning. Full-bleed `contain` display keeps every element; if a crop is ever necessary for focus, keep every element the narration relies on (legend, axis, label, arrow, scale) inside the visible frame. Never trim an image down to a decorative fragment that loses the original teaching context.
2. **Use source images as static material, never as motion.** Display an article image as a static inspected visual. Do not fake animation by cycling, flipping, jittering, panning across, or sequencing still images to simulate a GIF or moving picture. Motion in a geography scene comes from deterministic Remotion frame-driven layers (overlays, route traces, layer reveals, cross-section construction, raster reveals) drawn on top of a stable image — never from animating the image itself. If a process genuinely needs to move, generate it with a frame-driven component, not by treating photographs as frames.
3. **Match the image's knowledge point to the narration, not just its topic.** Before placing an image, confirm that the exact concept, region, process, or relationship the image explains is the one being narrated in that scene. Do not drop in an image because it is topically related, looks relevant, or fills an empty board. If an image shows a different sub-point, time, scale, or region than the current cue, either move the image to the scene where that content is taught, supplement it with overlays that bridge to the narrated point, or do not use it. Record the matched knowledge point beside the image reference in `storyboard.md` so the alignment is auditable, not implied.

### Generated-Image Fallback

If a suitable source image is unavailable and a text-only board would leave the geography unclear, call `image-gen` to create a conceptual teaching asset. The prompt should state the place/process, viewpoint, season or time, visual purpose, orientation, and any exclusions. Record the prompt and role beside the asset. Generated imagery may explain a landform, atmospheric process, landscape, or human-land scene; it must not invent exact coastlines, borders, measurements, statistical values, or map labels. For exact spatial claims, use verified data and deterministic overlays on top of the generated or source image. The three integrity rules above (completeness, static use, knowledge-point match) apply to generated images as well.

### Open-Source Component Alternative

When a source image is not used as the video material — because none matches the narrated knowledge point, because the needed spatial relationship cannot be shown by a static picture, or because the teaching point is itself a process the image cannot carry — generate the visual with an open-source geographic component instead of forcing an ill-fitting image. See **Geographic Component Selection** below. A frame-driven generated component is preferred over a loosely-matched source image whenever the image does not actually explain the current knowledge point. Mixing is allowed: a source image may provide real-world evidence while a generated component supplies the spatial structure or process the image cannot show.

Default image density:

- Every core teaching scene has at least one inspectable geographic visual: source image, generated illustration, map, chart, cross-section, raster, or spatial animation.
- Prefer a change of image, crop, layer, or visual state every `20-40` seconds of explanation when the content supports it. Do not add decorative images that do not advance the knowledge point.
- Keep one dominant visual on screen; full-bleed means the figure is the whole page. Do not pile side panels or captions next to it — explanation belongs in the subtitle + narration.

## Geographic Component Selection

Select the least complex tool that makes the spatial idea clearer. Do not install or combine all libraries by default.

| Need | Preferred tool | Frame-driven use |
| --- | --- | --- |
| Projection, graticule, GeoJSON boundaries, thematic map, route overlay | `d3-geo` | Recompute deterministic paths or reveal layers from `frame`/`progress`. |
| Buffer, centroid, distance, intersect, route, spatial relationship | Turf.js | Precompute geometry where possible; animate only authored highlights or paths. |
| Elevation, terrain, globe, atmosphere, 3D cross-section | Three.js | Disable its clock/render loop; render the camera/object state from the Remotion frame. |
| Globe-scale terrain, time-varying 3D geographic context | CesiumJS | Use only when a flat map or SVG loses the required scale; freeze interaction and camera clocks. |
| GeoTIFF climate/elevation/remote-sensing raster | GeoTIFF.js | Decode/sample deterministically or preprocess; reveal raster/contours from frame state. |
| Many wind, current, rainfall, migration, or transport particles | PixiJS | Disable the ticker and generate particle positions from a seeded function of frame. |

Use SVG/React for precise labels, legends, arrows, boundaries, sections, and overlays even when a library supplies the base geometry. Avoid network map tiles in rendered lessons; package verified local data/assets so the same frame renders the same way offline.

## Teaching Patterns

- `ImageEvidence`: show the source/generated image full-bleed, then let each narration cue walk a specific element of it (legend, arrows, labels, data) — no separate side panel.
- `RegionMap`: establish location, scale, orientation, neighboring regions, and the spatial pattern before explaining causes.
- `LayeredThematicMap`: reveal one verified layer at a time; keep the legend and color meaning visible.
- `ProcessCrossSection`: move from landscape photograph or map to terrain/climate/water/urban cross-section, then to cause → process → result.
- `RasterToMeaning`: reveal a GeoTIFF/remote-sensing layer, sample or compare regions, and connect the pattern to the narrated geographic concept.
- `HumanLandSystem`: connect resource → production → transport → settlement/management → impact with a map, flow arcs, and real images.
- `GlobeToRegion`: use a globe or 3D terrain only when scale or relief matters; preserve the same region anchor when transitioning to a flat map.
- `ComparisonTextPage`: when a concept is a contrast (普通 vs 特殊, before vs after), or when the adjacent scene already used the only fitting image, use a text page — two labeled cards + a causal chain — instead of reusing the image.

## Geographic Continuity And QA

For each scene, record `visualCueId`, source/generated asset, projection or viewpoint, legend, geographic claim, **and the narrated knowledge point the asset is matched to**. Keep north/up, scale, region framing, and semantic colors stable across adjacent cues unless the change is taught explicitly.

Before completion:

- inspect the source image and final framing for orientation, legend, labels, attribution, and readability; full-bleed `contain` must keep every element the cue references inside the visible frame — no legend, scale bar, axis, label, or annotation lost;
- verify the source/generated image is shown statically and is not being cycled, flipped, jittered, or sequenced to fake motion; confirm any visible motion comes from frame-driven overlays or component state on top of the stable image;
- verify that each placed image actually explains the knowledge point narrated in its scene (same region, process, scale, time, and relationship), not merely a topically related picture; check the matched knowledge point recorded beside the image reference in `storyboard.md`;
- verify generated images are conceptual and that exact data/boundaries come from verified local data or deterministic overlays;
- render start, middle, and end frames for map pan/zoom, layer reveal, cross-section, raster, particle, globe, and image-crop scenes;
- confirm no library ticker, timer, autoplay, interaction, requestAnimationFrame loop, or network tile changes the result outside Remotion frame control;
- check white-background contrast, subtitle legibility, safe areas, label/legend clipping, and subtitle overlap;
- **occlusion check**: render a still for every scene that places an image, and confirm nothing opaque — decorative shape, progress bar, logo, or panel — covers the image legend, scale bar, north arrow, axis, label, arrow, callout, or chart pattern. The floating subtitle panel is translucent by design and may sit on the image's bottom edge, but its footprint must not fully bury a critical legend/label: if a legend lives exactly where the panel lands, narrow the panel or shift the image's vertical framing inside `contain` bounds;
- **layout check**: confirm image pages are full-bleed with no chrome; text pages show the chrome title header; text-page cards/boards end above the subtitle band with no overflow;
- **subtitle check**: subtitle background is semi-transparent (`rgba(255,255,255,0.85)`), subtitle text is fully opaque deep teal (weight 700 + text shadow); render the longest cues and reject any fourth line, clipped text, or overlap with mid-image content;
- compare every subtitle cue verbatim with `口播稿.md`, keep every cue inside its scene boundary, and give every image scene 5–7 cues;
- confirm the cover reads as a cover at frame 0 (subject label + big title immediately visible) and that `<Sequence>` segmentation shows each scene in the IDE timeline.
