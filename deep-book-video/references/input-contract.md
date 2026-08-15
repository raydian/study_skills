# Input contract

## Preferred input

The preferred input is a completed `deep-book-reading` package with:

- `manifest.yaml`, source authorization, edition identity, completeness, and stable locator rules;
- `reading-ledger.yaml` with zero blocking coverage gaps;
- `evidence-ledger.yaml` linking claims to exact source units;
- chapter `knowledge.yaml` files and source locators;
- `synthesis/book-map.md`, `core-thesis.md`, `argument-map.md`, `critical-reading.md`, and `full-book-reading.md`;
- visual-resource descriptions where figures, art, layout, equations, or tables carry meaning.

Do not edit or silently repair the input knowledge package. Record detected problems in `input-audit.md` and route corrections back to the knowledge-building stage.

## Equivalent inputs

Accept another deep knowledge base only if an adapter can provide the same logical fields:

```text
source identity and authorization
stable source locator
knowledge unit ID and type
faithful statement
attribution class
source_refs
evidence kind, strength, directness, and limitation
relationships and prerequisites
book-level synthesis and critical boundaries
unresolved gaps and uncertainty
```

If the input is prose without stable locators, create a provisional source map and label the project `provenance_state: provisional`. A provisional project may produce an outline or prototype, but it cannot pass the Evidence Gate or be called source-faithful.

## Intake audit

Record:

| Field | Required decision |
|---|---|
| source status | authorized, public domain, licensed, user-provided, or unknown |
| edition | exact edition/translation and page mapping |
| completeness | complete, incomplete, or sampled |
| provenance | sealed/stable, usable, provisional, or absent |
| evidence coverage | strong, mixed, weak, or absent |
| visual dependence | none, helpful, material, or essential |
| interpretive plurality | low, medium, or high |
| spoiler policy | none, light, necessary, or full |
| blocking gaps | exact missing or unresolved source units |

## Source map rules

Every material page claim uses one or more `source_refs`. A reference should identify the book package locator and relation, for example:

```json
{"ref": "ch05-p044", "pages": ["121"], "relation": "states"}
```

For an external contextual fact, use an external source record with title, author/publisher, publication date, stable URL or identifier, access date, and relation. Do not disguise external context as the book author's claim.

The following are never evidence references:

- an AI-generated background or reconstruction;
- an image prompt;
- an unsourced model recollection;
- a search-result snippet;
- another summary that does not expose its primary source.

## Attribution vocabulary

Use the input package vocabulary where available: `author_claim`, `source_evidence`, `quoted_view`, `case`, `ai_explanation`, `ai_inference`, `ai_synthesis`, `critical_analysis`, or `editorial_note`.

Exact quotations require exact source text and locator. Paraphrases must not use quotation marks. Interpretations with multiple plausible readings must name the perspective and retain alternatives where material.
