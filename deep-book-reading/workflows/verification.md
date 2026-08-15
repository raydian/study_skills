# Verification workflow

## Deterministic verification

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

Report artifact counts, PASS states, coverage by resource kind, blocking/accepted gaps, fidelity audit results, topic splits, candidate decisions, generated Skills, and the exact next action for any incomplete run.
