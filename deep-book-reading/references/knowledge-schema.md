# Knowledge unit schema

Use exactly these canonical types unless the schema version is deliberately extended:

`Concept`, `Definition`, `Claim`, `Principle`, `Framework`, `Method`, `Pattern`, `Rule`, `Evidence`, `Case`, `Counterexample`, `Limitation`.

```yaml
schema_version: 1
knowledge_units:
  - id: ku-method-0012
    type: Method
    name: "__NAME__"
    statement: "__NORMALIZED_BUT_FAITHFUL_FORM__"
    human_explanation: "__PLAIN_LANGUAGE__"
    attribution: author_claim
    source_refs:
      - ref: ch05-p044
        pages: ["121"]
        relation: states
    evidence_refs: [ev-0104]
    prerequisites: [ku-concept-0008]
    inputs: ["__INPUT__"]
    outputs: ["__OUTPUT__"]
    steps: ["__STEP__"]
    boundary_conditions: ["__BOUNDARY__"]
    related_units: [ku-principle-0007]
    confidence: 0.88
```

Type distinctions:

- Concept: named idea or category.
- Definition: meaning assigned to a term.
- Claim: proposition asserted as true.
- Principle: general explanatory or normative proposition.
- Framework: organized dimensions/parts for understanding or decision-making.
- Method: ordered procedure toward an outcome.
- Pattern: recurring configuration with context and consequence.
- Rule: conditional directive or decision criterion.
- Evidence: material offered to support or challenge a claim.
- Case: situated instance or narrative.
- Counterexample: instance that challenges generality.
- Limitation: boundary, uncertainty, or failure condition.

Do not duplicate one idea across types merely to fill categories. Link units instead. Every method, framework, or rule must retain the assumptions and limitations that qualify it.
