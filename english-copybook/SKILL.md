---
name: english-copybook
agent_created: true
description: Generate printable A4 English handwriting copybooks (字帖) from high-school English unit notes. Use when the user asks to 生成英语字帖, 做练字纸, 背单词字帖, 描红练习, 单元默写纸, or wants a print-ready practice sheet covering vocabulary / phrases / example sentences / passage tracing / dictation for a 人教版高中英语 unit. Produces a self-contained HTML plus an A4 PDF.
---

# English Copybook（英语单元字帖）

## Core Rule

Turn an **input-oriented** unit note (`章节笔记/<Unit>/<Unit>-单元知识专题.md`) into an **output-oriented** handwriting practice sheet. Do not simply re-typeset the Markdown — a copybook that only makes the student copy text trains the hand, not the memory.

Every vocabulary entry must follow the **three-stage gradient**:

| 阶段 | 形式 | 认知负荷 |
| --- | --- | --- |
| ① 描红 | 灰色范字，直接覆盖书写 | 低（字形、肌肉记忆） |
| ② 临写 | 空格，看词性/中文抄写 | 中（拼写编码） |
| ③ 默写 | 册末集中，只给中文 + 首字母提示 | 高（主动提取） |

## Quick Start

```bash
cd /Users/yxy/document/jay/hs_knowledge/high_school/英语/字帖
/Users/yxy/.workbuddy/binaries/python/versions/3.13.12/bin/python3 \
  generate_copybook.py --data data/<unit>.json
```

Outputs `<单元名>/<单元名>-字帖.html` and `...-字帖.pdf` side by side.
Use `--out-dir` to redirect, `--no-pdf` to skip PDF export.

To build a new unit: copy `data/unit-1-teenage-life.sample.json`, rewrite `items`, rerun.

## Data Schema

Top level: `unit`, `book`, `scope`, `footer`, `hand_font`, `sections[]`.

Section keys: `key`, `title`, `desc`, `minutes`, `mode`, `cols?`, `row_h`,
`font`, `repeat_cap`, `blanks`, `items[]`.

Four `mode` values:

| mode | 渲染形态 | 关键字段 |
| --- | --- | --- |
| `word` | 第一行 编号+单词+词性+复选框；第二行 中文+说明；下方 描红行 + N 行临写 | `head`, `pos`, `cn`, `note`, `trace` |
| `sentence` | 第一行 编号+中文+复选框；第二行 短语本体+搭配；下方 整句描红 + 整句临写 | `head`(短语), `cn`, `note`, `trace`(完整例句) |
| `passage` | 标题行 + ①描红整段 + ②临写整段 | `head`(篇名), `text` |
| `recall` | 中文提示 + 挖空提示 + 单行书写格 | `prompt`, `hint` |

Set `cols: 2` on a `word` section for a two-column layout.

## Layout Constants (mm)

A4 210×297; padding `16 / 15 / 14 / 20` (left 20 for binding).
Content box 175×267, `CONTENT_SAFE` = 267 − 8 for pagination.
四线三格 row height: 词汇 8, 句子 9, 作文 7.

Color: 描红 `#C9CFD6`, 格线 `#CBD3DA`, 基线 `#93A0AD`, 强调 `#1F4E6B`, 正文 `#1A1A1A`.

## Hard-Won Constraints — Do Not Revert

1. **四线三格 must use real DOM borders + pseudo-elements, never `background-image`.**
   Browsers drop background images when printing; gradient grids produce blank paper.

2. **Baseline alignment uses `flex` + `align-items: baseline` + a zero-width spacer
   `.sp { width: 0; height: row_h × 2/3 }`.** The spacer's baseline is its bottom
   edge, so the position is font-independent. Do not switch to `line-height` tuning.

3. **Pagination is computed in Python by mm budget**, with a fixed 297mm `.page`
   carrying `break-after: page`. Do not rely on the browser's pagination — it splits
   entries mid-block.

4. **Keep the 8mm `CONTENT_SAFE` margin.** A page estimated at 266.5/267mm is one
   rounding error away from being clipped by `overflow: hidden`.

5. **`.l1` uses `nowrap + overflow: hidden`** (fixed height); **`.l2` uses
   `flex-wrap: wrap` with `line-height: 4.0mm`** so long notes wrap instead of truncating.

## Text Width Estimation

```python
CJK / 全角标点  → 1.00 em
ASCII           → 0.52 em   (Comic Sans)
space           → 0.28 em
```

Predict wrapping with an 8% safety factor: `lines = ceil(width / (avail * 0.92))`.
For `cols: 2`, per-column usable width is `(175 - 6) / 2 - 5 ≈ 79.5mm` — all font
sizing, trace repetition counts, and wrapping must be recomputed against that, not
against the full 170mm.

## Time Budget — Calibrate Against Reality, Not Theory

The first version estimated 30s per trace row and 25s per copy row and claimed 19
minutes; the user measured **under 15**. The estimates were ~35% too high.

Use measured coefficient **0.654** against the raw estimate:

| 行类型 | 原始估算 |
| --- | --- |
| 词汇描红行（2 遍） | 20s |
| 词汇临写行 | 12s |
| 例句描红行 | 40s |
| 例句临写行 | 35s |
| 短文描红行 | 50s |
| 短文临写行 | 45s |
| 默写行 | 15s |

`预计用时 = 原始估算总和 × 0.654`. If the user says it ran short, scale content
volume by the ratio rather than nudging a single number.

## Verification Workflow

Visual check when images are available:

```bash
/Users/yxy/.workbuddy/binaries/python/envs/default/bin/python -c "
import pypdfium2 as pdfium
pdf = pdfium.PdfDocument('<path>.pdf')
for i in range(len(pdf)):
    pdf[i].render(scale=150/72).to_pil().save(f'/tmp/p{i+1}.png')
"
```

Programmatic check when they are not — extract text per page and diff against the
source JSON so nothing is silently clipped:

```python
pages = [pdf[i].get_textpage().get_text_range() for i in range(len(pdf))]
```

Verify: every `head` / `trace` / `prompt` appears, every passage token appears, and
each page footer renders.

## Content Sizing Reference (Unit 1 sample, ~22 min, 5 pages)

- A 核心词汇 10 词，双栏 5 行，描红 2 遍 + 临写 2 遍
- B 短语与例句 7 条（描红整句 + 临写整句）
- C 描红短文 2 篇：课文节选（6 行）+ 建议信节选（3 行）
- D 默写自检 8 题
- 外加 1 页使用说明（三段式说明 + 练习记录表 + 范字示意）

## Extraction Source

Pull vocabulary, phrases, example sentences, and the reading passage from
`high_school/英语/章节笔记/<Unit>/<Unit>-单元知识专题.md`. Prefer items marked ★
in the source, and prefer example sentences taken verbatim from the textbook text.
