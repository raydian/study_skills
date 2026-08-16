# Book Manifest schema

The Book Manifest describes exactly what was received and what counts as complete.

```yaml
schema_version: 1
book_id: "__BOOK_SLUG__"
book:
  title: "__TITLE__"
  author: ["__AUTHOR__"]
  edition: "__EDITION__"
  language: "__LANGUAGE__"
  isbn: "__ISBN_OR_EMPTY__"
  publication_year: "__YEAR__"
source:
  format: pdf
  files: ["__SOURCE_FILE__"]
  authorization: user_provided
  authorization_note: "__NOTE__"
  searchable_text: true
  scanned_pages: false
  page_count_file: 0
  page_count_printed: 0
  missing_or_duplicate_pages: []
  source_state: staging
  # source-state: staging
  source_sha256: "__SOURCE_PDF_SHA256__"
ingestion:
  type: "__INGESTION_TYPE__"
  parser: "__INGESTION_PARSER__"
  conversion_dir: "__CONVERSION_DIR__"
  conversion_manifest: "__CONVERSION_MANIFEST__"
  provenance_index: "ingestion-provenance.json"
  source_pdf_sha256: "__SOURCE_PDF_SHA256__"
  gate_status: "__GATE_STATUS__"
  imported_at: "__ISO_8601__"
structure:
  front_matter: []
  chapters: []
  appendices: []
  notes_present: false
  bibliography_present: false
  index_present: false
resources:
  figures: 0
  tables: 0
  equations: 0
  code_blocks: 0
  footnotes: 0
  sidebars: 0
reading_profile:
  primary: "__PROFILE__"
  secondary: []
  rationale: "__RATIONALE__"
state:
  current_pass: 0
  status: in_progress
  next_unit: "pass0:source-integrity"
  blocking_issues: []
```

`ingestion` records validated conversion provenance: `type` identifies the importer; `parser` identifies its parser/version; `conversion_dir` must resolve below the project `markdown/` root; `conversion_manifest` must resolve to that directory's `conversion-manifest.json`; `provenance_index` must resolve inside the package to `ingestion-provenance.json`; `source_pdf_sha256` binds the package to its existing original PDF; `gate_status` must be `passed`; and `imported_at` is an ISO-8601 UTC timestamp. Relative paths resolve from the package root and may not escape the documented roots.

Package initialization and reuse rerun authoritative Gate P rather than trusting status text. `ingestion-provenance.json` records the conversion-manifest hash and, for every source unit, the chapter ID, contained conversion path/hash, contained package `source.md` path/hash, and an `assets` list of the package paths/SHA-256 values/byte sizes referenced by that source. The ordered source-unit IDs and paths must exactly reconcile with `split-index.json` and the actual `chapters/chNN/` set. Reuse additionally requires all root, chapter, and synthesis artifacts, every current package Markdown image link, every copied asset hash, and every expected chapter identity to match.

Set `source_state: sealed` only after source fidelity and locator checks. Store a SHA-256 for each sealed chapter Source or a deterministic combined Source hash. A correction after sealing creates `source_version: N+1`, records `supersedes`, and preserves the previous version or its hash.
