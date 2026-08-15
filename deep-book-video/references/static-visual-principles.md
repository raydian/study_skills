# Static full-screen visual principles

## Format assessment

The format is viable: static full-screen AI images can give each cognitive beat a memorable setting, while large subtitles make the video usable without sound. Its weaknesses are structural and must be designed around.

| Inherent weakness | Failure mode | Fixed remedy |
|---|---|---|
| no motion | mechanisms, chronology, and proof feel inert | split reasoning into successive static states; one page per change |
| image and subtitle compete | viewer cannot inspect art and read text at once | give the image one focal point and reserve a low-detail text-safe zone |
| subtitle-first presentation | transcript-sized text overloads working memory | subtitle only the cognitive anchor; let voiceover carry explanation |
| AI factual hallucination | invented costumes, places, charts, quotations, anatomy | treat image as illustration; add era/culture and realism constraints; verify renders |
| visual monotony | repeated centered portraits and metaphors flatten rhythm | vary scale, viewpoint, visual function, and light within one visual bible |
| style drift | recurring people/places change across pages | write continuity anchors and reuse stable character/environment descriptions |
| exact information in raster art | malformed text, numbers, equations, and data | prohibit generated text/data; place sourced exact information in overlays |
| subtitle placement after generation | text covers faces, hands, or focal evidence | specify safe zone and crop safety inside every image prompt |
| static pacing | pages become either rushed or stagnant | derive duration from voiceover and reading load; use hard cuts at reasoning changes |
| accessibility | color-only emphasis or insufficient contrast excludes viewers | use contrast, weight, scrim, line breaks, and non-color cues |

## Separation of responsibilities

```text
evidence → what may be claimed
voiceover → reasoning and nuance
subtitle → current cognitive anchor
AI background → atmosphere, situation, metaphor, or spatial orientation
```

An AI background may depict a labeled reconstruction only in production metadata. It may not establish a historical event, scientific observation, statistical value, quotation, or visual analysis of the original book.

## Subtitle system

For a 1920×1080 master:

- use a CJK-capable sans-serif font such as Noto Sans CJK SC or Source Han Sans;
- use 64–84 px for normal subtitles and 84–112 px for very short thesis cards;
- use weight 700–900;
- use 1–3 lines, normally no more than 20 Chinese characters or 42 Latin characters per line;
- keep total subtitle text near 12–48 Chinese characters; split the page when it cannot fit naturally;
- target WCAG-style local contrast of at least 7:1 for primary text;
- use a solid or semi-opaque scrim when the image cannot guarantee stable contrast;
- keep at least 5% horizontal and vertical title-safe margins; keep mobile crop safety when required;
- never communicate a distinction by color alone.

Subtitle text may be a claim, contrast, question, definition, step, or conclusion. It is not a verbatim transcript field. Punctuation and line breaks should expose syntax rather than create decorative fragments.

## Timing

- Default page duration: 6–16 seconds; use 4–6 seconds only for very short hooks or transitions.
- Target Mandarin voiceover: roughly 3.5–5.0 Chinese characters per second after punctuation and pauses.
- Give dense definitions, evidence qualifications, unfamiliar names, equations, and quoted text more time.
- If voiceover, subtitle, and image each introduce a different new idea, split the page.
- Change page on a reasoning move, not on a fixed timer.

## Image-prompt construction

Each `image_prompt` contains both structured direction and one assembled `rendered_prompt`. Specify:

1. subject and exact state/action;
2. setting and relevant era/culture;
3. art direction and degree of realism;
4. palette and light tied to the visual bible;
5. lens/camera, scale, and viewpoint;
6. composition and focal hierarchy;
7. symbolic elements, each justified by the page;
8. continuity anchors for recurring people/places/objects;
9. exact safe-text zone as a percentage or named region;
10. realism constraints and known uncertainties;
11. negative prompt forbidding text, letters, numbers, titles, logos, watermarks, frames, anatomy defects, and clutter in the safe zone;
12. aspect ratio and crop safety.

Do not ask the image model to draw the subtitle. Generate clean art, then apply subtitles in the video layout system.

## Visual functions

Choose one primary function per page: `situate`, `concretize`, `model`, `contrast`, `evoke`, `orient`, `characterize`, `symbolize`, or `rest`. A beautiful image with no explanatory or emotional job is not a valid page design.

For diagrams, equations, timelines, or quantitative comparisons, use successive static composition states or deterministic overlays in final production. Because this skill's background remains AI-generated, the background must not contain exact labels or values.

## Source-image and Studio review

After images exist, inspect the source files at full size and the full composition in Remotion Studio at desktop and phone-preview sizes. Do not render a still or video for this review. Reject or regenerate when:

- the safe zone contains a face, hand, bright edge, high-frequency texture, or focal object;
- the subtitle requires outline-only treatment to remain readable;
- hands, eyes, architecture, period clothing, maps, instruments, or scientific objects are wrong;
- a recurring character or object loses continuity;
- accidental text, logo, signature, number, or watermark appears;
- the image asserts more certainty than the evidence supports;
- the image aestheticizes violence, trauma, religion, or identity in a misleading way.
