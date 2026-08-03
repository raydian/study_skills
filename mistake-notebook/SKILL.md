---
name: mistake-notebook
agent_created: true
description: Create subject-specific high-school wrong-answer notebooks from exams, homework, practice questions, question banks, test analyses, answer records, or correction notes. Use when the user asks for 错题本, 错题整理, 错题复盘, 二次订正, 从试卷提取错题, or to create subject mistake-notebook outputs under high_school; the subject must be provided or inferred and routed to the matching reference file.
---

# Mistake Notebook

## Core Rule

Create wrong-answer notebooks for real mistakes, unstable solved questions, repeated traps, or high-value correction records. Do not create question banks, whole-paper analyses, method summaries, or chapter notes.

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

1. Identify the subject, source material, mistake source, and target notebook theme.
2. If the subject is ambiguous, ask for the subject before writing files.
3. Read the matching subject reference file.
4. Extract only wrong, unstable, repeated, or high-value questions from the input.
5. For each mistake, preserve the original question, the wrong answer or wrong thinking, the correct solution, the cause, and a prevention rule.
6. Classify mistakes by question form, knowledge point, mistake cause, and mastery status.
7. Create or update:
   - `high_school/<学科>/错题本/<错题主题>.md`
8. Add second-correction records and same-type variants when useful.
9. Validate that every mistake explains why it was wrong and how to avoid repeating it.

## Output Boundary

Use `错题本/` only for correction and retention.

Use other outputs when appropriate:

- `试卷解析/`: whole-paper review and per-question scoring analysis.
- `题库整理/`: collections of questions for practice.
- `方法总结/`: reusable solving or answer methods across question groups.
- `知识点专题/`: conceptual knowledge organized by topic.
