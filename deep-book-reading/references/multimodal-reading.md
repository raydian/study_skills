# Multimodal and non-body reading

Inventory non-body resources during PASS 0 and assign stable IDs before interpretation.

## Resource protocol

| Kind | Read for | Preserve |
|---|---|---|
| figure/diagram | structure, direction, encoding, comparison, omitted variables | image, caption, legend, labels, page |
| table | headers, units, denominators, totals, anomalies | cell text, notes, page |
| equation | symbols, definitions, assumptions, derivation role | exact expression, numbering, page |
| code | language, dependencies, inputs/outputs, claimed result | exact code, caption, page |
| footnote/endnote | qualification, citation, exception, attribution | marker, note text, backlink |
| sidebar/callout | example, exception, practice, alternate voice | bounds, heading, page |

For scanned pages, inspect page images first. Use OCR as a draft transcription, then verify names, negation, numbers, units, formula symbols, table boundaries, and hyphenation visually. If confidence is insufficient, preserve the uncertain reading, tag it `uncertainty`, and open a blocking gap; never silently guess.

## Figure reading record

Record `resource_id`, `page`, `caption`, `description`, `data_or_relations`, `role_in_argument`, `source_refs`, `confidence`, and `open_questions`. Treat a data-bearing figure as evidence even when prose does not repeat its values.

## Contradictions

If visual material conflicts with prose, do not reconcile it by invention. Create a contradiction record, cite both resources, describe exactly what differs, and carry the issue into critical reading.
