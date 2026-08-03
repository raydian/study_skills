---
name: pdf-markdown
agent_created: true
description: Convert PDF textbooks, curriculum standards, handouts, exams, and other source PDFs into complete Markdown outputs with extracted content images. Use when the user asks to PDF 转 Markdown, 转换教材 PDF, 格式化 Markdown, 提取 PDF 图片, preserve all text content, or use OCR fallback when embedded text extraction is incomplete.
---

# PDF Markdown

## Core Rule

Convert source PDFs into traceable Markdown under the outer `markdown/` directory, not under `high_school/`.

Read `references/pdf-markdown-contract.md` before converting or formatting files.

## Workflow

1. Identify the subject, PDF type, source path, and expected output scope from the user request.
2. Create an output folder named after the PDF file stem:
   - textbook: `markdown/<学科>/<文件名>/`
   - original material: `markdown/<学科>/原始资料/<文件名>/`
3. Generate at least:
   - `<文件名>.md` for the raw traceable conversion;
   - `<文件名>-格式化.md` for the cleaned and structured Markdown;
   - `images/` for extracted non-background content images when present.
4. Extract text first using PDF embedded text. Detect layout before extraction:
   - single-column pages: normal text extraction;
   - multi-column pages: crop by columns and read left-to-right, top-to-bottom.
5. Extract meaningful content images, diagrams, figures, tables, and question images into `images/`. Do not save background textures, page decorations, or full-page decorative scans unless they are the only readable source.
6. If embedded text is missing, garbled, incomplete, or clearly out of order, use OCR fallback for the affected pages.
7. Format Markdown without dropping content: preserve body text, headings, formulas, figure captions, tables, exercises, answers, notes, indexes, and annotations.
8. Validate before finishing:
   - output folder exists and is named after the PDF;
   - raw and formatted Markdown both exist;
   - extracted images are referenced from Markdown with relative paths;
   - OCR fallback is noted when used;
   - no obvious PDF noise, page footers, duplicated outline-font text, or column-order corruption remains in the formatted file.

## Boundary

This skill creates conversion and formatting outputs only. Use `$chapter-notes` later when the user asks to generate learning-oriented chapter notes from the converted Markdown.
