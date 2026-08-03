# Physics Visual Design And Project Template

Use this reference for every `学科=物理` project in this repository. Treat
`video/物理/物理视频模板/` as the implementation source of truth. Preserve its shared
visual infrastructure and design lesson content only after analyzing the source knowledge point.

## Project Creation Contract

Create a new first-level physics project from the workspace root:

```bash
python3 scripts/create_physics_video.py "<工程目录名>" --composition-id <CompositionId>
```

- Copy the neutral template; never copy an existing lesson or run a generic scaffold.
- Keep `node_modules -> ../node_modules` as a relative symlink to
  `video/物理/node_modules` in the template and every first-level physics lesson.
- Install shared dependencies only from `video/物理/`. Never replace a child symlink with a
  real dependency directory.
- Keep direct dependency declarations in each consuming project and keep all Remotion packages
  on the same exact version as the physics root.
- Exclude `.git`, `node_modules`, `output`, `temp`, `renders`, and `.DS_Store` when creating a
  lesson. Do not keep dependency migration backups after verification.

## Template Content Boundary

- Keep only the standardized cover and closing page plus background, typography, subtitle,
  course chrome, theme, and font infrastructure.
- Keep the template free of specific concepts, quantities, laws, formulas, examples, exercises,
  assessment points, misconceptions, and chapter conclusions.
- Use neutral placeholders only in the template. Replace the title, range, cue, closing route,
  and takeaway when finishing a real lesson.
- Design all content scenes from `physics-video-structure.md`; never turn placeholder content
  pages into a generic physics slide deck.

## Canvas And Typography Baseline

- Use `1920x1080` at `30fps`.
- Use local Noto Sans SC for teaching text and Noto Serif SC for major display titles.
- Reserve at least `90px` at the left and right, `160px` at the top and bottom of the primary
  teaching stage, and the dedicated bottom subtitle band.
- Use a `168px`, weight-900 serif title as the cover baseline. Make the knowledge-point title
  the largest white element and preserve the `1.12fr / 0.88fr` text-to-diagram cover structure.
- Show the complete title hierarchy and the complete primary diagram on frame 0. Entry motion
  may add emphasis but must not make the first frame blank, partial, or structurally incomplete.
- Use `44px` as the shared scene-header baseline and `30px` as the subtitle baseline. Do not
  shrink text to conceal an overcrowded layout.
- Keep subtitles within the template's `1574px` maximum width and two rendered lines.

## Graphite Blue Physics System

Use these exact base tokens:

| Role | Color |
|---|---|
| deep background | `#101722` |
| page background | `#151A24` |
| card background | `#1C2635` |
| raised/formula panel | `#243247` |
| primary title | `#F5F7FA` |
| body text | `#D7DEE8` |
| annotation text | `#9AA6B2` |
| disabled/axis line | `#5C6678` |
| Physics Blue | `#68C3FF` |
| Guide Orange | `#FFB547` |
| Warning Red | `#FF5A5F` |

- Never use black text on the dark physics background.
- Use blue for laws, core concepts, formulas, key variables, curves, and motion paths.
- Use orange for reasoning steps, guides, process changes, and comprehension prompts.
- Use red sparingly for errors, risk, wrong directions, unit mistakes, and experiment warnings.
- Keep the overall visual ratio near 70% environment, 20% neutral text, and 10% accents; within
  accents, keep blue dominant over orange and red.
- Use blue as the default chart curve, orange as the supporting curve, red for anomalous data,
  `#5C6678` for axes, and `#9AA6B2` for ticks.
- Use `12-16px` card radii, a `#243247` border, and restrained shadow depth.

## Background Physics Texture

- Do not use a flat pure-color background. Use the template gradient plus low-opacity physical
  line texture: grid, coordinate axes, waveform, field/process curve, or vector motif.
- Keep texture opacity between 10% and 25%; preserve high contrast for teaching content.
- Place decorative axes, waves, and vectors outside the main title, teaching, diagram, and
  subtitle safety zones whenever possible.
- Do not fill the background with dense formulas or high-contrast illustrations.
- Use stable SVG ids for shared motifs and keep the texture deterministic and frame-driven.

## Diagram And Collision Rules

- Do not let lines, symbols, arrows, or labels overlap or obscure one another.
- Give every arrow shaft, arrowhead, endpoint, object, and label an explicit bounding area.
  Reserve clearance beyond both ends before placing direction text such as `v > 0` or `v < 0`.
- Place direction labels beside or above the complete arrow, never behind the arrowhead or across
  the shaft. Keep negative-direction text clear of left-facing arrowheads.
- Keep coordinate-axis labels outside arrowheads and tick marks. Align every explanation with the
  exact axis, point, interval, tangent, slope, or area it describes.
- When teaching instantaneous quantities, show the limiting interval, local tangent/state, and
  physical meaning explicitly; a generic coordinate plot without linked explanation is not enough.
- Keep one dominant diagram and one highlighted reasoning step per scene. Split the scene when
  labels, formulas, and arrows cannot retain their own readable space.
- Inspect start, middle, and fully revealed states. Check arrowhead clearance, long labels,
  formulas, coordinate annotations, bottom subtitles, and background motifs at each state.
- Treat reported red-box overlap as a layout defect. Fix geometry and spacing instead of hiding
  content, shrinking text, or merely changing z-index.

## Cover And Closing Rules

- Keep the cover hierarchy: subject label, dominant knowledge-point title, nearest chapter/range,
  short pre-start cue, and a complete topic-specific SVG on the right.
- Make the first frame useful as a static lesson cover: title and full visual structure must
  already be visible.
- Reconfigure the right-side SVG for the real lesson while preserving the template's panel,
  scale, line weight, palette, and safety margins.
- Keep the closing page focused on the lesson route, transferable takeaway, and one final method
  cue. Do not repeat all content or leave neutral placeholders in a completed lesson.

## Validation And Render Boundary

Before reporting the source project ready:

1. Run focused tests and `npm run lint` or the project's typecheck.
2. Verify every child dependency path is a symlink that resolves to `video/物理/node_modules`.
3. Run `npx remotion compositions src/index.ts` to confirm the project bundles and the
   Composition is discoverable.
4. Inspect the project in the IDE/Remotion Studio when visual debugging is requested.
5. Do not render unless the user explicitly asks. If the user asks only for a render command,
   return the command and do not execute it.

For a 4K command, keep the 1920x1080 Composition and use Remotion `--scale=2`; do not create a
separate 3840x2160 timeline. Set `--codec=h264` and `--pixel-format=yuv420p` when broad MP4
compatibility is desired, unless the user requests another codec.
