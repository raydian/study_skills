# PASS 0 — Survey and intake

## Entry

At least one source file or complete chapter collection is available.

For a PDF package, Gate P has passed before PASS 0. Run package verification rather than trusting stored status: require contained conversion/provenance paths, authoritative conversion report `passed`, persisted zero-blocker gate, current original-PDF hash, and matching conversion/package source-unit provenance. Parsed Markdown and the formatted fallback remain staging evidence; do not seal any `source.md` during intake.

## Procedure

1. For a PDF, refuse to start if revalidation finds a missing/malformed manifest, changed PDF, incomplete or cross-owned stage output, noncanonical artifact, undeclared/missing/hash-mismatched resource, unresolved image/reference, split coverage/identity gap, unclassified/blocking warning, escaping path, or ordered package source/asset provenance mismatch—even when stored text says `passed`. Report the blocking ingestion issue and return to [pdf-ingestion.md](pdf-ingestion.md).
2. Record title, author, edition, language, publication metadata, file format, authorization basis, and file identity in the Book Manifest.
3. Compare file page count, printed pagination, table of contents, front/back matter, appendices, notes, bibliography, and index. Record missing, duplicate, blank, rotated, or corrupt pages.
4. Determine searchable text versus scan. Sample front, middle, and back pages for extraction/OCR quality.
5. Inventory chapters, sections, paragraphs, figures, tables, equations, code blocks, footnotes/endnotes, sidebars, captions, and appendices.
6. Select a primary reading profile and optional secondary profile.
7. Create Reading Ledger totals, PASS states, known gaps, and first resumable unit.
8. Create an empty Evidence Ledger using the reference schema.

## Exit gate

Pass only when the received object is unambiguously described, authorization is recorded, page mapping is known, and missing content is classified. For PDF input, this additionally requires the verified Gate P record. An incomplete source may proceed for partial work but cannot reach final whole-book status.
