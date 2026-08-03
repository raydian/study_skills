# PDF to Markdown Conversion Contract

## Purpose

Create complete, traceable Markdown conversions from source PDFs while preserving text content and meaningful images. The conversion output is an intermediate source artifact, not a final learning note.

## Output Location

Use the outer `markdown/` directory.

For textbooks:

```text
markdown/<学科>/<文件名>/
  <文件名>.md
  <文件名>-格式化.md
  images/
```

For original materials such as handouts, exams, diagrams, or reference PDFs:

```text
markdown/<学科>/原始资料/<文件名>/
  <文件名>.md
  <文件名>-格式化.md
  images/
```

Rules:

- Name `<文件名>` from the PDF stem without `.pdf`.
- Do not put converted Markdown or extracted images into `high_school/`.
- Do not flatten unrelated PDFs into the same output folder.
- Keep image links relative, such as `![图 1](images/page-012-figure-01.png)`.

## Extraction Priority

Use this order:

1. Embedded text extraction.
2. Layout-aware embedded text extraction.
3. OCR for only pages or regions where embedded extraction fails.

Use OCR when:

- a page has no embedded text;
- extracted text is mostly garbled characters;
- columns are mixed and cannot be repaired by cropping;
- formulas, captions, or question stems are visibly missing;
- scanned pages contain only images.

When OCR is used, add a short note near the page or in a conversion note section:

```markdown
> 转换说明：本页使用 OCR 识别，已人工整理明显断行和乱码。
```

## Layout Rules

Before extracting text, inspect page layout.

- Single-column pages: extract normally.
- Double-column pages: split by the page middle or detected column gutters; read left column first, then right column.
- Multi-column tables or vocabulary lists: preserve row order when possible; otherwise use Markdown tables or aligned lists.
- Exercises and exams: keep each question, options, diagrams, and answers together.

Do not split by page headers alone. Page boundaries are useful for traceability but should not break sentences, formulas, question stems, or table rows.

## Image Rules

Extract meaningful content images into `images/`.

Extract:

- textbook figures and diagrams;
- experiment apparatus diagrams;
- maps, charts, and graphs;
- question images;
- tables that cannot be reliably reconstructed as Markdown;
- handwritten or scanned content that is part of the source.

Do not extract:

- background textures;
- decorative borders;
- publisher watermarks;
- page-number ornaments;
- full-page screenshots when text and figures can be extracted separately.

Image naming:

```text
images/page-001-figure-01.png
images/page-013-table-02.png
images/page-026-question-05.png
```

Markdown reference format:

```markdown
![图片：图注或内容说明](images/page-013-figure-01.png)
```

If an image cannot be extracted but is required for understanding, preserve a placeholder:

```markdown
[图片：第 3 题右侧的受力示意图，需回看原 PDF]
```

## Raw Markdown Requirements

`<文件名>.md` should be traceable and conservative.

It may include:

- page markers;
- conversion notes;
- image links or placeholders;
- original order preserved as much as possible.

It must preserve:

- body text;
- headings and subheadings;
- formulas and equations;
- figure captions;
- exercises and answers;
- annotations, footnotes, indexes, appendices;
- tables or table placeholders.

## Formatted Markdown Requirements

`<文件名>-格式化.md` should be readable and structurally clean.

Clean:

- generated page headings such as `## 第 X 页`;
- meaningless footer page numbers;
- repeated decorative number rows;
- publisher layout noise;
- broken hyphenation or unnecessary hard line breaks;
- duplicated outline-font text, such as `LLiisstteenniinngg` -> `Listening`.

Preserve:

- all meaningful text from the raw conversion;
- formulas in Markdown/LaTeX where practical;
- content images and placeholders;
- exercises, answers, indexes, appendices, notes, and captions.

Recommended heading levels:

```markdown
# 教材名或资料名

## 第一章 章名

### 1.1 小节名

#### 栏目名
```

For unit-based textbooks:

```markdown
# 教材名

## Unit 1 Unit Name

### Reading and Thinking
```

## Formula Rules

Use Markdown/LaTeX where practical.

Examples:

```markdown
$v = \frac{\Delta x}{\Delta t}$

$$
Na_{2}SO_{4} + BaCl_{2} = 2NaCl + BaSO_{4}\downarrow
$$
```

Do not discard formulas because extraction is imperfect. If a formula cannot be recovered confidently, keep a placeholder:

```markdown
[公式：此处为第 18 页例题中的速度计算公式，需回看原 PDF 校对]
```

## Quality Checks

Before finishing, check:

- Raw and formatted Markdown both exist.
- The formatted file is not shorter because content was accidentally dropped.
- Each extracted image is referenced or intentionally unused with a reason.
- There are no obvious `cid:` fragments, repeated-art-font words, broken columns, or orphaned page footers.
- OCR pages are noted.
- For exams and exercises, each question keeps its options, diagrams, and answer relationship intact.

If content completeness is uncertain, say so and list the pages or sections that need manual review.
