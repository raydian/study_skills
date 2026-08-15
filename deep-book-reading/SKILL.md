---
name: deep-book-reading
description: Use when a user wants to read, decompose, annotate, teach, synthesize, or mine reusable Agent Skills from a complete book, textbook, PDF, EPUB, scan, or chapter collection—especially when coverage, multimodal content, attribution, source fidelity, stable citations, chapter articles, or cross-chapter reasoning matter.
---

# Deep Book Reading

## Overview

Turn an authorized book source into three synchronized assets: publishable human deep-reading articles, an AI-readable semantic corpus, and source-backed reusable knowledge/Agent Skills. Treat the canonical Source layer as immutable evidence; every interpretation must point back to it.

## Non-negotiable contract

1. Preserve source wording. Formatting repairs may restore structure, whitespace, hyphenation, or OCR only when verified; never paraphrase `source.md`.
2. Seal the normalized Source layer with a hash before annotation. Revise Annotation records by version; never silently mutate Source after sealing.
3. Give every chapter, section, paragraph, page, figure, table, equation, code block, sidebar, caption, and footnote a stable locator.
4. Attach `source_refs` to every material reading claim, annotation, knowledge unit, synthesis claim, and generated Skill rule.
5. Keep attribution explicit: `author_claim`, `source_evidence`, `quoted_view`, `case`, `ai_explanation`, `ai_inference`, `ai_synthesis`, `critical_analysis`, or `editorial_note`.
6. Never claim complete reading while a mandatory Reading Ledger unit is incomplete or unresolved.
7. Never convert merely factual, literary, weakly evidenced, or non-repeatable content into a procedural Skill.
8. Respect copyright and authorization. A full Source layer is for user-provided, public-domain, licensed, or otherwise authorized material; otherwise produce only permitted transformations and short evidence excerpts.

Read [artifact-contract.md](references/artifact-contract.md), [locator-and-provenance.md](references/locator-and-provenance.md), and [quality-gates.md](references/quality-gates.md) before producing artifacts. For scans or books with any non-body content, also read [multimodal-reading.md](references/multimodal-reading.md). For a generated Skill, read [skill-candidate-and-generation.md](references/skill-candidate-and-generation.md).

## Output package

```text
book-slug/
├── BOOK.md
├── manifest.yaml
├── reading-ledger.yaml
├── evidence-ledger.yaml
├── chapters/chNN/
│   ├── source.md
│   ├── reading.md
│   ├── annotated.md
│   ├── annotations.yaml
│   ├── knowledge.yaml
│   └── assets/
├── knowledge/
│   ├── concepts.yaml
│   ├── claims.yaml
│   ├── frameworks.yaml
│   ├── methods.yaml
│   ├── cases.yaml
│   └── glossary.md
├── synthesis/
│   ├── book-map.md
│   ├── core-thesis.md
│   ├── concept-evolution.md
│   ├── argument-map.md
│   ├── critical-reading.md
│   └── full-book-reading.md
└── skills/<candidate-slug>/
    ├── SKILL.md
    ├── provenance.yaml
    └── tests/
```

Use the corresponding files under `templates/`; do not improvise incompatible schemas.

## Select the reading profile

Read [classifier.md](profiles/classifier.md), choose one primary profile, and optionally add one secondary profile:

| Profile | Load when |
|---|---|
| [technical.md](profiles/technical.md) | architecture, algorithms, API, code, implementation |
| [textbook.md](profiles/textbook.md) | definitions, dependency order, theorems, worked examples |
| [business-management.md](profiles/business-management.md) | frameworks, decisions, organizations, cases |
| [academic.md](profiles/academic.md) | studies, methods, evidence quality, rival explanations |
| [history-biography.md](profiles/history-biography.md) | chronology, agency, causation, turning points |
| [literature.md](profiles/literature.md) | character, narrative, imagery, theme, form |

Record the choice and rationale in `manifest.yaml`.

## Execute PASS 0–5

### PASS 0 — Survey and intake

Read [pass-0-intake.md](workflows/pass-0-intake.md). Verify source authorization, edition, completeness, OCR/searchability, page mapping, structure, and all resource kinds. Create the Book Manifest and initial Reading Ledger. Stop finalization if the source is incomplete.

### PASS 1 — Structural reading

Read [pass-1-structural.md](workflows/pass-1-structural.md). Recover the book map, chapter roles, questions, preliminary concepts, and argument topology. Establish stable IDs. Do not write final interpretations yet.

### PASS 2 — Analytical chapter reading

Read [pass-2-analytical.md](workflows/pass-2-analytical.md) and [chapter-package.md](workflows/chapter-package.md). For each chapter:

1. Normalize and seal `source.md`.
2. Read text and non-text resources.
3. Build Evidence Ledger entries before prose claims.
4. Produce one main `reading.md` that leads the reader through the chapter rather than summarizing it.
5. Calculate the density score. Under plan B, always keep the main reading; if score is 60–74 add 2 topic readings, 75–89 add 3, and 90–100 add 4. Do not split below 60.
6. Produce `annotated.md`, `annotations.yaml`, and `knowledge.yaml` with traceable attribution.
7. Run the chapter gate before moving on.

### PASS 3 — Cross-chapter reading

Read [pass-3-synthesis.md](workflows/pass-3-synthesis.md). Trace concept evolution, claims, evidence reuse, contradictions, revisions, dependencies, and chapter roles. Synthesize the author's system; do not concatenate chapter summaries.

### PASS 4 — Critical reading

Read [pass-4-critical.md](workflows/pass-4-critical.md). Test assumptions, evidence strength, causality, selection bias, counterexamples, scope, age, and rival explanations. Keep author view, evidence, alternative view, and AI assessment separate.

### PASS 5 — Skill mining

Read [pass-5-skill-mining.md](workflows/pass-5-skill-mining.md). Score candidates for procedure, repeatability, defined inputs/outputs, decision logic, generalizability, known boundaries, and evidence. Generate only approved candidates and retain provenance and tests.

## Checkpoint and resume

Books may exceed one context window. Finish the current atomic unit, write ledger state, record unresolved items and the next locator, then stop. On resume, read `manifest.yaml`, both ledgers, the latest chapter card, and the next source unit. Never reconstruct progress from memory.

## Verification

Read [verification.md](workflows/verification.md). Run:

```bash
python3 scripts/validate_book_package.py /absolute/path/to/book-package
python3 -m unittest discover -s tests -p 'test_*.py'
```

Report coverage by chapters, sections, pages, paragraphs, figures, tables, equations, code blocks, footnotes, sidebars, and appendices. Classify each gap as `blocking`, `accepted`, or `not_applicable`; only `blocking: 0` allows final status.

## Common mistakes

| Failure | Corrective action |
|---|---|
| Smooth source prose by rewriting | Restore original wording; move explanation to Annotation |
| Write “author believes” without evidence | Add a source locator or relabel as AI inference |
| Treat figures as decoration | Inventory, transcribe/describe, interpret, and cite them |
| Produce bullet summaries as reading articles | Rebuild around question → reasoning → evidence → application → boundary |
| Split every long chapter | Use the density rubric; length alone is insufficient |
| Replace an evolved concept with one frozen definition | Preserve evolution history and identify final state |
| Generate one Skill per chapter | Evaluate procedural knowledge units across chapters |
| Hide uncertainty | Record uncertainty, failed OCR, missing pages, and unresolved conflicts |

## Resource map

- Schemas: `references/*schema*.md` and `references/locator-and-provenance.md`
- End-to-end workflows: `workflows/`
- Book-type adaptations: `profiles/`
- Copy-ready artifact shapes: `templates/`
- Deterministic checks and fixtures: `scripts/` and `tests/`
- Package intent and extension rules: `DESIGN.md`
