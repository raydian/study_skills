---
name: chapter-notes
description: Create subject-specific high-school chapter notes with complete learning sections, knowledge-point-centered tags, Obsidian Wikilinks, chapter MOCs, and Quartz-compatible SEO frontmatter from a specified textbook Markdown file, chapter file, or source material. Use when the user asks to 生成章节笔记, 拆解章节笔记, 按指定文件生成章节目录和子章节笔记, 建立知识图谱或双向链接, or create and improve chapter-note outputs under high_school; the subject must be provided or inferred and routed to the matching reference file.
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
16. Validate outputs before finishing:
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
   - image annotations and knowledge-map annotations are placed only where they support learning, with controlled quantity and subject-consistent style;
   - content is explanatory, not copied raw textbook text.

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
