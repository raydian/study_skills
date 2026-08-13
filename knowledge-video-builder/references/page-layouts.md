# Page Layouts (逐帧页面布局库)

## Contents

1. Layout Tag System
2. Canvas And Safe Areas
3. Horizontal Frame Library (16:9)
4. Vertical Frame Library (9:16)
5. Frame-To-Layout Mapping Table
6. Layout Selection Rules
7. Quality Gates

This file defines the canonical per-frame page layouts for every knowledge video. It is distilled from `output/高中学科科普视频-视频帧布局应用-水墨留白.html` (2026-08) and is the single source of truth for scene structure. Horizontal and vertical layouts are **separate, independent page structures** — the vertical version is never a crop or scale of the horizontal one.

The absolute baseline source is `/Users/yxy/document/jay/hs_knowledge/output/高中学科科普视频-视频帧布局应用-水墨留白.html`. Preserve its canvas-relative geometry and typography when translating CSS into Remotion. If another skill reference or a framework default disagrees with the token values in this file, this file wins. A project may deviate only when the design explains why and the review and verification artifacts prove equivalent readability and hierarchy.

Every frame in the library is a reusable page layout. Choose layouts by teaching purpose, not by frame order. A project reuses a subset; it does not have to contain all 22.

## Layout Tag System

Each page layout has a stable tag used in `storyboard.md`, scene ids, and layout component names:

| Tag | Layout name | Tags in this file |
|---|---|---|
| L01 | CenterStack | Cover, Closing |
| L03 | Center | Section Break |
| L04 | KeyStatement / Slogan | Key Statement, Slogan |
| L05 | Split 50/50 | Concept + Visual |
| L07 | 3-Column / Spotlights | 3 Pillars, 3 Spotlights |
| L08 | Compare 2 | Two-Column Compare |
| L09 | Single KPI | Hero Number |
| L11 | Three KPIs | KPI Row |
| L12 | Quote | Quote |
| L13 | Row Steps | Process Steps |
| L15 | 2x2 | Matrix |
| L16 | Icon Row | Icon Features |
| L17 | Chart + Insight / Metric Bars | Data + Insight, Metric Bars |
| L18 | Before/After | Before/After |
| L19 | Card List / Definition / Text List / Spec | List Cards, Definition, Text List, Spec Sheet |
| L20 | CenterStack | Closing |

Use the tag in the storyboard `Horizontal visual` / `Vertical visual` columns (e.g. `L07 · 3-Pillar`), in scene ids (e.g. `scene-pillars`), and in layout component names (`PillarsLayout`, `VerticalPillarsLayout`).

## Canvas And Safe Areas

Two compositions, both at 30fps, sharing one semantic timeline and one caption set:

```text
KnowledgeWide      1920x1080
KnowledgeVertical  1080x1920
```

### Horizontal `1920x1080`

- left/right safe area: `90px`;
- standard content inset: `6cqw = 115.2px`; selected layouts use `8cqw = 153.6px`; never cross the `90px` absolute safe edge;
- standard teaching header top: `5-8cqh = 54-86.4px`; main-board start is layout-specific (`19-38cqh`);
- subtitle footprint: centered width `82cqw = 1574.4px`, font `5cqh = 54px`, weight `700`, line-height `1.3`, `bottom: 2cqh = 21.6px`; teaching content must clear it;
- subtitle shadow: `0 4.32px 12.96px rgba(49,50,44,.38)`, `0 2.16px 4.32px rgba(49,50,44,.42)`, `1.728px 1.728px 0 rgba(49,50,44,.28)` on light scenes; use the baseline black-shadow inversion on dark scenes;
- structural zones from top: header (kicker + title) → content board → subtitle band.

### Vertical `1080x1920`

The vertical canvas is divided into three independent zones, **never a scaled horizontal board**:

- **Top zone (0 - 17%)**: platform and title reserve. Content (`pv-body`) starts at `17cqh`; centered content (`pv-center`) starts at `15cqh`.
- **Middle zone (17% - 67%)**: the teaching content board, left/right safe area `56-72px` (use `7cqw`), bottom of the board ends at `67%` (`bottom: 33cqh`).
- **Bottom zone (67% - 100%)**: the dedicated `33cqh = 633.6px` subtitle zone. Subtitle sits at `bottom: 11cqh = 211.2px`, left/right `6cqw = 64.8px`, type `6cqw = 64.8px`, weight `700`, line-height `1.5`, max two rendered lines. This zone belongs to subtitles; teaching content never extends into it.
- subtitle shadow: `0 8.64px 26.88px rgba(49,50,44,.4)`, `0 4.224px 8.64px rgba(49,50,44,.44)`, `3.456px 3.456px 0 rgba(49,50,44,.3)` on light scenes; use the baseline black-shadow inversion on dark scenes.

Vertical common components (from the reference):

- `pv-kicker`: small section label, `3.4cqw`, accent color;
- `pv-title`: serif title, `8.6cqw`, up to two lines;
- `pv-desc`: body copy, `3.5cqw`, `1.9` line height;
- `pv-card`: horizontal strip card (icon/number + text) used for lists, features, specs;
- `pv-step` + `pv-step-arrow`: vertical step rail with down arrows;
- `pv-num` / `pv-kpi`: large number hero / KPI number;
- `pv-spec-row`: spec row (label left, value right);
- `pv-bar`: metric bar (name + track + value);
- `pv-chart`: chart placeholder panel;
- `pv-insight`: insight strip with accent left border;
- `pv-li`: text list item with accent dot;
- `pv-quote` / `pv-slogan` / `pv-tags`: quote / slogan / tag chips;
- `pv-col`: full-width panel for Before/After or compare columns;
- `grid2`: two-column grid (used by matrix, icon features, spec sheet); a grid header spans both columns; the last spec row spans both columns to avoid orphans.

Dark frames (cover, closing) use the `.dark` variant: ink background, paper text, subtitle inverted to paper color.

## Horizontal Frame Library (16:9)

Each entry defines the horizontal page structure only. The matching vertical page is defined independently in the next section.

### H01 · Cover (L01 · CenterStack)

- **Purpose**: emotional opening; establish series identity and the video topic in one frame.
- **Structure (top to bottom, centered stack)**: weak series label → serif title (max 2 lines, the dominant element) → subtitle line → meta line (episode/duration/year). Series label is optional and typically omitted on ink-wash covers.
- **Surface**: full ink background with low-opacity rings; one accent seal element (e.g. corner seal) as the only accent-shaped decoration. On ink-wash (选科) covers add low-opacity `paper` wave-line strokes (2-3 horizontal waves, `rgba(245,242,233,0.10)`, 1.2-2px, plus tiny `seal` dots at 0.18-0.35 opacity) behind content so the ink field is not flat; wide and vertical use independent path geometry. The ink surface + wave texture are rendered by the shared `SceneShell` dark branch; the cover component itself must not paint an opaque `backgroundColor` (it would hide the texture).
- **Emphasis**: exactly one key phrase in accent; the seal is the only accent-shaped element.
- **Typography**: label `1.6cqw` muted; title `88-120px` serif; subtitle `2.4cqw`; meta `1.5cqw`.
- **Rules**: complete and readable; lasts exactly one frame; no narration, no subtitle, no animation, no transition.

### H02 · Section Break (L03 · Center)

- **Purpose**: chapter/stage separator; a rhythm pause between major parts.
- **Structure**: weak chapter label (e.g. `第二章 · PART 02`) → oversized chapter title (serif, `6.4cqw`, letter-spaced) → short accent underline.
- **Surface**: paper background, minimal; at least `60%` whitespace.
- **Typography**: label `1.8cqw` muted; title `6.4cqw` serif.
- **Rules**: at most two information points; no cards, no diagrams.

### H03 · Key Statement (L04 · KeyStatement)

- **Purpose**: one core claim displayed as the largest element; a memory anchor.
- **Structure**: small kicker (`核心观点`) → statement text (serif, max 2 lines, `4.6cqw`) with one accent keyword → source line (`—— 来源`).
- **Surface**: paper background, optional low-opacity ring at corner.
- **Rules**: one statement per frame; exactly one accent keyword; source line muted.

### H04 · Concept + Visual (L05 · Split 50/50)

- **Purpose**: introduce a concept beside its supporting visual (diagram, chart placeholder, icon).
- **Structure**: left column (62%) = small kicker + concept title + body (max 4 lines); right column (38%) = visual panel with border, vertically centered.
- **Surface**: paper background; left text `2.6cqw` muted body; title `4.6cqw` serif.
- **Rules**: text is primary; visual supports; the visual must teach (icon/diagram/chart), not be a decorative frame.

### H05 · Definition (L19 · Definition)

- **Purpose**: term + plain definition + formula, minimal and focused.
- **Structure** (centered): term (serif, large `4.2cqw`) → definition body (max 3 lines, `2.4cqw`) → formula line (`2.8cqw`, Georgia/serif, accent).
- **Surface**: paper background, extremely few elements.
- **Rules**: term is the largest element; formula on its own line; no side panels.

### H06 · 3 Pillars (L07 · 3-Column)

- **Purpose**: three parallel pillars/principles/requirements in equal-width columns.
- **Structure**: header (kicker + title `4.8cqw`) → three equal columns: icon placeholder + name + 2-line description; one column highlighted as core (accent border + accent name).
- **Surface**: paper background; cards with thin borders and soft card fill.
- **Rules**: equal width, top-aligned, equal height; highlight at most one core pillar.
- **Implementation**: center the three columns vertically (content board `flex:1; justifyContent:center` with `maxWidth ~520px` per card) instead of an absolute `top` offset, so the pillar page sits balanced in the middle rather than too high; keep the footer above the subtitle footprint (`bottom ≥ 250px`).

### H07 · List Cards (L19 · Card List)

- **Purpose**: an ordered checklist, steps, or rule items, one card per row.
- **Structure**: header → vertical card list: each card = number circle + key term (fixed narrow column) + description; highlight the current/important card.
- **Surface**: paper; cards with generous vertical padding; accent highlights number/key of the hot card.
- **Rules**: one card per row; 3-5 cards typical; equal height; highlight at most one.

### H08 · Two-Column Compare (L08 · Compare 2)

- **Purpose**: contrast two concepts/options side by side.
- **Structure**: header → two columns: column name + 3 bullet points; the emphasized side uses the ink/dark variant (inverted surface) to create contrast.
- **Surface**: paper; emphasized column inverted (dark background, light text).
- **Rules**: exactly two columns; bullets short (`2.4cqw`); the accent is used for list dots on the light column.

### H09 · Process Steps (L13 · Row Steps)

- **Purpose**: an ordered process/method with numbered steps.
- **Structure**: header → horizontal row of 4 steps: number circle + step name + one-line description; arrows between steps; first step (or the current step) emphasized.
- **Surface**: paper; number circles bordered; arrows muted.
- **Rules**: equal spacing; at most 4-5 steps; one-line descriptions only.

### H10 · Matrix (L15 · 2x2)

- **Purpose**: a 2x2 classification/quick-reference table.
- **Structure**: header → 2x2 equal cards: icon placeholder + name + one-line description; header spans both columns.
- **Surface**: paper; equal-height cards with thin borders.
- **Rules**: exactly four cells; icons semantic; header spans the full grid width.

### H11 · Three KPIs (L11 · Three KPIs)

- **Purpose**: three key metrics as large numbers; numbers are the protagonists.
- **Structure**: header (centered) → three equal columns: big number + small unit + label below; one column accented.
- **Surface**: paper; numbers `11cqh` serif/Georgia; labels muted.
- **Rules**: same baseline; accent on the most important number only.

### H12 · Data + Insight (L17 · Chart + Insight)

- **Purpose**: a chart/visual evidence followed by a one-line insight conclusion.
- **Structure**: header → chart panel (about `55%` of board height) → insight strip with accent left border: small label + bold one-line conclusion (`3.4cqw` serif).
- **Surface**: paper; chart panel card; insight strip soft fill.
- **Rules**: one chart, one conclusion; insight text single line and unclipped.

### H13 · Text List (L19 · Text List)

- **Purpose**: 3-4 large conclusions/points where text is the only protagonist.
- **Structure**: header → vertical list of large lines (`2.8cqw`) with accent dots, separated by thin dividers; generous line spacing, no wrapping.
- **Surface**: paper background.
- **Rules**: 3-4 items; each item one line; accent dot markers.

### H14 · Hero Number (L09 · Single KPI)

- **Purpose**: a single decisive number shown at maximum size.
- **Structure**: header (centered, optional) → huge number (`14cqh`, Georgia) + accent unit → one-line context below.
- **Surface**: paper background, centered.
- **Rules**: exactly one number; unit in accent; context muted.

### H15 · Quote (L12 · Quote)

- **Purpose**: an emotional quote for opening, transition, or closing emphasis.
- **Structure**: centered: accent quote mark → quote text (serif, max 3 lines, `4.4cqw`) → source line.
- **Surface**: paper background, extreme minimalism.
- **Rules**: quote is the dominant element; at most one accent element (the quote mark).

### H16 · Icon Features (L16 · Icon Row)

- **Purpose**: four features/properties as icon cards.
- **Structure**: header → four equal feature cards: icon + name + one-line description; core feature highlighted.
- **Surface**: paper; four equal cards in one horizontal row beneath the header.
- **Rules**: four equal cards; icon meaningful; highlight at most one.

### H17 · Before/After (L18 · Before/After)

- **Purpose**: show an upgrade/transformation: old view vs new view.
- **Structure**: header → two side panels: Before (light, weak) / After (dark/inverted, emphasized), with an accent arrow between them; each panel: small tag (BEFORE/AFTER) + title + one-two-line description.
- **Surface**: paper; After panel inverted.
- **Rules**: exactly two panels; arrow direction is semantic; the emphasized side is the After.

### H18 · Slogan (L04 · Slogan)

- **Purpose**: promotional slogan page with supporting tags.
- **Structure**: centered slogan (serif, `6.4cqw`, max 2 lines, one accent keyword) + sub line + tag chips row (2-4 chips, one hot).
- **Surface**: paper background.
- **Rules**: slogan dominant; chips secondary; at most one hot chip.

### H19 · Spec Sheet (L19 · Spec)

- **Purpose**: key parameters/configuration in a table form.
- **Structure**: header → spec table: rows of label (left, muted) + value (right, bold) + unit; the core row highlighted with accent border/value.
- **Surface**: paper; table with thin dividers and card fill.
- **Rules**: label/value/unit three-level typography; highlight at most one core row.
- **Implementation**: render the whole page as a flow column (header `flexShrink:0` → table `flex:1; justifyContent:center` → footer flowing); give each row compact padding (`~18px 26px`) and set the value cell to `whiteSpace:nowrap; overflow:hidden; textOverflow:ellipsis` so a long value never wraps and overlaps the next row (production bug fixed 2026-08, 选科 series).

### H20 · Spotlights (L07 · Spotlights)

- **Purpose**: three feature spotlights with a hero symbol each.
- **Structure**: header → three equal spotlight cards: badge (e.g. `亮点 01`) + title + large symbol (letter/number, `6cqh`) + description; core spotlight inverted (dark).
- **Surface**: paper; dark variant for the core card.
- **Rules**: three equal cards; one dark inverted core; symbols semantic.

### H21 · Metric Bars (L17 · Metric Bars)

- **Purpose**: comparative performance/coverage metrics as horizontal bars.
- **Structure**: header → vertical stack of metric rows: name (fixed width) + track with fill + value (right-aligned); the leading metric accented.
- **Surface**: paper; track soft fill, rounded; fill ink or accent.
- **Rules**: name/value alignment consistent; accent on the leader only.

### H22 · Closing (L20 · CenterStack)

- **Purpose**: closing page echoing the cover; restate one takeaway and prompt next action.
- **Structure**: centered stack: small label (`结 · 语`) → serif closing quote (max 2 lines, one accent keyword) → sub line (next topic) → action button (accent fill).
- **Surface**: ink background with low-opacity ring, echoing the cover.
- **Rules**: mirrors the cover surface; exactly one accent keyword; button accent-filled.

## Vertical Frame Library (9:16)

Every vertical page is an **independent layout** composed for the 1080x1920 canvas: one primary unit at a time, stacked or sequential, with the bottom third reserved for subtitles. Never scale or crop the horizontal version. When a horizontal scene has two or three columns, the vertical version becomes stacked panels, steps, or a sequential reveal.

### V01 · Cover (L01 · CenterStack)

- **Purpose**: same as H01, composed vertically.
- **Structure** (centered in `pv-center`, starts `15cqh`): weak series label → serif title (max 4 short lines, `9.5cqw`) → subtitle/slogan sub → meta line. Series label is optional and typically omitted on ink-wash covers.
- **Surface**: ink background (`.dark`), low-opacity rings; subtitle inverted to paper. Add low-opacity `paper` wave-line strokes (2-3 waves, `rgba(245,242,233,0.10)`, plus tiny `seal` dots) with 1080x1920-specific paths so the vertical ink field is not flat. Texture comes from `SceneShell` dark; the cover component must not set its own opaque background.
- **Typography**: title `9.5-11cqw` serif; label/kicker `3.4cqw` muted; sub/meta smaller muted.
- **Rules**: title readable at phone-preview size; subtitle zone fixed at the bottom third.

### V02 · Section Break (L03 · Center)

- **Purpose**: chapter separator, vertical rhythm pause.
- **Structure** (centered): weak label → oversized chapter title (`11cqw`, letter-spaced).
- **Surface**: paper; whitespace is the dominant element; subtitle at bottom.
- **Rules**: max two elements; subtitle sits in the fixed bottom zone.

### V03 · Key Statement (L04 · KeyStatement)

- **Purpose**: one core claim, vertical stack.
- **Structure** (centered): kicker → statement text (serif, `8cqw`, max 3 lines, one accent keyword) → source line.
- **Surface**: paper background; subtitle bottom.
- **Rules**: exactly one accent keyword; statement text is the largest element.

### V04 · Concept + Visual (L05 · Split Stacked)

- **Purpose**: concept first, visual below.
- **Structure** (top-aligned `pv-body start`): kicker → concept title (`8.6cqw`) → body copy (`3.5cqw`) → visual panel below (`pv-chart`, with margin).
- **Surface**: paper; visual panel bordered.
- **Rules**: text on top, visual underneath; visual must teach; body copy compact.

### V05 · Definition (L19 · Definition)

- **Purpose**: term → definition → formula, centered vertical stack.
- **Structure** (centered): term (serif, `10cqw`) → definition body (`3.5cqw`, centered) → formula line (`4.6cqw`, Georgia, accent).
- **Surface**: paper; minimal.
- **Rules**: one term; formula on its own line; subtitle bottom.

### V06 · 3 Pillars (L07 · Stacked Cards)

- **Purpose**: three pillars as three stacked full-width cards.
- **Structure** (`pv-body`, gap `2.8cqh`): kicker + title → three `pv-card` rows: icon block + name + description; one hot card.
- **Surface**: paper; cards horizontal strips (icon left, text right).
- **Rules**: exactly one card at a time is hot; cards stacked, never a vertical 3-card grid squeezed from the wide version.
- **Typography floors**: card name `≥ 42px`, description `≥ 32px`, icon `≥ 52px`; do not render card copy smaller (production feedback 2026-08, 选科 series).
- **Implementation**: flow column container (`padding:170px 64px 640px`); header `flexShrink:0`; cards `flex:1; justifyContent:center`; footer flows — never absolute-position the header and cards separately (they overlap when the title wraps).

### V07 · List Cards (L19 · Card List)

- **Purpose**: ordered checklist, one card per row, vertical.
- **Structure** (`pv-body`): kicker + title → `pv-card` rows: number circle + key term + description; hot card highlighted.
- **Surface**: paper; generous card padding.
- **Rules**: single column; number circle left; hot card accented; subtitle bottom zone.

### V08 · Two-Column Compare (L08 · Stacked Compare)

- **Purpose**: contrast two concepts stacked vertically with a down arrow.
- **Structure** (`pv-body`, gap `2.4cqh`): kicker + title → panel A (`pv-col`) → down arrow (`pv-ba-arrow`) → panel B (`pv-col dark`); each panel: tag + title + description.
- **Surface**: paper; emphasized panel inverted.
- **Rules**: top-to-bottom flow; the down arrow is the connector; only two panels.

### V09 · Process Steps (L13 · Vertical Rail)

- **Purpose**: ordered process as a vertical step rail with down arrows.
- **Structure** (`pv-body start`): kicker + title → step rows: number circle + name + one-line description, connected by `pv-step-arrow` down arrows; first/current step emphasized.
- **Surface**: paper; number circles bordered.
- **Rules**: 4-5 steps max; arrows accent-colored; one-line descriptions.

### V10 · Matrix (L15 · 2x2 Grid)

- **Purpose**: 2x2 quick-reference, kept as a two-column grid.
- **Structure** (`pv-body grid2`): grid header (kicker + title, spanning both columns) → four `pv-card` cells (icon + name + one-line description).
- **Surface**: paper; equal-height cells.
- **Rules**: keep the 2x2 grid; the header spans both columns; four cells only.

### V11 · Three KPIs (L11 · Stacked KPIs)

- **Purpose**: three metrics as stacked number blocks.
- **Structure** (`pv-body`, gap `1cqh`): centered title → three `pv-kpi` blocks: big number (`12.5cqw`) + small unit + label; one hot block.
- **Surface**: paper; numbers serif/Georgia.
- **Rules**: one block at a time is hot; blocks stacked, not side by side.

### V12 · Data + Insight (L17 · Chart + Insight)

- **Purpose**: chart, then one insight line, vertically.
- **Structure** (`pv-body start`): kicker + title → chart panel (`pv-chart`) → insight strip (`pv-insight`): accent left border, label + bold conclusion.
- **Surface**: paper; insight strip soft fill.
- **Rules**: chart → insight → subtitle, strict vertical order; insight single line.

### V13 · Text List (L19 · Text List)

- **Purpose**: 3-4 large conclusions, vertical.
- **Structure** (`pv-body`, gap `3.4cqh`): kicker + title → `pv-li` rows: accent dot + large text (`3.9cqw`), thin dividers.
- **Surface**: paper.
- **Rules**: one item per row; items do not wrap into dense paragraphs; subtitle bottom.

### V14 · Hero Number (L09 · Single KPI)

- **Purpose**: one decisive number at maximum size.
- **Structure** (centered): kicker → huge number (`pv-num`, `15cqw`, Georgia) + accent unit → context line (`pv-num-ctx`).
- **Surface**: paper; centered.
- **Rules**: exactly one number; unit accent; context muted.

### V15 · Quote (L12 · Quote)

- **Purpose**: emotional quote, vertical.
- **Structure** (centered): accent quote mark (`pv-quote-mark`) → quote text (`pv-quote`, serif `7.6cqw`, max 3 lines) → source (`pv-quote-src`).
- **Surface**: paper; minimal.
- **Rules**: quote dominant; one accent element; subtitle bottom.

### V16 · Icon Features (L16 · 2x2 Grid)

- **Purpose**: four features as a 2x2 grid.
- **Structure** (`pv-body grid2`): grid header spanning both columns → four `pv-card` cells: icon + name + one-line description; one hot cell.
- **Surface**: paper; equal-height cells.
- **Rules**: keep 2x2; header spans columns; one hot cell.

### V17 · Before/After (L18 · Stacked Before/After)

- **Purpose**: old vs new, stacked vertically with a down arrow.
- **Structure** (`pv-body`, gap `2.4cqh`): kicker + title → Before `pv-col` (light) → down arrow → After `pv-col dark` (inverted); each: tag + title + description.
- **Surface**: paper; After inverted.
- **Rules**: Before above, After below; accent down arrow; only two panels.

### V18 · Slogan (L04 · Slogan)

- **Purpose**: slogan + tags, centered vertical stack.
- **Structure** (centered): slogan (`pv-slogan`, serif `8.6cqw`, max 2-3 lines, one accent keyword) → sub line (`pv-slogan-sub`) → tag chips (`pv-tags`, wrap, one hot).
- **Surface**: paper.
- **Rules**: slogan dominant; chips wrap centered; one hot chip.

### V19 · Spec Sheet (L19 · Spec Grid)

- **Purpose**: key parameters as a two-column spec grid.
- **Structure** (`pv-body grid2`): grid header (title spanning both columns) → `pv-spec-row` cells: label left, value+unit right; core row accented; last row spans both columns.
- **Surface**: paper; cells card-styled.
- **Rules**: keep the 2-column grid; the last row spans both columns to avoid an orphan.
- **Typography floors**: label `≥ 34px`, value `≥ 28px`, icon `≥ 34px`; grid `gap ≥ 18px`, cell padding `≥ 24px` so six cells do not look cramped.
- **Implementation**: flow column container; grid `flex:1; gridTemplateRows: repeat(3, 1fr)` for six rows; value cell `whiteSpace:nowrap; overflow:hidden; textOverflow:ellipsis` to prevent wrapping into the next row.

### V20 · Spotlights (L07 · Stacked Spotlights)

- **Purpose**: three feature spotlights, stacked full-width cards.
- **Structure** (`pv-body`, gap `2.6cqh`): title → three `pv-card` rows: icon block + name + description + big symbol right (`c-big`); core card dark inverted.
- **Surface**: paper; core card inverted.
- **Rules**: one card at a time is core; symbol right-aligned; stacked, not a squeezed 3-column row.

### V21 · Metric Bars (L17 · Stacked Bars)

- **Purpose**: comparative metrics as stacked vertical bars.
- **Structure** (`pv-body`, gap `3.4cqh`): title → `pv-bar` rows: name (fixed `22cqw`) + track with fill + value (right); leader accented.
- **Surface**: paper; tracks rounded, soft fill.
- **Rules**: name/value aligned; accent on the leader only; roomy spacing.

### V22 · Closing (L20 · CenterStack)

- **Purpose**: closing page echoing the cover, vertical.
- **Structure** (centered): small label (`结 · 语`, muted) → serif closing quote (`8.5cqw`, max 3 lines, one accent keyword) → sub line (next topic) → action button (accent fill).
- **Surface**: ink background (`.dark`), subtitle inverted to paper.
- **Rules**: mirrors the vertical cover surface; one accent keyword; button accent-filled.

## Frame-To-Layout Mapping Table

| Storyboard purpose | Horizontal layout | Vertical layout | Tag |
|---|---|---|---|
| Series cover | H01 Cover | V01 Cover | L01 |
| Chapter / stage separator | H02 Section Break | V02 Section Break | L03 |
| Single core claim | H03 Key Statement | V03 Key Statement | L04 |
| Concept + supporting visual | H04 Concept + Visual | V04 Concept + Visual (stacked) | L05 |
| Term + definition + formula | H05 Definition | V05 Definition | L19 |
| Three parallel pillars | H06 3 Pillars | V06 Stacked Pillars | L07 |
| Ordered checklist / rules | H07 List Cards | V07 List Cards | L19 |
| Contrast two concepts | H08 Compare | V08 Stacked Compare | L08 |
| Ordered process / method | H09 Process Steps | V09 Vertical Rail | L13 |
| 2x2 classification | H10 Matrix | V10 2x2 Grid | L15 |
| Three key metrics | H11 Three KPIs | V11 Stacked KPIs | L11 |
| Chart + one conclusion | H12 Data + Insight | V12 Chart + Insight | L17 |
| 3-4 large conclusions | H13 Text List | V13 Text List | L19 |
| Single decisive number | H14 Hero Number | V14 Hero Number | L09 |
| Emotional quote | H15 Quote | V15 Quote | L12 |
| Four icon features | H16 Icon Features | V16 2x2 Grid | L16 |
| Old vs new view | H17 Before/After | V17 Stacked Before/After | L18 |
| Promotional slogan | H18 Slogan | V18 Slogan | L04 |
| Key parameters table | H19 Spec Sheet | V19 Spec Grid | L19 |
| Three feature spotlights | H20 Spotlights | V20 Stacked Spotlights | L07 |
| Comparative metric bars | H21 Metric Bars | V21 Stacked Bars | L17 |
| Closing / next action | H22 Closing | V22 Closing | L20 |

## Layout Selection Rules

- Map each storyboard scene to one horizontal layout and one vertical layout from the table; record both tags in the storyboard row.
- Prefer the layout whose purpose matches the scene's teaching job. A scene with three principles → L07; a contrast → L08; an ordered method → L13; a chart with a conclusion → L17.
- If no listed layout fits, design a new layout, give it a tag, and add it to this file — do not invent an ad-hoc geometry in code and leave the library stale.
- Reuse the same layout family for sibling scenes so the series reads as one sequence (e.g. every subject scene uses L07-family cards, or every step scene uses L13).
- The vertical layout must reduce simultaneous content vs its horizontal counterpart: columns → stacked panels or sequential reveal; grids → single-column flow unless the grid is the actual teaching point (2x2 matrix stays a grid).
- Record the chosen tags in `storyboard.md`; scene ids and layout component names carry the tag so review and tests can verify the mapping.

## Quality Gates

Reject a scene when:

- the storyboard row does not name a horizontal and a vertical layout tag;
- horizontal and vertical are the same fixed geometry at different scales;
- the vertical page is produced by cropping, scaling, or shrinking the horizontal page;
- a vertical scene keeps two or three columns by shrinking cards instead of stacking or sequencing;
- the vertical content board extends into the bottom subtitle zone;
- the horizontal subtitle differs from the `54px`/`1.3`/`82cqw` baseline without an approved deviation, or a third line appears;
- the vertical subtitle differs from the `64.8px`/`1.5`/`6cqw` inset baseline without an approved deviation, or a third line appears;
- the page uses elements from a layout other than the one declared in the storyboard;
- dark pages (cover/closing) lose the inverted subtitle treatment in the vertical version;
- the final revealed state is denser than the opening state can support.
