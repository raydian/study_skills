---
name: epub-markdown
agent_created: true
description: Convert EPUB e-books/articles into Markdown, split per article/chapter, with images extracted to images/. Use when the user asks to EPUB 转 Markdown, 拆分电子书, 电子书转 md, 把 epub 拆成文章, or wants a book's chapters as separate Markdown files.
---

# EPUB Markdown

## Core Rule

Convert source EPUB files into traceable, per-article Markdown under the outer `markdown/` directory (e.g. `markdown/<学科>/<书名>/`), not under `high_school/`. One article = one Markdown file; extracted images go in a sibling `images/` subdir with relative references.

Read `references/epub-markdown-workflow.md` before converting.

## Workflow (summary)

1. Inspect the EPUB: unzip to a temp dir, read `toc.ncx` (or `nav.xhtml`) to get the article order and titles, and `content.opf` for the image folder (usually `OEBPS/Images`).
2. Convert the WHOLE EPUB with pandoc (this is the reliable path — pandoc resolves the EPUB container internally):
   - Run with `cwd` = the output dir, and use a **relative** `--extract-media` so image refs stay relative.
   - `cd <out_dir> && pandoc "<book>.epub" --extract-media=images -t markdown -o _combined.md`
3. Clean pandoc artifacts in `_combined.md` (see reference for the exact list and pitfalls).
3b. **Strip non-article promotional/boilerplate blocks** that often appear at the end of a chapter (or the whole book): public-account promos ("欢迎关注公众号", "后台留言/推送", book lists like "现已整理的作家与系列作品", "回复名称获取图书", "AZW3+EPUB+MOBI"), QR/网盘/提取码 ads, "版权所有·侵权必究" only if it is a standalone trailer line rather than the book's real copyright page. Match by distinctive phrase, not by generic words like "资源/获取" which also occur in real text.
4. Split `_combined.md` by top-level `# ` headings into `NN-标题.md` files in reading order.
5. Flatten any nested image subdir (pandoc often writes `images/Images/...`) and rewrite refs to `images/...`.
6. Optional: write `README.md` index linking all articles.
7. Validate: every `images/...` reference resolves; no `:::`, `[]{#`, or `(#chapter` leftovers.

## Boundary

This skill creates conversion/cleanup output only. Use `$chapter-notes` later when the user asks to generate learning-oriented notes from the converted Markdown.

## Pitfalls (details in reference)

- **Relative images depend on cwd.** Run pandoc from the output dir with `--extract-media=images`; an absolute extract-media path yields unusable absolute image links.
- **Do NOT convert individual XHTML files** one-by-one — pandoc then resolves `../Images/...` against the wrong directory and drops images.
- **Nested image dir:** after `--extract-media`, images may land in `images/Images/`; flatten them.
- **Footnote markers** (`[^\[1\]^](#...)`, `[\[1\]](#...)`) appear in appendix-style chapters; remove them with an exact single-backslash string replace, not a raw-string regex.
- **Promotional blocks** from ebook sources (公众号推广、图书清单、获取方式、二维码/网盘广告) are NOT article content and must be removed. They usually sit at the very end of a chapter file. Detect via distinctive phrases; never delete lines just because they contain common words like "资源" or "获取".
