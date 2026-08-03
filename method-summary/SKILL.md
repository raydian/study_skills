---
name: method-summary
agent_created: true
description: Summarize reusable subject-specific learning, solving, analysis, and exam-answer methods from questions, exams, wrong-answer records, solution notes, or question-bank materials. Use when the user asks for 方法总结, 解题方法归纳, 试题方法总结, 从题目总结方法, or to create subject method-summary outputs under high_school; the subject must be provided or inferred and routed to the matching reference file.
---

# Method Summary

## Core Rule

Create method summaries from question materials. Do not create knowledge-point topic notes, chapter notes, question banks, or single-question answers.

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

1. Identify the subject from the user request, source path, directory, or provided materials.
2. If the subject is ambiguous, ask for the subject before writing files.
3. Read the matching subject reference file.
4. Review the provided questions, exams, wrong-answer records, answer keys, solution notes, or question-bank materials.
5. First classify question forms in `题目形态归纳`.
6. Then classify questions by shared solving method or analysis method in `方法分类归纳`.
7. Create one method-summary file under:
   - `high_school/<学科>/方法总结/<方法名称>.md`
8. Write transferable steps, trigger cues, examples, variants, mistakes, and a quick checklist.
9. Validate that the output teaches how to solve a class of questions, not only how to answer one question.

## Output Boundary

Use `方法总结/` only for reusable methods derived from question materials.

Use other outputs when appropriate:

- `知识点专题/`: conceptual knowledge organized by knowledge point.
- `章节笔记/`: textbook chapter learning notes.
- `题库整理/`: collections of questions for practice.
- `试卷解析/`: whole-paper review and per-question analysis.
- `错题本/`: personal wrong-answer records.
