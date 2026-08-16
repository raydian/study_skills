# Quality gates

## Gate P — PDF conversion provenance

Applicable only to PDF input and required before PASS 0.

- The original absolute PDF exists; SHA-256, size, and mtime were captured before MinerU and matched after execution/import. MinerU produced one primary Markdown file, at least one content-list JSON, and nonempty structured records with explicit page identities.
- The schema-v2 manifest records nonempty backend/language/executable/version, an exact source/output/backend/language-bound command or documented import mode, timestamps, source/MinerU page counts and reconciliation, four distinct canonical raw/formatted/log/split artifacts, exact stage outputs, hashed resource provenance, classified warnings, `validation.status: passed`, zero blockers, and no issues.
- Formatted Markdown and its normalization audit recompute exactly from raw Markdown. Split spans plus explicit classified exclusions cover formatted Markdown exactly, each split file recomputes from its source span, protected Markdown cannot be rewritten or create chapter boundaries, and prefix/front matter is preserved. With no reliable chapter, the full formatted artifact is the declared fallback.
- Every local inline or full/collapsed/shortcut reference image is defined, contained, present, hashed, and manifested. JSON paths use `mineru/<relative-path>`.
- `books/<slug>/manifest.yaml` records matching PDF identity, contained conversion paths, `ingestion.gate_status: passed`, and package-local `ingestion-provenance.json`; exact ordered chapter/source identities, current Markdown image links, copied-asset hashes, and all required package artifacts revalidate before reuse.
- Conversion publication is an atomic complete-directory generation below non-symlinked configured roots; no undeclared or stale image, JSON, or split file from another generation remains.
- A failed, incomplete, missing, or hash-mismatched conversion blocks PASS 0 and every later PASS. Re-ingest or correct it; never bypass Gate P by summarizing parsed text.

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
