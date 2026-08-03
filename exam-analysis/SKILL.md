---
name: exam-analysis
agent_created: true
description: Analyze subject-specific high-school exam papers, tests, quizzes, mock exams, answer sheets, score records, and paper review materials by question type, knowledge distribution, mistakes, scoring, and follow-up actions. Use when the user asks for 试卷分析, 试卷解析, 试题分析, 月考分析, 期中分析, 模拟卷解析, or to create subject exam-analysis outputs under high_school; the subject must be provided or inferred and routed to the matching reference file.
---

# Exam Analysis

## Core Rule

Create whole-paper analysis and review outputs. Do not create only a wrong-answer notebook, question bank, method summary, topic note, or chapter note.

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

1. Identify the subject, paper name, exam type, source paper, answer key, score record, and student answers if provided.
2. If the subject is ambiguous, ask for the subject before writing files.
3. Read the matching subject reference file.
4. Classify the paper by question type and problem type according to the subject reference.
5. Analyze knowledge distribution, difficulty distribution, score distribution, and high-value questions.
6. For each question or question group, summarize tested knowledge, solution idea, answer basis, common traps, and likely loss reasons.
7. Distinguish `不会`, `会但做错`, `审题失误`, `计算/表达失误`, `时间分配问题`, and `方法不熟`.
8. Create one file under:
   - `high_school/<学科>/试卷解析/<试卷名称>解析.md`
9. Mark questions that should later enter `错题本/`, `题库整理/`, `方法总结/`, or `知识点专题/`.
10. Validate that the output supports exam review and follow-up study planning, not just answer recording.

## Output Boundary

Use `试卷解析/` only for whole-paper or whole-test review.

Use other outputs when appropriate:

- `错题本/`: personal wrong-answer retention.
- `题库整理/`: reusable question collections.
- `方法总结/`: reusable solving or answer methods.
- `知识点专题/`: conceptual topic knowledge.
