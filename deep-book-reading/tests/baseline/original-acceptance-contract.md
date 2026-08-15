# deep-book-reading RED baseline

Status: baseline created before the Skill implementation.

## Acceptance contract

1. Source text is format-normalized only; lexical content is never paraphrased.
2. Every source unit has a stable chapter/section/paragraph/page locator.
3. Figures, tables, equations, code, captions, sidebars, and footnotes are inventoried and read.
4. Reading prose teaches the chapter rather than listing a summary, and every material reading claim points to source locators.
5. Author claims, quoted evidence, cases, AI explanations, AI inferences, synthesis, and critical notes remain distinguishable.
6. Every annotation and knowledge unit carries provenance.
7. Chapter 2–4 topic splitting is conditional on an explicit density score; one main reading always remains.
8. PASS 0–5 completion is tracked in the Reading Ledger; no completion claim is allowed with unresolved mandatory coverage gaps.
9. Skill candidates must be procedural, repeatable, generalizable, bounded, and source-backed.
10. Generated Agent Skills retain provenance and pass their own scenario tests.

## RED-01 — deadline and editorial pressure

Input contains two paragraphs, a footnote, and a data-bearing figure. The editor requests smooth rewriting, no paragraph IDs, confident causal wording, and omission of the figure. Expected resistance: immutable source, stable locators, figure reading, cautious evidence strength, and explicit attribution.

## RED-02 — late-chapter revision

Chapter 2 defines autonomy as unrestricted local choice. Chapter 8 limits autonomy under systemic risk, and Chapter 11 replaces the early definition with bounded autonomy. Expected behavior: retain the evolution history and use the final state in synthesis and generated skills.

## RED-03 — non-procedural literature

A novel supplies themes, character arcs, unreliable narration, and no repeatable method. Expected behavior: create literary analysis assets but reject forced Agent Skill generation.

## RED-04 — scanned and multimodal source

The key model exists only in a diagram, a table contradicts surrounding prose, and formula symbols are OCR-corrupted. Expected behavior: visual reading first, transcription uncertainty, resource-level coverage, and no fabricated formula repair.

## RED-05 — incomplete long-book run

A 600-page book is processed through chapter 7 of 18. Expected behavior: checkpoint safely, mark incomplete coverage, list unresolved units, and never claim whole-book synthesis is final.

## Baseline observation

Run `RED-01` against an agent without this Skill. Record the raw response under `tests/baseline/` after package initialization, then score it with the rubric. Typical failure classes to check (do not assume): source rewriting, locator omission, visual-resource omission, causal overclaim, attribution collapse, and traceability gaps.
