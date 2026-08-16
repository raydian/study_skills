# PDF ingestion workflow

Run this workflow before PASS 0 whenever the source is a PDF. Read [pdf-ingestion-contract.md](../references/pdf-ingestion-contract.md) first. It uses the bundled MinerU CLI; parsed Markdown is staging evidence, not sealed Source.

## 1. Check the input

Confirm that the PDF is authorized, readable, complete enough for the requested scope, and has a stable absolute path. Choose a single path-safe `category` and `title`; they determine the output roots. The CLI records SHA-256, size, and mtime before MinerU and rejects a pre/post fingerprint change. Do not start a summary or PASS 0 while conversion is pending.

## 2. Discover MinerU and run conversion

Run from the target project root. The CLI discovers MinerU in this order: `--mineru-bin`, `MINERU_BIN`, `PATH`, `.venv-mineru/bin/mineru`, then `.venv/bin/mineru`.

```bash
python3 skills/deep-book-reading/scripts/ingest_pdf.py run \
  --pdf /absolute/path/to/book.pdf --category "CATEGORY" --title "TITLE" \
  --language "LANGUAGE"
```

Use `--language ch` only for Chinese PDFs; select the appropriate MinerU language code for every other PDF. The CLI defaults to `ch`, so state the caller-selected language explicitly whenever the source is not Chinese. Use `--mineru-bin /absolute/path/to/mineru` when discovery needs an explicit executable. The command runs MinerU with the declared backend/language, verifies complete output and the unchanged PDF fingerprint, then builds the entire conversion in one controlled sibling staging directory. Raw import, formatted artifact, normalization log, resources, split coverage index, schema-v2 manifest, and Gate P must all validate before the directory is atomically published and the package is initialized.

## 3. Import a completed MinerU result

If conversion already completed, do not run it again. Its supplied directory may be the `auto/` directory or its parent:

```bash
python3 skills/deep-book-reading/scripts/ingest_pdf.py import-mineru \
  --pdf /absolute/path/to/book.pdf --mineru-output /absolute/path/to/mineru-output \
  --category "CATEGORY" --title "TITLE"
```

Before either command runs MinerU or imports files, it validates any existing conversion. A complete matching conversion is reused without rewriting. A different/unknown source hash stops by default. After explicitly verifying that replacing the conversion is safe, pass `--conflict-policy replace`; this never authorizes replacement of an existing same-slug package tied to another PDF.

## 4. Validate and inspect the two roots

The CLI prints both roots. They must be:

```text
markdown/<category>/<title>/
  <title>.md
  <title>-格式化.md
  normalization-log.json
  images/
  mineru/
  拆分/split-index.json
  conversion-manifest.json
books/<title-slug>/
  manifest.yaml
  ingestion-provenance.json
  chapters/chNN/source.md
```

You may rerun the conversion validator independently:

```bash
python3 skills/deep-book-reading/scripts/ingest_pdf.py validate \
  --conversion-dir markdown/<category>/<title>
```

Require a zero exit status plus report `status: passed`, manifest `validation.status: passed`, `validation.blocking_count: 0`, and an empty issue list. The authoritative validator checks schema, source identity, nonempty exact run-command provenance, distinct canonical raw/formatted/log/split artifacts, explicit content-list page identities, page reconciliation, exact stage outputs, declared-only resource/split files, resource path/hash containment, every Markdown image/reference form (including unresolved definitions), split-span coverage, classified warnings, and the recorded gate. The package's `manifest.yaml` must then show `ingestion.gate_status: passed`, the same PDF SHA-256, contained conversion paths, and `ingestion-provenance.json`. `books/<title-slug>/chapters/chNN/source.md` is initialized in staging; it is not sealed until Gate B.

## Resume and stop rules

For an existing package with the same PDF hash, rerunning the command returns it only after package integrity, required artifacts, exact ordered conversion/source-unit/chapter identities, current package Markdown image links, copied-asset hashes, and ingestion provenance all pass. An existing package with a different/unknown hash, a missing artifact/asset, or mismatched provenance is a blocking condition: preserve it, inspect it, and resolve the discrepancy instead of overwriting it.

Stop before PASS 0 and report the exact failure when the PDF is missing or changes, MinerU cannot be found or fails/times out, `auto/` lacks required Markdown/content-list/page records, an artifact/resource/stage/split/image/warning check fails, a destination component is symlinked, the manifest is invalid, or package identity/provenance does not match. When no chapter heading is reliable, use the manifest-declared formatted fallback rather than raw Markdown. Request a corrected PDF or corrected/re-ingested conversion; never bypass Gate P with a summary.
