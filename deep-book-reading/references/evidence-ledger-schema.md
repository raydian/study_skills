# Evidence Ledger schema

The Evidence Ledger records how claims are supported, qualified, contradicted, or derived.

```yaml
schema_version: 1
evidence:
  - id: ev-0291
    statement: "__WHAT_THE_SOURCE_SUPPORTS__"
    evidence_kind: study
    attribution: source_evidence
    source_refs:
      - ref: ch07-p018
        pages: ["183"]
        relation: supports
    strength: moderate
    directness: direct
    limitations: ["small_sample"]
    supports: ["ku-claim-0034"]
    contradicts: []
claims:
  - id: ku-claim-0034
    statement: "__CLAIM__"
    attribution: author_claim
    source_refs:
      - ref: ch07-p016
        pages: ["182"]
        relation: states
    evidence_refs: [ev-0291]
    confidence: 0.82
```

Evidence kinds include `data`, `study`, `quotation`, `observation`, `case`, `example`, `diagram`, `table`, `equation`, `code_result`, and `reasoning`. Do not treat a case or example as general proof by default. Record whether evidence is direct, indirect, anecdotal, or externally cited.

For every high-importance claim, ask:

1. Is this explicit or inferred?
2. What exact source units state and support it?
3. Does the evidence establish description, association, mechanism, or causation?
4. What limitation travels with the claim?
5. Does another chapter revise or contradict it?
