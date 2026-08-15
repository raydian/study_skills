# deep-book-reading design

## Goal

Build a durable Book → Source → Human Reading → AI Semantic Corpus → Knowledge → Agent Skills pipeline. The package serves human readers, downstream AI retrieval, and reusable agent behavior without collapsing evidence and interpretation into one text.

## Architecture

The design separates four layers:

1. **Source** — normalized but semantically untouched evidence with stable locators. It becomes immutable when sealed.
2. **Human Reading** — narrative, publishable “guided reading,” with material claim IDs and source references.
3. **Annotation** — revisable AI semantic interpretation with explicit attribution and revision history.
4. **Knowledge/Skills** — typed, source-backed knowledge units; cross-chapter models; selectively generated Agent Skills.

Three ledgers govern the process: the Book Manifest defines the object received, the Reading Ledger proves what was read, and the Evidence Ledger connects claims to source units.

## B-plan chapter publishing

Every chapter has exactly one main reading. A recorded density score controls topic splitting: below 60, no topic articles; 60–74, two; 75–89, three; 90–100, four. Density measures independent knowledge/argument clusters and applications, not page count alone. Topic articles must have distinct questions and non-overlapping primary source ranges.

## Processing model

PASS 0 surveys and validates intake. PASS 1 recovers structure. PASS 2 performs per-chapter analytical reading and creates chapter packages. PASS 3 builds cross-chapter synthesis and concept evolution. PASS 4 adds critical reading. PASS 5 evaluates and generates reusable Skills. Each pass has entry/exit gates and writes resumable state.

## Integrity model

Source normalization happens in a staging state. Once locator coverage and sample comparison pass, the source is sealed and hashed. Corrections after sealing create a new source version and a correction record; annotations remain revisable through `revision`, `supersedes`, and `change_reason`.

Traceability flows from all derived claims to one or more stable source IDs. Relations may be direct (`supports`, `defines`, `illustrates`) or derived (`synthesizes`, `criticizes`), but derived relations must name their attribution class.

## Validation model

Deterministic tests validate structure and required fields. Semantic gates validate fidelity through sampled source comparison, evidence sufficiency, attribution review, contradiction review, and reading-claim traceability. No single coverage percentage substitutes for zero blocking gaps.

## Extension rules

- Add a profile only when a book family changes the reading object or evidence standard.
- Add a knowledge type only when none of the 12 canonical types can express it without loss.
- Extend schemas compatibly and bump `schema_version` for breaking changes.
- Keep detailed rules in direct references from `SKILL.md`; avoid nested reference chains.
- Keep generated Skills separate from the meta-skill and include `provenance.yaml` plus scenario tests.

## Non-goals

The Skill does not bypass copyright, guarantee perfect OCR, replace domain experts for high-stakes interpretation, or force all books to produce Agent Skills. It also does not prescribe one extraction tool; source format and available tools determine ingestion.
