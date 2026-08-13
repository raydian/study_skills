---
name: knowledge-video-builder
description: Convert Chinese knowledge articles, notes, rules, methods, concepts, processes, comparisons, data, and cases into complete, video-native Remotion explainer projects with synchronized 16:9 and 9:16 compositions and subtitles. Use for 知识类视频、文章转视频、知识讲解、科普、规则解读、方法教程、概念解释、案例分析，或需要第 0 帧独立大字体封面、第 1 帧起独立钩子、分层讲清楚、SVG 图标/关系图、结构化背景、语义化转场和横竖版独立自适应布局的视频工程。选科类知识讲解（选科科普、科目介绍、专业与选科对应、选科决策方法）默认使用水墨留白配色方案（见 visual-system.md 的 Ink-Wash tokens）。必须按七阶段门禁执行；字幕最多两行，过长内容拆到不同播放帧；不生成配音，不自动渲染。
---

# Knowledge Video Builder

Create one repeatable Remotion knowledge-video project from one article, note, chapter, or structured source. Build separate horizontal and vertical layouts from shared content, subtitles, scene ids, and authored timing.

## Read The References

Read all nine references before creating a project:

- `references/workflow-gates.md`: mandatory Superpowers stage order, artifacts, and gates.
- `references/content-design.md`: separate cover and hook, narrative routes, scene structure, and teaching language.
- `references/visual-system.md`: approved palette, typography, layouts, and 16:9/9:16 adaptations.
- `references/page-layouts.md`: canonical per-frame page layouts — 22 horizontal (H01-H22) and 22 vertical (V01-V22) independent page structures, layout tags L01-L20, and the frame-to-layout mapping table.
- `references/motion-layout.md`: text-density limits, progressive reveals, semantic transitions, and adaptive wide/vertical layouts.
- `references/transition-playbook.md`: concrete SceneTransition wrapper, slide relay, matched-element continuity anchors, one-way staggered reveal, and transition safety budget for smooth scene and storyboard changes.
- `references/dual-format-contract.md`: shared subtitle, timeline, and composition contract.
- `references/project-structure.md`: project files, implementation boundary, proven implementation blueprints, validation, and completion report.
- `references/compliance-checklist.md`: final Stage 6 conformance pass for subtitles, motion, colors, and layout structure, with the fix-and-recheck loop.

## Non-Negotiable Boundaries

- Create every project under `/Users/yxy/document/jay/hs_knowledge/video/<内容分类>/<编号-主题>/`. Omit the number only when the source has no stable sequence.
- Execute these stages in order without skipping or merging: `Brainstorm → Plan → Task Breakdown → Implementation → Review → Testing → Complete`.
- Do not write Remotion production code before the Brainstorm, Plan, and Task Breakdown gates pass.
- Load `$remotion-best-practices` before designing layouts or writing Remotion code. Also load its `rules/display-captions.md`, `rules/timing.md`, and `rules/transitions.md` references. (That skill has no `rules/video-layout.md` or `rules/subtitles.md`; layout and subtitle limits are defined by this skill's `references/visual-system.md` and `references/motion-layout.md`.)
- Create video code, visual assets, authored timing, and subtitles only.
- Do not call a TTS or voiceover skill. Do not create, download, synthesize, measure, or embed narration audio.
- Do not run `remotion render`, `remotion still`, FFmpeg export, or any equivalent render command automatically.
- Render only after the user gives a separate, explicit render instruction. Rendering is outside this creation workflow.
- Frame `0` is a complete standalone cover shown for exactly one frame. It has no narration, subtitle, or animation.
- Frame `1` hard-cuts to a separate hook page for approximately five seconds.
- Create `1920x1080` and `1080x1920` compositions at `30fps` from one shared semantic timeline and one subtitle dataset.
- Reflow meaning into aspect-specific layouts. Never crop or mechanically shrink the horizontal composition to produce the vertical version.
- Treat `/Users/yxy/document/jay/hs_knowledge/docs/design/高中学科科普视频-视频帧布局应用-水墨留白.html` as the baseline layout specification. `references/page-layouts.md` is its implementation contract; when prose or a generic Remotion default conflicts with that reference, the page-layout token table wins. Record any intentional project-specific deviation in the design, review, and verification artifacts.
- The ink-wash (选科) cover is a **dark surface**: H01/V01 use `ink` background with large `paper` title, exactly one `seal` key phrase, and one small seal accent. Never "fix" a dark cover whose title is invisible by switching the cover to the light `paper` surface — the correct fix is a `paper` title on `ink` (see `references/visual-system.md`). Do not place a series label such as `选科科普 · 01` on the cover; cover meta line is optional and stays secondary.
- The ink surface and its wave-line texture are rendered by the shared `SceneShell` dark branch. **The cover component itself must not paint an opaque `backgroundColor` on its root `AbsoluteFill`** — an opaque cover root would cover the wave texture and silently regress the cover to a flat single-color ink field (real-project bug fixed 2026-08, 选科 series). Keep the cover root transparent, set only `color: paper` for text. The same applies to any other dark-surface layout component (e.g. closing).
- The closing page (H22/V22) does **not** preview the next article's title by default. It restates one conclusion and gives an action line (e.g. `行动，从三件小事开始`) instead. Preview the next topic only when the user explicitly asks for a next-video prompt.
- Choose every scene's page structure from `references/page-layouts.md`: one horizontal layout (H01-H22) and one independent vertical layout (V01-V22) per scene, recorded as layout tags in `storyboard.md`. The vertical page is an independent stacked or sequential composition for the 1080x1920 canvas, never a scaled or cropped horizontal board.
- Keep each frame focused on one main message. Move secondary information into later frames, animation states, or additional scenes instead of stacking paragraphs and dense cards.
- Do not reduce an explanatory article into title-only cards. Each core teaching scene must carry a conclusion, a short explanation, and an evidence, consequence, comparison, example, or action cue.
- Use readable HTML/SVG as needed for explanation; short explanatory text is required when an icon or diagram alone cannot teach the point.
- Use meaningful, reusable SVG icons, relationship diagrams, trend marks, checklists, or paths where they clarify the concept. Do not rely on homogeneous outline cards or decorative lines as the primary information carrier.
- Give backgrounds restrained structural depth: low-contrast grids, routes, nodes, layers, or context shapes may support hierarchy, but must stay behind teaching content and subtitles.

## Content Contract

- Extract one core learning question, one direct answer, two to four key ideas, one representative example or case, and one takeaway or action.
- Do not narrate the source paragraph by paragraph.
- Let complexity determine duration. Most focused explainers should be `3-5` minutes, using authored cue durations that remain independent of audio.
- Tie time-sensitive claims to source, version, region, and date when relevant. Mark illustrative data and composite cases clearly.
- Keep `口播稿.md` as an editorial script for future human or external voice production, but do not turn it into audio in this workflow.
- Store subtitles as JSON using the Remotion `Caption` shape. The same cues and timing drive both compositions.
- Limit every visible subtitle cue to at most two lines in both compositions. If either layout would exceed two lines, split the text at semantic boundaries into multiple cues and assign them to consecutive, non-overlapping playback frame ranges.

## Implementation Contract

- Scaffold an empty project with the command prescribed by `$remotion-best-practices` when no suitable project exists.
- Keep content, subtitle data, scene ids, and timing shared; keep aspect-specific layout components separate.
- Use adaptive layout tokens for safe areas, gaps, typography, column count, orientation, and simultaneous item count. Wide and vertical layouts may share data and primitives but must not share one fixed page geometry.
- Name layout components after the page-layouts tags (e.g. `PillarsLayout` / `VerticalPillarsLayout` for L07, `CompareLayout` / `VerticalCompareLayout` for L08) so the storyboard mapping is directly inspectable in code.
- Give vertical scenes a dedicated bottom subtitle zone (bottom third of the 1080x1920 canvas) and keep teaching content out of it; subtitles use the reference baseline `6cqw = 64.8px` there. Do not silently substitute smaller generic subtitle defaults.
- Vertical scene containers use **flow layout** (flex column with `padding: 170px 64px 640px` and header `flexShrink:0`, content `flex:1`, footer flowing), never absolute-positioned stacks of header + content that overlap when a two-line title grows (see `references/motion-layout.md`). Vertical card text must meet the vertical token floors: card name `≥ 42px`, description `≥ 32px` (baseline `4.2cqw`/`2.8cqw`); do not render card copy smaller than that.
- Wide scene content boards center vertically (flex column with content `flex:1` + `justifyContent:center`) instead of absolute `top` offsets, so three-pillar pages do not sit too high; keep footer above the subtitle footprint (`bottom ≥ 250px` on the 1080-high canvas).
- Drive animation with `useCurrentFrame()`, `interpolate()`, and deterministic Remotion primitives.
- Use motion to reveal, compare, connect, transform, emphasize, or sequence information. Use scene transitions to communicate continuity or topic changes, not as decoration.
- Implement smooth scene changes with the shared patterns in `references/transition-playbook.md`: one SceneTransition wrapper per scene (paired enter/exit fades for cross-fade), slide relay for ordered sibling scenes, a matched-element continuity anchor across each multi-scene series, and one-way staggered reveals.
- Do not use CSS transitions, CSS animations, or Tailwind animation classes.
- Keep assets in `public/` and reference local assets with `staticFile()`.
- Display readable text as HTML or SVG overlays, not inside generated imagery.
- Give `SubtitleBand` an explicit readable text color and font; never rely on inherited color from a sibling background container.
- Implement the exact baseline typography roles: `Noto Sans SC` for body/subtitles/labels/tables, `Noto Serif SC` for major titles and quotations, and Georgia for Latin numerals/formulas where specified. Load the actual font files before rendering; a CSS family name without an available font is not compliance.
- Register semantic scene `Sequence` blocks with human-readable names so Remotion Studio provides a useful, navigable timeline. Do not promise automatic thumbnail strips for pure code-generated scenes; Studio shows structural scene ranges rather than NLE-style video thumbnails.
- Reserve subtitle-safe areas and keep each visible subtitle cue within two lines in both formats.
- Split overlong subtitles across different playback frames. Do not force text into two lines by shrinking below the approved subtitle size, tightening letter spacing, clipping, masking, scaling, or hiding overflow.

## Completion Definition

Mark the creation workflow complete only when:

- all seven stage artifacts exist and their gates passed;
- the source, content design, storyboard, script, captions, and timeline agree;
- both compositions load through non-rendering checks and share fps, duration, scene ids, and captions;
- code review has no unresolved Critical or Important issues;
- required tests, typecheck, lint, caption-schema checks, and timeline checks pass;
- the Stage 6 compliance pass in `references/compliance-checklist.md` was run covering subtitles, motion, colors, and layout structure; every failed item was fixed and the full suite re-run — checks are never weakened to match the code;
- deterministic subtitle-fit checks prove that every cue stays within two lines in both layouts;
- every storyboard scene names a horizontal and a vertical layout tag from `references/page-layouts.md`, and the implemented components match those tags;
- layout review confirms that vertical scenes contain fewer simultaneous elements and use a deliberate stacked or sequential composition from V01-V22, never a scaled or cropped horizontal board;
- visual review confirms scene hierarchy: conclusion first, explanation second, evidence/action third; backgrounds and SVG elements support rather than replace meaning;
- no audio file or generated MP4 was created by the workflow.

Do not claim a rendered video exists. Report the project as “工程与字幕已完成，等待人工预览或渲染指令”.
