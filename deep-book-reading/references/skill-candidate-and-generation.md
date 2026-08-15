# Skill candidate evaluator and Agent Skill generation

## Skillability score

Score each dimension 0–4, apply the weight, and normalize to 100:

| Dimension | Weight |
|---|---:|
| Procedural: contains an actionable sequence | 20 |
| Repeatable across more than one instance | 15 |
| Inputs are identifiable | 10 |
| Outputs are identifiable | 10 |
| Decision logic is expressible | 15 |
| Generalizable beyond the book's case | 15 |
| Boundaries/failure modes are known | 10 |
| Evidence is adequate for intended claims | 5 |

Decision bands: `80–100 approve`, `65–79 hold/research`, `0–64 reject`. An automatic veto applies if the candidate is purely factual, only literary interpretation, unsafe without missing expertise, unsupported by Source, or dependent on inaccessible proprietary inputs.

## Candidate record

```yaml
candidate_id: sc-0012
name: "__VERB_LED_NAME__"
problem: "__TRIGGERING_PROBLEM__"
score: 86
decision: approve
dimensions: {procedural: 4, repeatable: 4, inputs: 3, outputs: 4, decision_logic: 4, generalizable: 3, boundaries: 3, evidence: 3}
source_units: [ku-method-0012, ku-rule-0008]
source_refs: [ch05-p044, ch08-p019]
risks: ["__RISK__"]
```

## Generation contract

Generated Agent Skills must:

1. Solve one recognizable problem and use a trigger-only description beginning with “Use when…”.
2. Separate book-derived rules from generalization or external additions.
3. Preserve `source_refs`, limitations, and transformations in `provenance.yaml`.
4. Include at least one positive scenario, boundary scenario, counterexample, and attribution/fidelity scenario under `tests/`.
5. Be validated against the original knowledge units and evidence before approval.

Never generate one Skill per chapter by default. Merge knowledge across chapters when it forms one coherent procedure; split only when triggers, inputs, or outputs differ materially.
