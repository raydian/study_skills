# Locator and provenance protocol

## Stable IDs

Use zero-padded IDs that remain stable across derived artifacts:

| Unit | Pattern | Example |
|---|---|---|
| chapter | `chNN` | `ch03` |
| section | `chNN-sNN` | `ch03-s02` |
| paragraph | `chNN-pNNN` | `ch03-p028` |
| figure | `chNN-figNNN` | `ch03-fig004` |
| table | `chNN-tblNNN` | `ch03-tbl002` |
| equation | `chNN-eqNNN` | `ch03-eq007` |
| code | `chNN-codeNNN` | `ch03-code003` |
| footnote | `chNN-fnNNN` | `ch03-fn011` |
| sidebar | `chNN-sideNNN` | `ch03-side002` |
| reading claim | `r-chNN-NNN` | `r-ch03-014` |
| annotation | `ann-chNN-NNN` | `ann-ch03-021` |
| knowledge unit | `ku-<type>-NNNN` | `ku-claim-0042` |
| evidence | `ev-NNNN` | `ev-0291` |

Do not encode mutable titles into IDs. Preserve printed page labels separately because PDF indices and printed pages can differ.

## Source markup

```markdown
<!-- chapter: ch03; source-pages: 067-092 -->
# Chapter title

<!-- section: ch03-s02; page: 076; pdf-index: 88 -->
## Section title

<p id="ch03-p028">Exact normalized source wording.</p>

<figure id="ch03-fig004" page="077">
  <figcaption>Exact caption.</figcaption>
  <!-- asset: assets/ch03-fig004.png -->
</figure>
```

## Derived provenance

Every material derived item has:

```yaml
source_refs:
  - ref: ch03-p028
    pages: ["076"]
    relation: supports
    quote_hash: "sha256:__HASH__"
attribution: ai_explanation
confidence: 0.92
```

Allowed `relation` values: `defines`, `states`, `supports`, `illustrates`, `qualifies`, `contradicts`, `revises`, `derived_from`, `criticizes`.

Allowed `attribution` values:

- `author_claim`: explicit author position.
- `source_evidence`: data, study, quotation, or observation offered as evidence.
- `quoted_view`: another person's view quoted or summarized by the author.
- `case`: story or application; not automatically evidence.
- `ai_explanation`: faithful clarification without adding a new conclusion.
- `ai_inference`: conclusion derived by AI but not explicit in Source.
- `ai_synthesis`: multi-source integration across units/chapters.
- `critical_analysis`: evaluation, objection, alternative explanation.
- `editorial_note`: human-facing clarification or publishing note.

## Traceability rule

A derived claim with no valid `source_refs` is either removed, marked as an external addition with its own citation, or explicitly labeled unsupported. Never backfill a convenient source that does not actually entail the claim.
