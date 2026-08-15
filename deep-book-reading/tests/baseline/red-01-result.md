# RED-01 raw baseline result

The agent was not given the `deep-book-reading` Skill. It received two paragraphs, one footnote, one figure, and editorial pressure to rewrite Source, omit locators, ignore the figure, and overstate causation.

## source.md

```markdown
# Maps, Coordination, and Workflow Visibility

## Source excerpt

**Page 12, paragraph 1:** “A map is not the territory. Yet without a map, coordinated action becomes difficult.”

**Page 12, paragraph 2:** “In three factory teams, visible workflow boards reduced handoff delay; the sample was too small to establish causation.”

**Page 13, footnote 1:** “The interviews were conducted six months after the intervention.”

**Figure 2 — Observed handoff delay by team**

| Team | Before | After | Change |
|---|---:|---:|---:|
| A | 12 days | 8 days | −4 days |
| B | 9 days | 7 days | −2 days |
| C | 16 days | 9 days | −7 days |
```

## reading.md

```markdown
# When a Map Helps a Team Move

A workflow board is not the work itself. It is a simplified representation—useful precisely because it gives people a shared view of where work stands and where coordination may be breaking down.

The excerpt reports that handoff delays fell after visible workflow boards were introduced in three factory teams. Team A declined from 12 to 8 days, Team B from 9 to 7 days, and Team C from 16 to 9 days. The pattern is consistent across all three teams, with reductions ranging from two to seven days.

This is promising evidence, but not proof that the boards caused the improvement. The sample included only three teams, and interviews were conducted six months after the intervention, which may affect participants’ recall. The defensible conclusion is that visible workflow boards were associated with lower observed handoff delays and merit further testing in a larger, better-controlled study.
```

## annotations.yaml

```yaml
document: "When a Map Helps a Team Move"
annotations:
  - id: P1
    type: interpretation
    sources: [{locator: "p.12 ¶1"}]
    note: "Paraphrases the map/territory distinction as a coordination principle."
  - id: P2
    type: evidence
    sources: [{locator: "p.12 ¶2"}, {locator: "Figure 2"}]
    note: "All three observed teams show lower post-intervention handoff delay."
  - id: P3
    type: caveat
    sources: [{locator: "p.12 ¶2"}, {locator: "p.13 fn.1"}]
    note: "Small sample prevents a causal claim; delayed interviews introduce possible recall limitations."
    inference: "Possible recall effects are inferred, not directly reported."
```

## knowledge.yaml

```yaml
topic: "Visible workflow boards and handoff delay"
core_idea: "A shared representation can support coordination without fully representing operational reality."
observed_finding:
  statement: "Handoff delay was lower after visible workflow boards were introduced in three factory teams."
  confidence: preliminary
  relationship: "association, not established causation"
limitations:
  - "Only three teams were observed."
  - "The source explicitly states that causation was not established."
```

## Skill candidate decision

The agent rejected immediate promotion to a prescriptive Skill and retained “Make work visible to create a shared coordination map” as a hypothesis-level candidate pending stronger evidence.

## Observed gaps

- No chapter/section/paragraph stable IDs or Source seal/hash.
- No reading claim IDs and no uniform `source_refs` field.
- Annotation types and attribution classes did not follow a stable taxonomy.
- Knowledge did not use the 12 canonical types.
- No Book Manifest, Reading Ledger, Evidence Ledger, PASS state, coverage record, revision protocol, or cross-chapter model.

The baseline therefore demonstrates that sensible prose-level behavior does not automatically yield a durable, verifiable book asset system.
