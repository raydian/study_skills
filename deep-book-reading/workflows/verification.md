# Verification workflow

## Deterministic verification

For a PDF package, verify Gate P before any PASS or package completion check:

1. Resolve package-relative paths from the package root. Require `ingestion.conversion_dir` below the sibling project `markdown/` root; require `ingestion.conversion_manifest` to resolve to `<conversion_dir>/conversion-manifest.json`; require `ingestion.provenance_index` to resolve to package-local `ingestion-provenance.json`. Reject absolute or relative paths that escape their allowed roots and every symlink escape.
2. Read schema-v2 conversion identity. Require `source.pdf` to be the existing absolute original PDF; recompute SHA-256 and size; require the hash to equal conversion `source.sha256`, package `ingestion.source_pdf_sha256`, package `source.source_sha256`, and package provenance. Verify nonempty backend/language/executable/version, timestamps, and either the exact nine-field run command bound to the source/output/backend/language or the documented empty import command.
3. Rerun the bundled conversion validator. Require report `passed`, every stage `complete`, `validation.status: passed`, `validation.blocking_count: 0`, and no issues. Confirm the four distinct canonical raw/formatted/log/split-index paths and hashes, recomputed raw-to-formatted text/audit derivation, one content-list JSON with explicit structured page identities, valid `source_count`/`mineru_count` reconciliation, exact ordered split coverage and deterministic split-file derivation, and classified warnings with zero blocking entries.
4. Resolve every path/hash/size in the exact stage output sets and `resources.images`/`resources.mineru_json` below the conversion root. Require MinerU JSON paths to begin `mineru/` and reject undeclared files under `images/`, `mineru/`, or `拆分/章节/`. Re-scan all Markdown outside protected blocks for inline, angle-bracket, full/collapsed/shortcut reference images; unresolved definitions block, and each local target must be contained, present, hashed, and manifested.
5. Validate `ingestion-provenance.json`: conversion manifest hash, exact ordered split-unit/chapter IDs, conversion source-unit paths/hashes, package source paths/hashes, package asset paths/hashes/sizes, and all required root/chapter/synthesis artifacts. Re-scan current package Markdown image links. Existing-package reuse fails closed on any discrepancy.
6. If any check fails, mark Gate P blocking; do not advance PASS 0 or claim package completion. Preserve the existing generation and package, then re-ingest or correct the source explicitly.

Run the bundled validator on the output book package. Resolve errors before finalization. Warnings require an explicit disposition.

## Semantic verification

1. Recompute inventory totals from the Source layer and compare them with the Reading Ledger.
2. Resolve every `source_ref`; flag missing and dangling targets.
3. Sample claims by importance and confidence, including all low-confidence/high-impact items.
4. Compare the original context, derived wording, attribution, evidence strength, and carried limitations.
5. Review all figures/tables/equations/code/notes marked essential or contradictory.
6. Verify later concept revisions appear in synthesis and generated Skills.
7. Check topic-reading count against density score and inspect overlap.
8. Run generated-Skill scenario tests and inspect for prescriptive overreach.

## Completion report

Report Gate P status and conversion-manifest path for PDF input, then artifact counts, PASS states, coverage by resource kind, blocking/accepted gaps, fidelity audit results, topic splits, candidate decisions, generated Skills, and the exact next action for any incomplete run.
