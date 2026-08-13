# Visual System

## Contents

1. Visual Character
2. Color Tokens
3. Color Semantics
4. Typography And Safe Areas
5. Layout Pairings
6. Cover, Hook, Subtitle, And Closing
7. Visual QA

## Visual Character

Use a rational, calm, modern educational style. Let deep cyan-blue establish trust and structure; use warm yellow to capture attention; use green and red only for explicit semantic states.

The mandatory one-frame cover may be bold and poster-like in hierarchy, but keep its composition restrained and educational. The hook uses a separate page and visual hierarchy. Avoid loud gradients, full-screen saturated red/yellow, decorative particles, and low-contrast text panels.

## Palette Selection

Two approved palettes. Pick one for the whole project and do not mix token sets:

- **Standard (default)**: the deep cyan-blue palette below. Use for all knowledge videos unless the topic is 选科-related.
- **Ink-Wash 水墨留白 (subject selection)**: the palette in "Ink-Wash Subject-Selection Tokens". Use for 选科-related knowledge videos — 选科科普、科目介绍、专业与选科对应、选科决策方法, and any project under the `video/选科/` category.

Never mix deep-blue backgrounds with ink-wash semantic colors. The palette choice is part of the design spec and must be recorded in `content-design.md`.

## Color Tokens

Use these values derived from `docs/design/colors.md`:

```ts
export const COLORS = {
  bgDeep: "#0F1A20",       // 墨黑
  bgBase: "#1A3A5F",       // 青黛
  bgPanel: "#2A475F",      // 黛蓝
  bgPanelSoft: "#33495E",  // 黛色
  textPrimary: "#F8F4F0",  // 荼蘼白
  textSecondary: "#C6D7DB",// 月白天青
  textMuted: "#7B8C8D",    // 云青灰
  line: "#2A5C82",         // 青蓝
  lineStrong: "#4A8DDA",   // 蓝色
  primary: "#4A8DDA",      // 蓝色
  primaryDeep: "#2A5C82",  // 青蓝
  primaryLight: "#B0D4E3", // 浅蓝
  accent: "#E6C24D",       // 鸦黄
  accentDeep: "#D4A017",   // 流黄
  accentSoft: "#F5D87E",   // 黄裳
  success: "#2AAE6F",      // 翠青
  danger: "#FF6B6B",       // 霞绯
  auxiliary: "#9B8AE8",    // 紫藤萝
};
```

Default color distribution:

- `70%` dark background and neutral surfaces;
- `20%` blue structure and current focus;
- `7%` yellow key emphasis;
- `3%` green, red, and purple semantic states.

## Ink-Wash Subject-Selection Tokens (水墨留白 · 选科)

Subject-selection (选科) knowledge videos use this restrained ink-wash palette instead of the standard deep-blue tokens above. It simulates 宣纸 (rice paper) + 墨 (ink) + 一点朱砂 (a single vermilion seal):

```ts
export const COLORS = {
  paper: "#F5F2E9",        // 凝脂 宣纸底（最大面积，≈85%）
  ink: "#31322C",          // 京元 墨色文字/主结构（正文对比≈11:1）
  inkSoft: "#595333",      // 素綦 次要文字/注释（≈7:1）
  wash: "#BEB1AA",         // 葭灰 淡墨面板/分割线（只配深字）
  seal: "#c12c1f",         // 珊瑚赫 朱砂 强调/关键结论/当前步（浅底≈5.3:1）
  sealSoft: "#E8DDD4",     // 朱砂淡晕 选中卡片底（可选）
  success: "#2AAE6F",      // 翠青 已选/符合条件（配深色文字）
  danger: "#9E3B3B",       // 绛缨 限制/误选（仅文字/描边/小面积）
  line: "#BEB1AA",         // 淡墨分隔线
  lineStrong: "#595333",   // 浓墨强调线
  auxiliary: "#595333",    // 紫藤萝语义在浅底替换为素綦墨灰
};
```

Default distribution for the ink-wash palette:

- `85%` paper and neutral surfaces;
- `10%` ink text and structure;
- `4%` seal emphasis;
- `1%` green and red semantic marks.

The ink-wash palette is intentionally restrained — 留白 is the style. Colored area must stay smaller than the standard palette.

Ink-wash color semantics (map from the standard roles below):

- Seal (珊瑚赫): direct answer, key number, decisive criterion, must-remember point, current step. The only "hot" accent.
- Ink (京元): rule, route, evidence, neutral comparison, body text.
- InkSoft (素綦): secondary dimension, alternative path, annotations, inactive items.
- Success (翠青): condition met, valid path, recommended action. Use dark text on it.
- Danger (绛缨): risk, restriction, invalid inference, misconception. Use as text/outline/small fill only — never a large filled field.
- Wash (葭灰): inactive, contextual, or not-current information. Never pair white text with wash; use ink/inkSoft text.

Cover for ink-wash follows the baseline H01/V01 dark treatment: `ink` background, large `paper` title, muted secondary copy, low-opacity paper rings, and one small `seal` accent. Frame 0 remains caption-free even though the browser layout demonstrator shows a sample subtitle strip; the production-video frame-0 rule takes precedence. Other light scenes use `paper`; their subtitle text uses `ink` with at most one `seal` keyword. Do not place long small text on saturated `seal` fills.

## Color Semantics

- Blue: rule, route, current step, evidence, neutral comparison.
- Yellow: direct answer, key number, decisive criterion, must-remember point.
- Green: condition met, valid path, recommended action.
- Red: risk, restriction, invalid inference, misconception.
- Purple: profession category, secondary dimension, alternative path.
- Gray: inactive, contextual, or not-current information.

Keep semantics stable across the whole series. Do not recolor a role for variety.

Use `danger` as text, outline, icon, or small warning fill. Do not place long small text on saturated red. Use dark text on yellow emphasis pills.

## Typography And Safe Areas

The exact baseline is `/Users/yxy/document/jay/hs_knowledge/output/高中学科科普视频-视频帧布局应用-水墨留白.html`. Use canvas-relative values from `references/page-layouts.md`; the pixel equivalents below are calculated at the final composition size and are not generic substitutes.

Use locally available `Noto Sans SC` for body, subtitles, labels, and tables. Use `Noto Serif SC` for major titles, key statements, quotations, and closing copy. Use Georgia only for Latin numerals, KPI figures, and formulas. Approved fallback stacks are:

```ts
const sans = '"Noto Sans SC", "PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif';
const serif = '"Noto Serif SC", "Songti SC", serif';
const numeric = 'Georgia, "Noto Serif SC", serif';
```

Load the chosen Noto font files from project assets before the composition is ready. Do not claim font compliance merely because `fontFamily` names a font that is not installed or loaded. Use weight `700` for dominant titles/subtitles, `600-700` for card names and key values, and `400-500` for explanations. Preserve the line-height and tracking specified by the selected H/V layout; never tighten either to make excess text fit.

### Horizontal `1920x1080`

- left/right safe area: `90px`;
- standard content inset: `6cqw = 115.2px`; layouts that specify `8cqw` use `153.6px`; never go inside the absolute `90px` safe edge;
- top teaching header: normally `5-8cqh = 54-86.4px`, with the main board commonly starting at `19-38cqh` according to its H-layout;
- teaching content ends above the subtitle footprint; keep at least `9cqh = 97.2px` clear where the selected layout uses the baseline bottom padding;
- major teaching titles: normally `4.0-4.8cqw = 76.8-92.2px`; key/section/slogan titles may use `4.6-6.4cqw = 88.3-122.9px` as specified by H01-H22;
- board body: normally `1.9-2.8cqw = 36.5-53.8px`; named values and insight conclusions may use `3.0-3.4cqw = 57.6-65.3px`;
- diagram/annotation labels: follow the selected layout and remain readable; do not use the browser-demo's placeholder SVG labels as production typography;
- subtitles: `5cqh = 54px`, weight `700`, line-height `1.3`, width `82cqw = 1574.4px`, centered at `bottom: 2cqh = 21.6px`, maximum two rendered lines.
- frame-0 cover video title or topic: `88-120px`, typically no more than three lines.

### Vertical `1080x1920`

The vertical canvas is divided into three independent zones (defined in `references/page-layouts.md`):

- **Top zone (0-17%)**: platform and title reserve; content board starts at `17cqh` (centered content at `15cqh`);
- **Middle zone (17-67%)**: teaching content board, left/right safe area `56-72px`, bottom of the board at `67%`;
- **Bottom zone (67-100%)**: dedicated subtitle zone (`633.6px` high), subtitles at `bottom: 11cqh = 211.2px`, never entered by teaching content.

Zone values:

- left/right safe area: `56-72px`;
- standard content inset: `7cqw = 75.6px`; subtitle inset: `6cqw = 64.8px`;
- content board: `top: 17cqh = 326.4px` and `bottom: 33cqh = 633.6px`; centered layouts use `top: 15cqh = 288px`;
- kicker: `3.4cqw = 36.7px`; major title: `8.6cqw = 92.9px`; body: `3.5cqw = 37.8px`; card name: `4.2cqw = 45.4px`; card description: `2.8cqw = 30.2px`;
- **vertical card-text floors** (do not render smaller): card name `≥ 42px`, card description `≥ 32px`, step/detail text `≥ 32px`, list text `≥ 46px`. Production feedback (2026-08, 选科 series) shows `26-30px` card copy reads too small on the 1080x1920 canvas;
- subtitles: `6cqw = 64.8px`, weight `700`, line-height `1.5`, left/right `6cqw`, `bottom: 11cqh`, maximum two rendered lines. This exact baseline is larger than generic mobile-caption defaults; split cues instead of reducing it.
- frame-0 cover video title or topic: `104-148px`, typically no more than four short lines.

Do not shrink a dense horizontal board into the vertical canvas. Reduce simultaneous items and reveal them sequentially.

Use the sizes above as layout-specific tokens, not as values on one globally scaled canvas. Allow wide and vertical scenes to choose different flow direction, card count, gaps, alignment, and reveal cadence.

## Layout Pairings

Every scene's page structure comes from `references/page-layouts.md`, which defines 22 horizontal frames (H01-H22) and 22 independent vertical frames (V01-V22) with layout tags L01-L20. Choose one horizontal layout and one vertical layout per scene from its mapping table, and record both tags in `storyboard.md`. The summary table below names the dominant pairings; page-layouts.md is the authoritative structure reference.

| Teaching purpose | Horizontal layout | Vertical layout |
|---|---|---|
| Series cover | H01 Cover (L01) | V01 Cover (L01) |
| Chapter / stage separator | H02 Section Break (L03) | V02 Section Break (L03) |
| Single core claim | H03 Key Statement (L04) | V03 Key Statement (L04) |
| Concept + supporting visual | H04 Concept + Visual (L05) | V04 Concept + Visual stacked (L05) |
| Term + definition + formula | H05 Definition (L19) | V05 Definition (L19) |
| Three parallel pillars | H06 3 Pillars (L07) | V06 Stacked Pillars (L07) |
| Ordered checklist / rules | H07 List Cards (L19) | V07 List Cards (L19) |
| Contrast two concepts | H08 Compare (L08) | V08 Stacked Compare (L08) |
| Ordered process / method | H09 Process Steps (L13) | V09 Vertical Rail (L13) |
| 2x2 classification | H10 Matrix (L15) | V10 2x2 Grid (L15) |
| Three key metrics | H11 Three KPIs (L11) | V11 Stacked KPIs (L11) |
| Chart + one conclusion | H12 Data + Insight (L17) | V12 Chart + Insight (L17) |
| 3-4 large conclusions | H13 Text List (L19) | V13 Text List (L19) |
| Single decisive number | H14 Hero Number (L09) | V14 Hero Number (L09) |
| Emotional quote | H15 Quote (L12) | V15 Quote (L12) |
| Four icon features | H16 Icon Features (L16) | V16 2x2 Grid (L16) |
| Old vs new view | H17 Before/After (L18) | V17 Stacked Before/After (L18) |
| Promotional slogan | H18 Slogan (L04) | V18 Slogan (L04) |
| Key parameters table | H19 Spec Sheet (L19) | V19 Spec Grid (L19) |
| Three feature spotlights | H20 Spotlights (L07) | V20 Stacked Spotlights (L07) |
| Comparative metric bars | H21 Metric Bars (L17) | V21 Stacked Bars (L17) |
| Closing / next action | H22 Closing (L20) | V22 Closing (L20) |
| Route map | 3-column or radial map | stacked steps or one-node-at-a-time path |
| Timeline | horizontal progression | vertical milestone rail |
| Rule explanation | rule card + example panel | rule card, then example state |
| Case analysis | subject/profile left, evidence right | context header, evidence cards below |
| Evaluation matrix | compact table or radar | one criterion per card with persistent result |
| Category map | grouped columns | swipe-like category stack, frame-driven |
| Data interpretation | chart plus annotation panel | chart focus followed by annotation cards |
| Subject selection 选科 | 3+3 grouped grid or subject-vs-dimension matrix; `SubjectNav` node rail on top | one subject card at a time with vertical `SubjectNav` progress dots; never show all six cards at once |

Share data and semantic order. Implement separate layout components when the reflow is materially different. Vertical page structure follows the V01-V22 definitions in page-layouts.md: a bottom third reserved for subtitles, one primary unit at a time, and stacked or sequential composition.

For vertical scenes, default to one primary content unit and at most one compact supporting unit at a time. Move remaining items into later frames or additional scenes.

## Cover, Hook, Subtitle, And Closing

The structural definitions for these pages live in `references/page-layouts.md`: cover = H01/V01 (L01 CenterStack), section break = H02/V02 (L03 Center), closing = H22/V22 (L20 CenterStack). Color and emphasis rules below apply on top of those structures.

### One-Frame Cover

- Frame `0` must be a complete, readable cover page in both formats and must last exactly one frame. Use the H01/V01 structure from `references/page-layouts.md`.
- Standard palette: use `bgDeep` with a subtle blue light field at `8-12%` opacity. Ink-wash (选科) palette: use `ink` with low-opacity `paper` rings, matching H01/V01 in the baseline.
- Show the video title or topic in large `textPrimary` type as the dominant element. Ink-wash palette: title in `paper` on the `ink` surface — the cover is **dark**; never move it to the light `paper` surface to fix an invisible title. The correct fix is a `paper` title on `ink`.
- Highlight exactly one key phrase in `accent`. Ink-wash palette: key phrase in `seal`.
- Do **not** place a series label (e.g. `选科科普 · 01`) on the cover. A cover meta line (category/source) is optional and must stay visually secondary. Ink-wash palette: use `wash` or a documented muted paper tone for secondary text on the ink surface.
- **Background texture on dark covers**: do not leave the `ink` surface flat. Add low-opacity `paper` wave-line strokes (2-3 horizontal wave paths at `rgba(245,242,233,0.10)` with 1.2-2px widths, plus a few tiny `seal` dots at `0.18-0.35` opacity) behind the content, mirroring the closing page's restrained decoration. Keep the texture subtle and behind text; it exists to avoid a monotonous single-color cover, not to compete with the title. Provide aspect-specific geometry: wide 1920x1080 paths and vertical 1080x1920 paths, never one scaled set.
  - **The cover component itself must NOT paint an opaque background** (`backgroundColor` on its root `AbsoluteFill`). The ink surface and wave texture live in the shared `SceneShell` dark branch; an opaque cover root would cover the texture and silently regress the cover to a flat single-color ink field (2026-08 real-project bug). Keep the cover root transparent, set only `color: paper` for text.
- Do not place narration or subtitles on the cover.
- Do not animate or transition the cover. Hard-cut to a separate hook page at frame `1`.

### Hook Page

- Start at frame `1` and remain visually distinct from the cover.
- Use a question, conflict, consequence, misconception, decision test, or counterintuitive fact as the dominant message.
- Use `textPrimary` for the hook and `accent` for exactly one key phrase. Ink-wash palette: `ink` hook text with one `seal` phrase.
- Use `danger` only when the hook describes a genuine risk. Ink-wash palette: use `danger` (绛缨) the same way.
- Let the hook page evolve through frame-driven supporting reveals for approximately five seconds.
- Do not repeat the cover title as the hook unless the wording and visual purpose materially change.

### Subtitle

- Match the baseline floating-text treatment: no mandatory filled rectangle behind subtitles. Use the exact mode-specific position, width, size, weight, line-height, and three-layer shadow tokens. Add a translucent surface only when the design documents a contrast failure that shadows cannot solve.
- Standard palette: use `textPrimary` for caption text and `accent` for at most one current keyword. Ink-wash light scenes use `ink` with at most one `seal` keyword; H01/V01 and H22/V22 dark surfaces invert subtitle text to `paper` (frame 0 itself remains caption-free).
- Keep the subtitle outside the main teaching board.
- Use identical cue text and timing in both formats.
- Display at most two subtitle lines at any frame.
- If a cue exceeds two lines in either format, split it into shorter semantic cues and show them in consecutive, non-overlapping frame ranges.
- Preserve the approved font size and spacing. Never use smaller type, condensed spacing, clipping, ellipsis, or overflow hiding as a substitute for cue splitting.

### Closing

- Return to the route map or action checklist.
- Highlight one takeaway in `accent`. Ink-wash palette: `seal`.
- Default closing does **not** preview the next article's title. Give one action line (e.g. `行动，从三件小事开始——答案来自证据`) in `textSecondary`. Add a next-video prompt only when the user explicitly requests one; when present it stays secondary in `inkSoft`.
- Structure follows H22/V22 (L20 CenterStack) from `references/page-layouts.md`; the vertical closing keeps the subtitle in the inverted bottom zone.

## Visual QA

- Check text contrast, including muted labels and chart annotations.
- For the ink-wash (选科) palette, verify: `ink` body on `paper` ≥ 7:1; `inkSoft` on `paper` ≥ 4.5:1; `seal` text on `paper` ≥ 4.5:1; never white text on `wash` panels — use `ink`/`inkSoft`; `danger` used only as text/outline/small fill.
- Inspect every scene at composition resolution in Remotion Studio or through non-rendering layout checks when preview is available.
- Inspect frame `0` without exporting media; reject blank, transitional, incomplete, small-title, animated, or multi-frame covers.
- Inspect frame `1`; confirm it is an independent hook page rather than the cover held or transformed.
- Confirm the cover title is the largest visual element and remains readable at phone-preview size.
- Check final revealed states, not only opening frames.
- Reject third subtitle lines, clipped cards, labels behind the subtitle band, and status colors without explicit meaning.
- Reject overlapping split cues or long subtitles squeezed into two lines by typography changes.
- Reject paragraph blocks, dense card grids, and vertical scenes with multiple competing focal points.
- Confirm wide and vertical use aspect-appropriate composition rather than a shared fixed geometry.
- Confirm every scene implements the horizontal and vertical layout tags declared in the storyboard, per `references/page-layouts.md`; vertical scenes use V01-V22 stacked/sequential structures and keep content out of the bottom subtitle zone.
- Confirm color roles stay consistent across all videos in the series — and that a series never mixes standard and ink-wash palettes.

## Icons, Diagrams, And Structural Backgrounds

- Use SVG icons only when they carry stable meaning: route/relationship, book/learning, graduation/profession, trend/data, checklist/action, clock/observation, warning/risk.
- Pair an icon with a short label and explanation. Never let an icon substitute for an unspoken inference.
- Prefer relationship diagrams, tiered decision structures, trend paths, before/after comparisons, and step rails over repeated empty outline cards.
- Give each core frame a visible hierarchy: conclusion is largest; explanation is secondary; evidence/action is compact but readable.
- Use a restrained `bgDeep` structural field—low-opacity grid, route, nodes, layers, or geometry—to make the frame feel intentional. Keep it low contrast and outside subtitle-safe areas. For the ink-wash (选科) palette, use a low-opacity ink-wash field (brush stroke, mountain silhouette, faint grid, or wash texture) at `6-10%` opacity on `paper`; keep it behind content and subtitles.
- For vertical subtitles, use the reference `6cqw = 64.8px` baseline and bottom-third zone. Do not reduce it to a generic `48-52px` setting.
