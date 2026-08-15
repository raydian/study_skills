# Quality gates

## Gate A — Intake integrity

- Edition and source files identified.
- Authorization recorded.
- Missing, duplicate, rotated, corrupt, or unreadable pages listed.
- Printed page mapping established.
- Text and every non-body resource kind inventoried.

## Gate B — Source fidelity and immutability

- Headings, paragraphs, lists, quotations, tables, notes, formulas, and code boundaries restored.
- No lexical paraphrase in `source.md`.
- Stable locator uniqueness passes.
- A stratified sample (front/middle/back plus OCR-risk pages) matches the source.
- Source is sealed and hashed; post-seal correction policy is active.

## Gate C — Chapter package

- One main guided-reading article exists.
- Density score and topic split decision are recorded.
- Material reading claims have IDs and `source_refs`.
- Author/quoted/AI/critical attribution is explicit.
- All chapter resources are reviewed or have classified gaps.
- Knowledge units use canonical types and preserve limitations.

## Gate D — Synthesis

- Concept evolution includes later revisions.
- Argument map connects claims, reasons, evidence, counterarguments, and boundaries.
- Conflicts are represented rather than averaged away.
- Full-book reading explains the system rather than concatenating chapter summaries.

## Gate E — Critical reading

- Assumptions, evidence strength, causality, samples, selection effects, recency, scope, counterexamples, and rival explanations reviewed where applicable.
- Critical claims are labeled `critical_analysis` and point to the evaluated Source.

## Gate F — Skill mining

- Every candidate has a Skillability score and veto check.
- Approved Skills retain provenance, boundaries, and scenario tests.
- Generated Skill guidance does not strengthen the book's claim beyond its evidence.

## Final completion rule

Completion requires all applicable gates, required coverage targets, zero blocking gaps, no dangling `source_refs`, and a fidelity audit. Report accepted gaps explicitly; do not hide them inside an average score.

## Fidelity audit

Sample high-impact claims and all low-confidence claims. For each, compare the derived statement with its exact source context, attribution, evidence strength, and limitations. Mark `faithful`, `overstated`, `underqualified`, `misattributed`, or `unsupported`; any non-faithful high-impact claim blocks finalization.
