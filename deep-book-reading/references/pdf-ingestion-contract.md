# PDF ingestion contract

## Scope and identity

This contract applies before PASS 0 for every PDF. The authorized input PDF is identified by its absolute path and SHA-256. The bundled MinerU route may proceed only with one complete `auto/` output containing exactly one top-level Markdown file and at least one `*_content_list_v2.json` file.

## Directory schema

With `category=CATEGORY`, `title=TITLE`, and `slug=title-slug`, ingestion owns two roots:

```text
markdown/CATEGORY/TITLE/                 # Parsed Source / staging evidence
  TITLE.md                               # imported primary Markdown
  TITLE-格式化.md                        # atomically persisted structural normalization
  normalization-log.json                # complete normalization audit
  images/                                # copied local image assets
  mineru/                                # copied JSON provenance artifacts
  拆分/README.md
  拆分/章节/*.md                          # high-confidence chapter splits
  拆分/split-index.json                  # ordered source spans and coverage proof
  conversion-manifest.json
books/title-slug/                        # initialized deep-reading package
  manifest.yaml
  ingestion-provenance.json              # conversion-to-package source identities
  chapters/chNN/source.md                # staging Source candidate
```

The parsed-source root is not canonical Source and cannot be sealed. The package creates a chapter Source candidate from it; after source review and Gate B, that candidate may become immutable canonical Source.

## Conversion manifest

`conversion-manifest.json` has schema version 2 and records:

- `book`: `title`, `category`, stable `slug`, and `language`.
- `source`: absolute original `pdf`, `sha256`, byte `size`, `mtime_ns`, and fingerprint timestamp.
- `engine`: `name` (`MinerU`), nonempty `version`, `backend`, `language`, executable, exact `command`, and execution mode. In `run` mode the nine command fields must bind that executable, the absolute fingerprinted PDF, absolute output staging directory, backend, and language exactly. Importing existing output records an empty command and `import-existing-output` mode because MinerU was not executed by that command.
- `timestamps`: MinerU/conversion start and completion times.
- `pages`: `source_count`, `mineru_count`, `reconciliation`, and nonempty page `records` derived from structured content-list objects with explicit page identities. Positional enumeration is not a page identity.
- `artifacts`: path, SHA-256, and size for the four distinct canonical identities `TITLE.md`, `TITLE-格式化.md`, `normalization-log.json`, and `拆分/split-index.json`.
- `stages`: `imported`, `formatted`, and `split` objects. Each uses status `complete`, a completion timestamp, and the exact path/hash/size output set owned by that stage; cross-stage aliases and unexpected outputs are invalid.
- `resources`: image and MinerU JSON records with conversion-relative path, SHA-256, size, and original-path provenance. Every MinerU JSON path starts with `mineru/`; image records also include source-page provenance, which may be null when MinerU does not expose a reliable mapping.
- `warnings`: objects with `code`, `message`, and classification `accepted`, `blocking`, or `not_applicable`.
- `validation`: Gate P status `pending`, `passed`, or `failed`, integer `blocking_count`, issue list, and validation timestamp.

Stage status and gate status are separate vocabularies: a stage becomes `complete`; Gate P becomes `passed` or `failed`; the validator report uses the same `passed`/`failed` gate vocabulary. Gate P accepts only `validation.status: passed`, `validation.blocking_count: 0`, and an empty issue list. The CLI first runs authoritative validation while status is `pending`, persists `passed` only for a zero-blocker report, and validates the persisted record again. Package initialization always reruns the same validator instead of trusting stored fields.

## Source fingerprint and atomic publication

Resolve the PDF to an absolute path and capture SHA-256, byte size, and nanosecond mtime before MinerU. Recompute all fields after MinerU and again after import; any change blocks publication. `run_mineru` uses an argument list with `shell=False`, a positive timeout, captured text output, and explicit backend/language.

Build raw Markdown, formatted Markdown, normalization log, copied resources, split files, split index, manifest, and passed Gate P inside one newly created sibling staging directory. Reject symlinked publication components and paths that resolve outside configured roots. Publish the complete directory atomically; on replacement failure restore the preceding generation. Never merge files into the live conversion directory.

Before conversion, compare an existing manifest, source hash, and a fresh integrity report. Reuse only a currently valid conversion with the same PDF hash. Integrity includes rejecting undeclared files present under `images/`, `mineru/`, or `拆分/章节/`, so injected or stale files cannot silently become part of a reused generation. A different/unknown hash is rejected by default. `--conflict-policy replace` permits a verified operator-requested conversion replacement, but it does not overwrite a same-slug book package bound to another PDF; use a new title/slug for that case.

## Permitted conversion normalization

The raw import preserves wording and order. It may only rewrite a local image path when a collision-safe copied image name is required, and that rewrite also skips every protected Markdown state. Formatting may remove an unambiguous page-edge page number or repeated short header/footer. Ambiguous lexical hyphens and line breaks are preserved by default; no automatic word join is permitted. YAML front matter, fenced/indented code, CommonMark raw-HTML blocks (including `details`/`summary`), comments, declarations, and other protected Markdown blocks are statefully preserved. Formatting must not paraphrase, silently correct OCR, delete body text, invent headings, translate, or convert parsed Markdown directly into sealed Source. Every applied change is persisted in `normalization-log.json` and hashed in the manifest; Gate P recomputes both the formatted text and audit list from the raw artifact.

## Chapter splitting and assets

Split only recognized Chinese `第…章/节/篇/部` H1/H2 headings outside an explicit table-of-contents region and outside protected Markdown states. Preserve front matter and all content before the first chapter by attaching that prefix to the first ordered chapter unit. `split-index.json` records formatted-source path/hash/character count plus each unit's ordered `[start,end)` span, source-slice hash, file hash, and explicit classified exclusions. The union of ordered unit/exclusion spans must cover the formatted source exactly, and each chapter file must equal the deterministic image-path rendering of its declared source span. If no high-confidence split exists, record `formatted_fallback` with the formatted artifact as the sole full-span unit; package initialization must use the formatted artifact, never the raw import.

Copy all local MinerU images into `images/` and preserve all JSON under `mineru/`. Rewrite imported Markdown references only to the copied local assets, resolving collision-safe names deterministically. Validate inline images, angle-bracket destinations, full/collapsed/shortcut reference images, and their reference definitions outside protected blocks. A reference-image use without a definition is blocking rather than invisible. Every local target must remain contained below the conversion root, exist, and appear in the hashed resource manifest. When package initialization creates `chapters/chNN/`, copy referenced assets into that chapter's `assets/` directory and rewrite only those local references. `ingestion-provenance.json` records each package asset path/hash/size beside its source unit; reuse rescans every package Markdown link and requires the current link set and asset hashes to match. A missing, escaping, symlinked, unmanifested, unresolved, or hash-mismatched local image is blocking.

## Page tracing

Preserve explicit page markers from parsed Markdown and retain MinerU content-list JSON so page evidence remains auditable. Gate P requires at least one content-list resource and nonempty structured page records; every entry must be an object with an explicit nonnegative page identity. Record both `source_count` and `mineru_count`: `matched` is required when a structural PDF count is observable; `source_count_unavailable` requires an accepted classified warning; an unexplained mismatch is blocking. PASS 0 must still reconcile file pages, printed pagination, and conversion page markers. Every later locator or page claim traces through the staged conversion and the PDF SHA-256, not an unverified page guess.

## Gate P failure and resumption

Gate P blocks PASS 0 if discovery, execution, output completeness, artifact/stage hashes, page records/reconciliation, warning classification, split coverage, any Markdown image form, manifest identity, package provenance, source hash binding, or `ingestion.gate_status` fails. Re-ingest after correcting the cause. Existing-package reuse requires every root/chapter/synthesis artifact plus `ingestion-provenance.json`; conversion-manifest identity and every conversion/package source-unit path/hash must still match. A different/unknown hash, missing artifact, or changed source identity is preserved and reported, never partially overwritten.
