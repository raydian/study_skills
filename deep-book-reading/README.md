# deep-book-reading

`deep-book-reading` turns a complete authorized book into a traceable book knowledge package: immutable formatted source, publishable chapter deep readings, AI annotations, normalized knowledge units, cross-chapter synthesis, critical reading, and selected Agent Skills.

## Key guarantees

- Source wording is never rewritten after normalization and sealing.
- Every material interpretation can be traced to stable source locators.
- Author statements, evidence, quotations, cases, AI explanations, AI inferences, synthesis, and critique remain distinguishable.
- Figures, tables, equations, code, captions, sidebars, and footnotes count toward reading coverage.
- Every chapter gets one main deep reading; only high-density chapters receive 2–4 additional topic readings.
- PASS 0–5 progress is resumable through the Book Manifest, Reading Ledger, and Evidence Ledger.
- Skill generation is selective and provenance-preserving.

## Installation

Copy the `deep-book-reading` directory into a Codex-compatible skills directory, or invoke it directly from its current path. The folder name must remain `deep-book-reading`.

## Typical invocation

```text
Use $deep-book-reading to process this authorized PDF as a complete book package.
Create one publishable main reading per chapter, split only high-density chapters,
and do not finalize until all source and multimodal coverage gates pass.
```

## What it produces

See `SKILL.md` for the canonical output tree. Templates live under `templates/`; detailed schemas live under `references/`; PASS workflows live under `workflows/`; book adaptations live under `profiles/`.

## Validation

```bash
python3 scripts/validate_book_package.py /absolute/path/to/book-package
python3 -m unittest discover -s tests -p 'test_*.py'
```

For PDF packages the validator also resolves conversion/provenance paths within allowed roots, recomputes the original PDF hash, reruns authoritative Gate P over exact schema-v2 artifacts/stages/resources/links/splits/warnings, and verifies ordered package source-unit plus copied-asset provenance. It rejects unresolved references and undeclared files, then rescans current package Markdown image links. It also checks structure, sealed Source markers, stable paragraph IDs, traceable reading claims, attribution fields, PASS state, resource-kind coverage, and synthesis files. It cannot prove semantic fidelity by itself; the workflow therefore adds quote sampling and human/AI fidelity review.

## Copyright and privacy

Only create a complete Source layer from user-provided, public-domain, licensed, or otherwise authorized material. Keep copyrighted full text internal to the authorized workflow and publish only permitted transformations. Do not send private book files to external services without authorization.

## Start here

1. Read `SKILL.md`.
2. Copy the templates into a new book package.
3. Complete PASS 0 and choose a profile.
4. Process chapters through PASS 2, checkpointing ledgers.
5. Complete PASS 3–5 and run verification.

`DESIGN.md` explains the architecture and extension rules.
