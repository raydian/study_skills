---
name: xiangtu-chapter-video-clone
description: This skill should be used when the user wants to create a silent Remotion video project for a new chapter of 费孝通《乡土中国》under video/语文/乡土中国/, following the established data-driven close-reading architecture (cover + 逐段细读 reading scenes + 结构统整/方法迁移 analysis scenes + closing).
agent_created: true
---

# 乡土中国章节视频克隆

## Overview

Clone the latest validated silent Remotion baseline in `video/语文/乡土中国/` and repurpose it for the next《乡土中国》chapter. The workflow preserves all bugfixes (subtitle splitter, Stack overlap fix, nowrap subtitles) and keeps the single-source data architecture: `reading.ts` + `analysis.ts` drive `subtitles.ts`, which drives `timeline.ts`, which drives the Remotion composition.

## When to Use

Use this skill when the user requests a new《乡土中国》chapter video with a reference like:

- "参考已完成的视频工程：.../文字下乡" or any existing chapter project under `video/语文/乡土中国/`
- The source is a chapter Markdown file such as `high_school/语文/章节笔记/乡土中国/NN-章节名.md`
- The output should be a silent Remotion project under `video/语文/乡土中国/NN-章节名/`

Do NOT use this skill for mathematics, physics, English, or generic Chinese poetry lessons — those use the subject-specific templates.

## Prerequisites

1. Identify the latest validated silent baseline project (e.g., the highest-numbered existing chapter like `10-家族/` or `11-男女有别/`).
2. Confirm the shared dependency symlink target exists: `video/语文/node_modules/`.
3. Read the source chapter Markdown to extract 逐段解读 units and overall structure.

## Workflow

### 1. Scaffold from the Latest Silent Baseline

```bash
cd video/语文/乡土中国/
BASELINE="<latest-silent-project>/"
TARGET="NN-章节名/"
rsync -a --exclude 'output' --exclude 'voiceover' --exclude '.git' --exclude '.DS_Store' --exclude 'node_modules' "$BASELINE" "$TARGET"
cd "$TARGET"
ln -s ../../../node_modules
rm -f src/timeline.json
rm -rf public/audio
```

### 2. Build `src/data/reading.ts`

- Create ~14 `ReadingUnit` objects with ids `"01"`–`"14"`.
- Each unit: `id`, `tag`（对应原文）, `title`, `quote`（原文摘录）, `layers: [{kind, text}]`（概念/推理/方法）, `summary`.
- Map each unit to one 逐段解读 paragraph or a closely related group of paragraphs from the source.
- Keep quotes excerpted but semantically complete; long quotes are auto-split by the subtitle splitter.

### 3. Build `src/data/analysis.ts`

- Create 6 `AnalysisUnit` objects with ids `"15"`–`"20"`.
- Use layouts: `map`, `bridge`, `route`, `methods`, `question`, `check`.
- Typical set:
  - 15 概念体系（map）
  - 16 文化/结构对比（bridge）
  - 17 因果链概括（route）
  - 18 论证方法（methods）
  - 19 方法迁移·概念阐释题（question）
  - 20 方法迁移·观点评价题（check）
- Keep `nodes` to at most 4 items for Stack-based layouts to avoid overlap.

### 4. Update `src/data/subtitles.ts`

- Keep `SCENE_ORDER` as `["00", "01".."14", "15".."20", "21"]`.
- Update `COVER_CUES_TEXT` and `CLOSING_CUES_TEXT` for the new chapter.
- Do not change `SUB_MAX`, `splitLong`, `pace`, or `TAIL` unless a layout issue is discovered.

### 5. Update `src/timeline.ts`

- Update `SCENE_NAMES` for all 22 scene ids to match the new chapter.

### 6. Update Visual Shell

- `src/scenes/Scene00Cover.tsx`: update `ROUTE` keywords, title, subtitle.
- `src/scenes/SceneClosing.tsx`: update `READ_WAYS`, big quote, title.
- `src/Composition.tsx`: remap scene components if the count changes (default 00 + 01–14 + 15–20 + 21).
- `src/Root.tsx`: update `id` to a PascalCase composition id.
- `package.json`: update `"name"`.

### 7. Validate

```bash
npx tsc --noEmit
```

Also run a subtitle length check:

```bash
npx tsx --no-cache -e "
import { SCENE_SUBTITLES } from './src/data/subtitles';
let max = 0;
for (const id of Object.keys(SCENE_SUBTITLES)) {
  for (const seg of SCENE_SUBTITLES[id]) {
    if (seg.text.length > max) max = seg.text.length;
  }
}
console.log('MAX_LEN=' + max);
"
```

Max must be ≤ 46.

### 8. Render Validation Stills

Render at least:

- Cover frame
- One reading scene with a long quote
- One Stack analysis scene (`map`/`bridge`/`route`/`methods`/`check`)
- Closing frame

Check that:

- Bottom subtitles stay on one line.
- No content card overlaps the bottom summary card.
- Scene titles and node labels are fully visible.

### 9. Generate Planning Docs

Regenerate from `subtitles.ts` true source:

- `口播稿.md`
- `storyboard.md`
- `content-design.md`

### 10. Clean Up

Remove stale preview stills copied from the baseline, temporary `t_*.ts` scripts, and any `.bak` files.

## Data Format Reference

Read the current baseline's source files for exact TypeScript types:

- `src/data/reading.ts` → `ReadingUnit`, `LayerKind`, `Layer`
- `src/data/analysis.ts` → `AnalysisUnit`, `AnalysisLayout`, `AnalysisNode`, `AnalysisAccent`
- `src/data/subtitles.ts` → `SubtitleSegment`, `SCENE_ORDER`, `SCENE_SUBTITLES`, `SCENE_DURATION`, `NARRATION`
- `src/timeline.ts` → `SceneDef`, `SCENE_NAMES`, `FPS`, `TOTAL_FRAMES`

## Constraints

- Keep the project silent; do not add `voiceover.mp3` or `timeline.json` in this workflow.
- Use the existing shared `node_modules` symlink; never run a local `npm install` inside the project.
- Maintain the 22-scene structure unless the chapter content genuinely requires a different split.
- Subtitle text must not exceed 46 characters per cue.
