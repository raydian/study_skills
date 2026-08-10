---
name: chapter-notes
description: Create subject-specific high-school chapter notes with complete learning sections, real-subchapter splitting, source-figure image annotations, knowledge-point-centered tags, Obsidian Wikilinks, chapter MOCs, and Quartz-compatible SEO frontmatter from a specified textbook Markdown file, chapter file, or source material. Use when the user asks to 生成章节笔记, 拆解章节笔记, 按真实子章节生成独立笔记, 为教材插图补充图片注释, 建立知识图谱或双向链接, or create and improve chapter-note outputs under high_school; the subject must be provided or inferred and routed to the matching reference file.
---

# Chapter Notes

## Core Rule

Do not place raw textbook splits directly into `high_school/<学科>/章节笔记/`.

`章节笔记/` must contain learning-note outputs: one folder per real textbook chapter, and one Markdown file per subchapter knowledge explanation.

The user request must include or imply a subject. Treat `学科` as the routing parameter.

Always read `references/common.md`, then read exactly one subject reference before writing files:

- `学科=语文`: `references/chinese.md`
- `学科=数学`: `references/math.md`
- `学科=英语`: `references/english.md`
- `学科=物理`: `references/physics.md`
- `学科=化学`: `references/chemistry.md`
- `学科=生物`: `references/biology.md`
- `学科=历史`: `references/history.md`
- `学科=地理`: `references/geography.md`

## Workflow

1. Identify the subject, input file, target chapter range, and output target from the user request.
2. If the subject is ambiguous, ask for the subject before writing files.
3. Read `references/common.md` and the matching subject reference file.
4. If the user gives a specific Markdown file, use that file as the source of truth. Do not silently switch to another source file.
5. If the user gives a PDF, first convert it to `markdown/<学科>/` according to the project rules, then generate notes from the Markdown.
6. Determine whether the input file is a full textbook, a single chapter, or a pre-split chapter file.
7. Locate real chapter headings and subchapter headings from the source. Do not split by page number, exercise block, or decorative heading.
8. Inspect existing notes under `high_school/` before assigning tags or links. Reuse established knowledge-point tag names, aliases, and real note targets; do not create synonym tags or dangling Wikilinks.
9. Create or update:
   - `high_school/<学科>/章节笔记/<章节名>/`
   - one file per subchapter, named `<小节序号> <小节名称>.md`.
10. For every created or updated chapter, create or maintain `章首 学习导图.md` as the chapter MOC. Link every real subchapter and explain the prerequisite, progression, comparison, derivation, or application relationships among its core knowledge points. A `章末 整理与提升.md` may supplement the MOC but cannot replace it.
11. For every subchapter file, first extract a source knowledge checklist and a normalized knowledge-point list. The final note must cover every core source point and must use those actual points to build its frontmatter tags and knowledge links.
12. Start every subchapter note with Quartz-compatible YAML frontmatter containing non-empty `title`, `description`, `aliases`, `tags`, and boolean `draft`. Add at least 2 real `知识点/` tags and normally 3–8; every knowledge-point tag must map to a substantive explanation in the note.
13. Add `## 知识关系导航` between the H1 title and the nine required learning sections. Every note must contain at least one verified Wikilink, normally to the chapter MOC plus relevant knowledge-point headings in existing or concurrently created notes. Add contextual body Wikilinks when they clarify a genuine knowledge relationship.
14. When one input file contains multiple chapters, create one chapter folder and one chapter MOC per real chapter, then generate the subchapter files inside each folder.
15. Do not create `原始课本素材.md` inside `章节笔记/` unless the user explicitly asks for source-material archiving there. Prefer keeping raw material in `markdown/`.
16. Treat illustrations as a two-pass deliverable: first write complete notes with source-figure-aware `图片描述` comments; only then hand the notes to `subject-illustrations` or another image workflow to generate and insert image files. Never remove a comment because an image has not yet been generated.
17. Validate outputs before finishing:
   - correct subject directory;
   - one folder per real chapter;
   - one file per real subchapter;
   - one maintained `章首 学习导图.md` per created or updated chapter, used only for chapter-level organization and not as a substitute for subchapter notes;
   - chapter folders are not whole-book dumps;
   - every created or updated note has valid YAML frontmatter with non-empty `title`, `description`, `tags`, `aliases`, and boolean `draft`;
   - every subchapter note has at least 2 stable `知识点/` tags, normally 3–8, and each tagged point is explained in the body;
   - every subchapter note has `知识关系导航` and at least one Wikilink whose target exists or is created in the same task;
   - knowledge links express a real prerequisite, progression, comparison, causation, derivation, method-transfer, or application relationship instead of forming a link dump;
   - every subchapter file has the required nine sections;
   - every core knowledge point, key definition, important conclusion, required method, and source example/experiment/material point from the textbook subchapter is covered;
   - every source figure, chart, map, experiment image, or other meaningful visual unit has a nearby, specific image annotation; the generic local-image count is only a default when the source has no figure inventory;
   - image annotations and knowledge-map annotations are placed only where they support learning, with controlled quantity and subject-consistent style;
   - content is explanatory, not copied raw textbook text.

## Subchapter Splitting Contract

Split by the textbook's real teaching structure, not by page boundaries or whatever heading happens to be easiest to match:

- A numbered teaching section such as `第一节`, `第二节`, `1.1`, or `1.2` becomes its own Markdown note and keeps the source section title in the filename.
- A chapter folder must contain every real teaching section plus any substantial chapter-end learning unit. A `问题研究`/专题探究 with its own materials, questions, or conclusions may be a separate note; a short `活动`/`思考`/`案例` remains in the parent section while its learning value is preserved.
- Do not merge two real sections into one file, flatten all sections into `原始课本素材.md`, or create files only for page ranges, image blocks, exercises, or decorative headings.
- After splitting, update `章首 学习导图.md` so it links every generated note and explains the sequence and cross-section relationships. Each split note still receives the complete learning-note structure; splitting must not reduce content to a summary.
- When updating an existing chapter, preserve established filenames and links where possible. If a split is corrected, update the MOC and all affected Wikilinks in the same task.

## Illustration Contract

Image annotations are part of the note content and form the handoff contract to image generation:

- Before writing, inventory source visual units by figure number/caption or source image reference. Map each meaningful source visual unit to one nearby `<!-- 图片描述：... -->` comment. Preserve the source figure identity in the visible explanation or in the comment so the mapping is auditable.
- Every subchapter starts with one “本节整体知识信息结构图” comment. Add source-driven comments and learning-value-driven local diagrams near the relevant paragraph; the source inventory overrides any generic 2–5-image guideline.
- A comment must describe the subject, structure, labels, arrows, variables, legend, comparison or process, key conclusion, and why the image helps at that exact location. `<!-- 配图 -->` and other empty placeholders are invalid.
- In the image-generation pass, insert the generated image immediately above its comment using a relative path such as `![图1.1：太阳辐射示意图](images/第一节-太阳辐射-图1-1.webp)`. Keep the comment after insertion.
- Image filenames and relative paths must contain no spaces. Use hyphens or underscores as separators; keep names stable, readable, and tied to the note/figure identity. Do not use a filename that changes between generation and insertion.
- Generated images belong beside the note in its `images/` directory and may be shared by related notes through relative paths when that is clearer; do not duplicate identical assets unnecessarily. Validate that every referenced file exists and that no source-image mapping was silently dropped.

## Output Boundary

Use `high_school/<学科>/章节笔记/` only for final learning notes.

Keep these outside `high_school/`:

- PDF textbooks;
- raw converted Markdown;
- formatted full-book Markdown;
- chapter source splits that are not learning notes;
- conversion scripts.

## Naming

Use the project’s Chinese naming style:

```text
high_school/<学科>/章节笔记/
  第一章 章名/
    1.1 小节名.md
    1.2 小节名.md
```

If the textbook uses sections without numeric labels, use:

```text
第一节 小节名.md
第二节 小节名.md
```

Keep filenames readable and close to the textbook’s real section titles.

## Validation Checklist

Before final response, run a quick check such as:

```bash
find "high_school/<学科>/章节笔记/<章节名>" -maxdepth 1 -type f -name "*.md" -print
rg -n "^title:|^description:|^aliases:|^tags:|^draft:|知识点/|^## 知识关系导航|\[\[[^]]+\]\]|^## 本节学习目标|^## 核心知识点讲解|^## 练习题答案" "high_school/<学科>/章节笔记/<章节名>"
```

If the files are only source extracts, delete or move them out of `章节笔记/` and regenerate as learning notes.

If a generated note is only a summary and omits textbook core content, regenerate it from the source instead of accepting the shortened version.
