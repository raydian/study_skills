# Chinese Visual Design

Use this reference for every `学科=语文` Remotion project. The reusable course-level rules were extracted from `video/语文/01-短歌行/` into the direct implementation baseline at `video/语文/语文视频模板/`. Create new projects from the template; do not clone an existing lesson or copy lesson-specific words, imagery, diagrams, or conclusions.

## Repository Template Contract

In this repository:

- create a Chinese project with `python3 scripts/create_chinese_video.py "<工程目录名>" --composition-id <CompositionId>`;
- keep the generated `node_modules` symlink pointing to `video/语文/node_modules`;
- use `src/config/video-style.ts` for the shared canvas, safe areas, type scale, palette, subtitle, and motion tokens;
- use `src/config/template-content.ts` only for cover and closing configuration;
- reuse or extend `Background`, `CourseChrome`, `Subtitle`, `CoverPage`, and `ClosingPage` without hard-coding lesson content into them;
- keep the template's section contract as `['cover', 'closing']` and build every content scene separately from the target article;
- never replace the template or a lesson's dependency symlink with a project-local installation.

## Contents

- [Visual Identity](#visual-identity)
- [Theme Tokens](#theme-tokens)
- [Background System](#background-system)
- [Typography](#typography)
- [Page Hierarchy](#page-hierarchy)
- [Cover](#cover)
- [Reading And Evidence Pages](#reading-and-evidence-pages)
- [Worked-Example Pages](#worked-example-pages)
- [Subtitle And Course Chrome](#subtitle-and-course-chrome)
- [Motion](#motion)
- [Adaptation By Genre](#adaptation-by-genre)
- [Visual QA](#visual-qa)

## Visual Identity

Create a modern Chinese reading room: deep ink-blue teaching space, warm ivory text paper, restrained manuscript guides, and calm literary emphasis. The course should feel mature, readable, knowledge-rich, and consistent across genres without making every lesson look like ancient poetry.

Keep the shared identity stable:

- dark ink/navy course background;
- warm ivory reading and answer panels;
- serif literary text plus sans-serif teaching UI;
- muted gold for literary focus and final insight;
- blue for evidence, structure, and reasoning;
- calm, deterministic, frame-driven annotation motion.

Vary only the topic layer: right-side title mark, motif, route diagram, imagery, character, argument, or material iconography.

## Theme Tokens

Use the `01-短歌行` palette as the default Chinese course palette:

```ts
export const CHINESE_COLORS = {
  bgDeep: "#111723",
  bgBase: "#182131",
  bgEdge: "#101219",
  bgPanel: "#F6EEDB",
  bgPanelSoft: "#FFF8E9",
  textPrimary: "#F9EED8",
  textSecondary: "#D9C9AC",
  textMuted: "#9E927F",
  ink: "#1E2A3A",
  line: "#8EB1D8",
  lineStrong: "#BFD7F2",
  primary: "#6FA8DC",
  primaryDeep: "#2F6FA3",
  primaryLight: "#D7E8F7",
  accent: "#D7A955",
  accentDeep: "#B7792C",
  accentSoft: "#F4D89B",
  success: "#65B98F",
  danger: "#D76C5D",
  auxiliary: "#B7A6E6",
} as const;
```

Keep color semantics stable:

- gold: key quotations, emotional turns, literary insight, final takeaway;
- blue: text evidence, structure, link, logic, reading route;
- red: wrong answer, conflict, trap, unsupported inference;
- green: correction, valid inference, confirmed score point;
- purple: secondary classification or supporting relation;
- warm ivory: source text, question, table, worked answer, or document surface.

Do not recolor every card by category. Use color to communicate teaching state and meaning.

## Background System

Use a dark gradient base:

```css
linear-gradient(135deg, #111723 0%, #182131 58%, #101219 100%)
```

Add restrained manuscript structure:

- low-opacity vertical column guides and horizontal paragraph guides;
- a very slow frame-driven grid drift, similar to `34px` over `900` frames;
- one subtle gold vertical margin line near the left edge;
- an optional low-opacity topic mark at the right edge;
- optional paper grain or lamp warmth only when it remains unobtrusive.

Make the topic mark configurable through props or content data. It may be a vertical title, motif word, character name, argument keyword, or material label. Never hard-code `建安风骨` or another lesson-specific term in a shared background.

Allow the topic mark to be disabled on dense pages. Keep its opacity low enough that body text, diagrams, and subtitles remain the focal layer.

## Typography

Load both fonts from project-local files before rendering:

```ts
export const FONT_SANS = "Noto Sans SC";
export const FONT_SERIF = "Noto Serif SC";
```

Use `Noto Serif SC` for:

- cover title;
- poem, prose, classical quotation, and key original text;
- famous sentence, literary conclusion, and short thematic takeaway;
- restrained scene number when it supports the literary identity.

Use `Noto Sans SC` for:

- scene title and context label;
- teaching annotation, evidence label, route node, table, and diagram;
- question prompt, reasoning step, answer, and score check;
- subtitle and progress chrome.

Default 1920×1080 size baseline:

- cover title: follow the shared `128-160px` starting range; preserve the literary title as the largest and first visual focus, using semantic line breaks and layout adjustment before modest font reduction;
- scene index: around `58px`;
- scene title: around `42px`;
- key quotation or conclusion: `38-52px`;
- board body and answer step: at least `26-28px`;
- small context label: usually `22-24px`, never critical evidence;
- bottom subtitle: around `29px`, within the shared `28-32px` range.

Render and adjust by actual width. Split text at semantic boundaries before shrinking. Do not rely on a system-font fallback.

## Page Hierarchy

Use a stable four-layer hierarchy:

1. header chrome: scene number, title, short context, progress;
2. primary board: the active quotation, question, evidence group, relationship, or conclusion;
3. support board: route map, annotation, comparison, structure, or answer path;
4. bottom subtitle: exact narration only.

Use dark panels for teaching space and warm ivory panels for source documents or worked answers. This creates a visible distinction between `文本材料` and `教师分析`.

Keep cards restrained:

- low-contrast border;
- modest radius around `10-16px`;
- small or no shadow;
- no neon glow, glassmorphism spectacle, marketing-card stacks, or arbitrary floating chips.

Use gold serif scene numbers, warm-white sans-serif titles, a muted secondary subtitle, and a gold-to-transparent underline as the default scene-title pattern.

## Cover

The Chinese cover may use either:

1. a topic-specific SVG/relationship graphic; or
2. a `01-短歌行`-style text-led literary composition.

For the text-led cover:

- left: subject label, dominant serif title, and concise learning range or reading question;
- right: a vertical quotation fragment, imagery pair, character pair, argument relation, or evidence-to-interpretation cue;
- keep the right-side element topic-specific and readable as one visual idea;
- use lowered opacity for supporting characters and full contrast only for the active words;
- preserve the bottom subtitle safe area and the cover's calm pre-start state.

Do not copy a fixed prefix such as `核心精讲版`, a textbook-volume label, or the reference lesson's `建安风骨`. Follow the shared cover information hierarchy unless the user asks otherwise.

## Reading And Evidence Pages

Prefer a two-zone structure:

- primary text zone: selected line, paragraph, event, claim, or material clue in large readable type;
- interpretation zone: keyword notes, evidence-effect chain, emotion/structure route, or local conclusion.

For literary reading:

- highlight the active line until its measured narration ends;
- reveal keywords, underlines, and margin notes in narration order;
- keep non-active text visible but subordinate;
- use gold for the current literary focus and blue for the evidence path.

For structure pages:

- rebuild note diagrams as native nodes, links, curves, or cards;
- keep three to five primary branches visible at once;
- highlight completed evidence links rather than repeating every detail as text.

## Worked-Example Pages

Match the visual stages in `chinese-video-structure.md`:

1. question page: full prompt, range, task verb, and known score;
2. task-analysis page: underline task verbs and show required answer dimensions;
3. evidence page: quote the selected text and attach evidence labels;
4. reasoning page: animate evidence-to-claim paths, one path at a time;
5. answer page: build the complete answer by score point;
6. check page: mark evidence coverage, reasoning validity, duplication, and scope.

For multiple solution paths, give each path a stable lane or tab and consistent color role. End with a synthesis board showing which points merge into the final answer. Do not place an abstract formula beside an unrelated source screenshot.

## Subtitle And Course Chrome

Use the reference subtitle treatment:

- position inside the bottom safe area, around `32px` from the bottom;
- max width around `82%` of the frame;
- dark translucent background near `rgba(11, 16, 25, 0.82)`;
- thin low-opacity `lineStrong` border;
- modest `10px` radius and horizontal breathing room;
- `Noto Sans SC`, about `29px`, warm-white text;
- at most two rendered lines, with one line preferred when the complete verbatim cue fits.

Keep the subtitle separate from the primary board and reserve enough height for two lines. Split the spoken marker at a semantic boundary if it would produce a third line; do not shrink the subtitle, clip text, or expand outside the safe width.

Keep scene number, title, context, and progress consistent across the video. A dedicated cover and closing page may suppress dense header chrome.

## Motion

All motion remains Remotion frame-driven.

Preferred motion:

- calm opacity and slight translate entrance;
- gold underline drawing;
- paper panel unfolding or sliding into place;
- keyword underline and annotation reveal;
- emotion curve, character link, or argument path drawing;
- evidence-to-answer link lighting;
- wrong answer fading or crossing into a corrected form.

Keep the background drift extremely slow. Avoid bounce, spin, random particles, decorative looping light, CSS transitions, and motion unrelated to reading or reasoning.

Once audio exists, bind reading focus, keyword emphasis, reasoning steps, and answer construction to measured narration cues.

## Adaptation By Genre

Preserve the same course palette and typography while changing the topic layer:

- poetry/ci: vertical quotation, imagery web, emotional curve, restrained moon/water/mountain/plant motifs when textually relevant;
- prose: object-event route, paragraph fold, emotional line, language annotation;
- classical Chinese: manuscript strip, word/sentence board, adjusted word-order path, character/event route;
- narrative/novel: scene frame, character relation, plot curve, perspective or environment layer;
- argumentative text: claim-evidence-reasoning chain, paragraph logic, document quotation;
- expository/practical/non-continuous text: material panels, information labels, comparison grid, integration path.

Do not make modern argumentative or practical texts imitate antique poetry. The shared identity comes from color, type hierarchy, paper/ink contrast, and annotation behavior—not ornamental antiquity.

## Visual QA

At 1920×1080, render and inspect:

- the cover after all title and topic elements appear;
- the longest quotation or classical sentence;
- the densest evidence/annotation state;
- the full question prompt;
- every solution path and the final synthesized answer;
- the longest subtitle cue;
- the closing theme and method recap.

Reject the scene if:

- body or answer text falls below the readable baseline merely to fit;
- serif literary text is used for dense teaching UI;
- warm ivory text appears on warm ivory panels or dark ink text disappears into the background;
- topic marks compete with evidence or subtitles;
- the final reveal clips labels, lines, annotations, or answer points;
- subtitle produces a third line, clips, or overlaps the board;
- gold, blue, red, or green changes meaning from page to page;
- a lesson-specific background word is hard-coded into a reusable component;
- decorative motion distracts from the current reading or reasoning step.
