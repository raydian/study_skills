# Annotation schema

Annotations explain Source without changing it. They are versioned and revisable.

```yaml
schema_version: 1
annotations:
  - id: ann-ch03-021
    target_refs: [ch03-p028, ch03-p029]
    annotation_type: claim
    attribution: author_claim
    body: "__FAITHFUL_RESTATEMENT__"
    source_refs:
      - ref: ch03-p028
        pages: ["076"]
        relation: states
    concepts: [coordination-cost]
    related_units: [ku-claim-0042]
    confidence: 0.95
    revision: 1
    supersedes: null
    change_reason: initial
```

## Annotation types

`concept`, `definition`, `claim`, `argument`, `evidence`, `case`, `example`, `method`, `framework`, `rule`, `assumption`, `limitation`, `counterargument`, `question`, `transition`, `reference`, `relation`, `ai-explanation`, `ai-inference`, `critical-note`, `terminology`, `uncertainty`.

## Attribution discipline

- A faithful simplification is `ai_explanation`, not `author_claim`.
- A plausible consequence not stated by the author is `ai_inference`.
- A judgment about evidence quality is `critical_analysis`.
- A view quoted before rejection is `quoted_view`.
- A story is `case` unless the author explicitly uses it as evidence, in which case record both roles without collapsing them.

`annotated.md` mirrors important annotations for human inspection, while `annotations.yaml` is authoritative for structured semantics.
