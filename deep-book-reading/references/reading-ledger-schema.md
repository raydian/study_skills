# Reading Ledger schema

The Reading Ledger proves what was read; it is not a narrative status update.

```yaml
schema_version: 1
book_id: "__BOOK_SLUG__"
passes:
  pass_0: complete
  pass_1: in_progress
  pass_2: pending
  pass_3: pending
  pass_4: pending
  pass_5: pending
coverage:
  chapters: {reviewed: 0, total: 0}
  sections: {reviewed: 0, total: 0}
  pages: {reviewed: 0, total: 0}
  paragraphs: {reviewed: 0, total: 0}
  figures: {reviewed: 0, total: 0}
  tables: {reviewed: 0, total: 0}
  equations: {reviewed: 0, total: 0}
  code_blocks: {reviewed: 0, total: 0}
  footnotes: {reviewed: 0, total: 0}
  sidebars: {reviewed: 0, total: 0}
  appendices: {reviewed: 0, total: 0}
units:
  - id: "ch01-s01"
    status: complete
    pages: ["001", "002"]
    resources_reviewed: ["ch01-fig001"]
    knowledge_units: ["ku-concept-0001"]
    unresolved: []
checkpoint:
  updated_at: "__ISO_8601__"
  next_unit: "ch01-s02"
  context_note: "__MINIMAL_RESUME_CONTEXT__"
gaps:
  - id: gap-001
    unit: "ch04-fig003"
    class: blocking
    reason: unreadable_scan
    resolution: manual_review
```

Use `not_applicable` only when the manifest total for that resource kind is zero. A percentage can be 100% while a known missing page remains; therefore finalization requires both required coverage and zero blocking gaps.
