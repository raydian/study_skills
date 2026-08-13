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

Never mix deep-blue backgrounds with ink-wash semantic colors, and never keep the standard cover light field on an ink-wash project. The palette choice is part of the design spec and must be recorded in `content-design.md`.

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

Cover for ink-wash: `paper` background with a subtle ink-wash structure field (low-opacity brush/mountain/grid at `6-10%` opacity), large `ink` title, exactly one key phrase in `seal`. Subtitle band: `paper` at `88-92%` opacity with `ink` caption text and at most one `seal` keyword; do not place long small text on saturated `seal` fills.

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

Use local `NotoSansSC` for body, subtitle, labels, and tables. Use `NotoSerifSC` sparingly for the series mark or major title.

### Horizontal `1920x1080`

- left/right safe area: `90px`;
- top teaching header reserve: `130-160px`;
- bottom subtitle reserve: at least `150px`;
- title: `42-52px`;
- board body: `28-36px`;
- diagram labels: `22-30px`;
- subtitles: `28-32px`, maximum two rendered lines.
- frame-0 cover video title or topic: `88-120px`, typically no more than three lines.

### Vertical `1080x1920`

- left/right safe area: `56-72px`;
- top platform and title reserve: `150-190px`;
- bottom platform and subtitle reserve: `260-320px`;
- title: `52-64px`;
- board body: `38-48px`;
- diagram labels: `30-40px`;
- subtitles: `38-52px`, maximum two rendered lines. Default to `48-52px` when the platform and safe-area permit; enlarge the bottom reserve rather than reducing teaching text to compensate.
- frame-0 cover video title or topic: `104-148px`, typically no more than four short lines.

Do not shrink a dense horizontal board into the vertical canvas. Reduce simultaneous items and reveal them sequentially.

Use the sizes above as layout-specific tokens, not as values on one globally scaled canvas. Allow wide and vertical scenes to choose different flow direction, card count, gaps, alignment, and reveal cadence.

## Layout Pairings

| Teaching purpose | Horizontal layout | Vertical layout |
|---|---|---|
| Route map | 3-column or radial map | stacked steps or one-node-at-a-time path |
| Comparison | two panels side by side | alternating full-width cards |
| Timeline | horizontal progression | vertical milestone rail |
| Rule explanation | rule card + example panel | rule card, then example state |
| Case analysis | subject/profile left, evidence right | context header, evidence cards below |
| Evaluation matrix | compact table or radar | one criterion per card with persistent result |
| Checklist | 3-item row | 3 full-width sequential items |
| Category map | grouped columns | swipe-like category stack, frame-driven |
| Process or mechanism | horizontal flow or causal chain | vertical steps or centered layer stack |
| Data interpretation | chart plus annotation panel | chart focus followed by annotation cards |
| Subject selection 选科 | 3+3 grouped grid or subject-vs-dimension matrix; `SubjectNav` node rail on top | one subject card at a time with vertical `SubjectNav` progress dots; never show all six cards at once |

Share data and semantic order. Implement separate layout components when the reflow is materially different.

For vertical scenes, default to one primary content unit and at most one compact supporting unit at a time. Move remaining items into later frames or additional scenes.

## Cover, Hook, Subtitle, And Closing

### One-Frame Cover

- Frame `0` must be a complete, readable cover page in both formats and must last exactly one frame.
- Standard palette: use `bgDeep` with a subtle blue light field at `8-12%` opacity. Ink-wash (选科) palette: use `paper` with a subtle ink-wash structure field (brush/mountain/grid at `6-10%` opacity).
- Show the video title or topic in large `textPrimary` type as the dominant element. Ink-wash palette: title in `ink`.
- Highlight exactly one key phrase in `accent`. Ink-wash palette: key phrase in `seal`.
- Keep optional series label, category, source, and episode number visually secondary. Ink-wash palette: use `inkSoft` for secondary text.
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

- Standard palette: use `bgDeep` at approximately `88-92%` opacity. Ink-wash (选科) palette: use `paper` at `88-92%` opacity with `ink` caption text.
- Use `textPrimary` for caption text and `accent` for at most one current keyword. Ink-wash palette: `ink` text with at most one `seal` keyword.
- Keep the subtitle outside the main teaching board.
- Use identical cue text and timing in both formats.
- Display at most two subtitle lines at any frame.
- If a cue exceeds two lines in either format, split it into shorter semantic cues and show them in consecutive, non-overlapping frame ranges.
- Preserve the approved font size and spacing. Never use smaller type, condensed spacing, clipping, ellipsis, or overflow hiding as a substitute for cue splitting.

### Closing

- Return to the route map or action checklist.
- Highlight one takeaway in `accent`. Ink-wash palette: `seal`.
- Keep the next-video prompt secondary in `textSecondary`. Ink-wash palette: `inkSoft`.

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
- Confirm color roles stay consistent across all videos in the series — and that a series never mixes standard and ink-wash palettes.

## Icons, Diagrams, And Structural Backgrounds

- Use SVG icons only when they carry stable meaning: route/relationship, book/learning, graduation/profession, trend/data, checklist/action, clock/observation, warning/risk.
- Pair an icon with a short label and explanation. Never let an icon substitute for an unspoken inference.
- Prefer relationship diagrams, tiered decision structures, trend paths, before/after comparisons, and step rails over repeated empty outline cards.
- Give each core frame a visible hierarchy: conclusion is largest; explanation is secondary; evidence/action is compact but readable.
- Use a restrained `bgDeep` structural field—low-opacity grid, route, nodes, layers, or geometry—to make the frame feel intentional. Keep it low contrast and outside subtitle-safe areas. For the ink-wash (选科) palette, use a low-opacity ink-wash field (brush stroke, mountain silhouette, faint grid, or wash texture) at `6-10%` opacity on `paper`; keep it behind content and subtitles.
- For vertical subtitles, default to `48-52px` when the platform and safe area permit; enlarge the subtitle reserve rather than reducing teaching text to compensate.
