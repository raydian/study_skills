---
name: topic-summary
agent_created: true
description: Create subject-specific high-school knowledge-point topic notes from textbooks, converted Markdown, course standards, notes, exercises, or source materials. Use when the user asks for 知识点专题, 专题整理, 专题总结, 知识网络, or to create subject topic outputs under high_school; the subject must be provided or inferred and routed to the matching reference file.
---

# Topic Summary

## Core Rule

Create knowledge-point topic notes. Do not create chapter notes, unit notes, method summaries, question banks, or single-question answers.

The user request must include or imply a subject. Treat `学科` as the routing parameter.

Read exactly one subject reference before writing files:

- `学科=语文`: `references/chinese.md`
- `学科=数学`: `references/math.md`
- `学科=英语`: `references/english.md`
- `学科=物理`: `references/physics.md`
- `学科=化学`: `references/chemistry.md`
- `学科=生物`: `references/biology.md`
- `学科=历史`: `references/history.md`
- `学科=地理`: `references/geography.md`

## Workflow

1. Identify the subject and target knowledge point from the user request, source path, or materials.
2. If the subject is ambiguous, ask for the subject before writing files.
3. Read the matching subject reference file.
4. Use source materials to gather concepts, related knowledge, examples, common traps, and exam angles.
5. Organize by knowledge point, ability point, model, rule, theme, or topic, not by chapter, lesson, or unit.
6. Create one topic file under:
   - `high_school/<学科>/知识点专题/<专题名称>.md`
7. Include topic positioning, knowledge network, examples, errors, exam summary, practice, and answers according to the subject reference.
8. Validate that the output is reusable across multiple chapters, materials, or question contexts.

## Output Boundary

Use `知识点专题/` only for reusable topic knowledge.

Use other outputs when appropriate:

- `章节笔记/`: textbook chapter learning notes.
- `方法总结/`: methods derived from question materials.
- `题库整理/`: collections of questions for practice.
- `试卷解析/`: whole-paper review and per-question analysis.
- `错题本/`: personal wrong-answer records.
