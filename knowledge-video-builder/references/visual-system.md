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
- subtitles: `38-44px`, maximum two rendered lines.
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

Share data and semantic order. Implement separate layout components when the reflow is materially different.

For vertical scenes, default to one primary content unit and at most one compact supporting unit at a time. Move remaining items into later frames or additional scenes.

## Cover, Hook, Subtitle, And Closing

### One-Frame Cover

- Frame `0` must be a complete, readable cover page in both formats and must last exactly one frame.
- Use `bgDeep` with a subtle blue light field at `8-12%` opacity.
- Show the video title or topic in large `textPrimary` type as the dominant element.
- Highlight exactly one key phrase in `accent`.
- Keep optional series label, category, source, and episode number visually secondary.
- Do not place narration or subtitles on the cover.
- Do not animate or transition the cover. Hard-cut to a separate hook page at frame `1`.

### Hook Page

- Start at frame `1` and remain visually distinct from the cover.
- Use a question, conflict, consequence, misconception, decision test, or counterintuitive fact as the dominant message.
- Use `textPrimary` for the hook and `accent` for exactly one key phrase.
- Use `danger` only when the hook describes a genuine risk.
- Let the hook page evolve through frame-driven supporting reveals for approximately five seconds.
- Do not repeat the cover title as the hook unless the wording and visual purpose materially change.

### Subtitle

- Use `bgDeep` at approximately `88-92%` opacity.
- Use `textPrimary` for caption text and `accent` for at most one current keyword.
- Keep the subtitle outside the main teaching board.
- Use identical cue text and timing in both formats.
- Display at most two subtitle lines at any frame.
- If a cue exceeds two lines in either format, split it into shorter semantic cues and show them in consecutive, non-overlapping frame ranges.
- Preserve the approved font size and spacing. Never use smaller type, condensed spacing, clipping, ellipsis, or overflow hiding as a substitute for cue splitting.

### Closing

- Return to the route map or action checklist.
- Highlight one takeaway in `accent`.
- Keep the next-video prompt secondary in `textSecondary`.

## Visual QA

- Check text contrast, including muted labels and chart annotations.
- Inspect every scene at composition resolution in Remotion Studio or through non-rendering layout checks when preview is available.
- Inspect frame `0` without exporting media; reject blank, transitional, incomplete, small-title, animated, or multi-frame covers.
- Inspect frame `1`; confirm it is an independent hook page rather than the cover held or transformed.
- Confirm the cover title is the largest visual element and remains readable at phone-preview size.
- Check final revealed states, not only opening frames.
- Reject third subtitle lines, clipped cards, labels behind the subtitle band, and status colors without explicit meaning.
- Reject overlapping split cues or long subtitles squeezed into two lines by typography changes.
- Reject paragraph blocks, dense card grids, and vertical scenes with multiple competing focal points.
- Confirm wide and vertical use aspect-appropriate composition rather than a shared fixed geometry.
- Confirm color roles stay consistent across all videos in the series.

## Icons, Diagrams, And Structural Backgrounds

- Use SVG icons only when they carry stable meaning: route/relationship, book/learning, graduation/profession, trend/data, checklist/action, clock/observation, warning/risk.
- Pair an icon with a short label and explanation. Never let an icon substitute for an unspoken inference.
- Prefer relationship diagrams, tiered decision structures, trend paths, before/after comparisons, and step rails over repeated empty outline cards.
- Give each core frame a visible hierarchy: conclusion is largest; explanation is secondary; evidence/action is compact but readable.
- Use a restrained `bgDeep` structural field—low-opacity grid, route, nodes, layers, or geometry—to make the frame feel intentional. Keep it low contrast and outside subtitle-safe areas.
- For vertical subtitles, default to `48-52px` when the platform and safe area permit; enlarge the subtitle reserve rather than reducing teaching text to compensate.
