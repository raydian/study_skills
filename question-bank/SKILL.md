---
name: question-bank
agent_created: true
description: Organize subject-specific high-school question banks from exercises, exams, homework, converted papers, practice sets, or selected typical questions. Use when the user asks for 题库整理, 题目整理, 专项训练题, 按知识点整理题目, 按题型整理题目, or to create subject question-bank outputs under high_school; the subject must be provided or inferred and routed to the matching reference file.
---

# Question Bank

## Core Rule

Create reusable practice question banks. Do not create wrong-answer notebooks, whole-paper analyses, method summaries, chapter notes, or topic notes.

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

1. Identify the subject, source materials, question-bank theme, and target scope.
2. If the subject is ambiguous, ask for the subject before writing files.
3. Read the matching subject reference file.
4. Extract complete questions from the input, preserving stems, options, figures, tables, answers, and necessary context.
5. Classify questions by knowledge point, question type, difficulty, source, and training purpose.
6. Deduplicate repeated or near-repeated questions unless they are useful variants.
7. Arrange questions from basic to consolidation to extension to comprehensive.
8. Create one file under:
   - `high_school/<学科>/题库整理/<题库名称>.md`
9. Keep answers and explanations separated from question bodies.
10. Validate that the output is suitable for repeated practice and later mistake recycling.

## Output Boundary

Use `题库整理/` only for practice collections.

Use other outputs when appropriate:

- `错题本/`: personal wrong-answer retention.
- `试卷解析/`: whole-paper review and scoring analysis.
- `方法总结/`: reusable solving or answer methods.
- `知识点专题/`: conceptual topic knowledge.
