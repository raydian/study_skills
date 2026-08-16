# Artifact contract

## Required root artifacts

| Artifact | Audience | Mutability | Purpose |
|---|---|---:|---|
| `BOOK.md` | human | revisable | navigation, scope, current status |
| `manifest.yaml` | AI/system | versioned | Book Manifest, source identity, structure, authorization |
| `reading-ledger.yaml` | AI/system | append/update | Reading Ledger and PASS/coverage state |
| `evidence-ledger.yaml` | AI/system | append/update | Evidence Ledger linking derived claims to Source |

## PDF parsed-source artifacts

For PDF input, `markdown/<category>/<title>/` is a separately and atomically published parsed-source generation. It contains raw `<title>.md`, formatted `<title>-格式化.md`, `normalization-log.json`, hashed `images/`, hashed `mineru/` JSON evidence, `拆分/split-index.json`, chapter splits when reliable, and schema-v2 `conversion-manifest.json`. It is staging evidence and must not be represented as sealed Source. Formatting preserves ambiguous lexical hyphens and protected Markdown states. If splitting is unavailable, the formatted artifact—not raw Markdown—is the package source unit.

The initialized package root is `books/<title-slug>/`; its `chapters/chNN/source.md` files begin in staging and become canonical Source only after Gate B sealing. `manifest.yaml` must retain `ingestion.conversion_dir`, `ingestion.conversion_manifest`, `ingestion.provenance_index`, `ingestion.source_pdf_sha256`, and `ingestion.gate_status: passed`. Package-local `ingestion-provenance.json` binds every ordered chapter ID and package source hash to its conversion source-unit path/hash and conversion-manifest hash, and binds every source-referenced copied asset by package path/hash/size. Reuse requires exact split/chapter/provenance identity and rescans all current package Markdown image links.

## Required chapter artifacts

### `source.md`

Canonical formatted original. Preserve wording, order, emphasis, quotations, notes, and resource associations. Permitted normalization is structural: remove repeated headers/footers, repair verified line wrapping and broken words, restore heading/list/table/code/formula boundaries, and attach stable IDs. Record uncertain OCR literally plus an uncertainty note outside the source text. After review, add `<!-- source-state: sealed -->` and hash the file in the manifest. Source is immutable after sealing.

### `reading.md`

One main guided-reading article for every chapter. It is publishable on WeChat, Zhihu, blogs, or paid communities after ordinary editorial review. It must explain the chapter's question, reasoning path, concepts, evidence, examples, boundary conditions, connection to the whole book, and implications. Each material claim uses a reading claim ID and visible or machine-readable `source_refs`.

High-density chapters may add `reading-topic-01.md` through `reading-topic-04.md`; these supplement rather than replace the main article.

### `annotated.md`

Source-oriented Markdown with compact callouts for AI/human inspection. Keep quoted source visually distinct from `[!AUTHOR-CLAIM]`, `[!EVIDENCE]`, `[!CASE]`, `[!AI-EXPLANATION]`, `[!AI-INFERENCE]`, `[!CRITICAL-NOTE]`, and `[!RELATION]` callouts.

### `annotations.yaml`

Machine-readable semantic layer. Annotation is revisable; include revision metadata and provenance. Never inject annotations into `source.md`.

### `knowledge.yaml`

Only the 12 canonical knowledge types: Concept, Definition, Claim, Principle, Framework, Method, Pattern, Rule, Evidence, Case, Counterexample, Limitation. A unit may link to annotations and other units but must point directly to Source.

## Required synthesis artifacts

- `book-map.md`: book questions, architecture, chapter roles, dependencies.
- `core-thesis.md`: central thesis and supporting hierarchy.
- `concept-evolution.md`: initial, extended, constrained, revised, and final concept states.
- `argument-map.md`: claims, reasons, evidence, counterarguments, limitations, conclusions.
- `critical-reading.md`: assumptions, evidence quality, alternatives, applicability.
- `full-book-reading.md`: a human guided reading of the whole system, not chapter-summary concatenation.

## Separation invariant

`Source != Reading != Annotation != Knowledge != Synthesis != Generated Skill`.

Derived layers may quote or reference Source but may not impersonate it. Every transformation records its attribution class and `source_refs`.
