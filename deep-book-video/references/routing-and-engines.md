# Routing and engines

## Architecture

Use this sequence:

```text
Book Profile
  × Content Unit Router
  × Depth Engine
  × Narrative Mode
  × Global Video Thesis
  → page-level reasoning arc
```

The Book Profile supplies priors. The Content Unit Router decides how a specific unit must be explained. The Depth Engine supplies the reasoning operation. The Narrative Mode orders viewer experience. The Global Video Thesis filters and binds the whole video.

## Book Profile

Choose one primary type and zero to three secondary types. Types include social thought, psychology/behavior, philosophy, history, biography, natural science, economics/finance, business/management, practical method, technology/professional, textbook/mathematics/academic, fiction, poetry/drama/classics, religion/intellectual classics, visual arts/comics/picture books, and essay/anthology/short-story collection.

Also score `narrative`, `conceptual`, `causal`, `methodological`, `argumentative`, `evidential`, `derivational`, `emotional`, `formal`, and `visual` from 0–5. Record chronology, core reader value, evidence forms, interpretive plurality, and spoiler sensitivity. These dimensions are more important than the shelf label.

## Content Unit Router

Give every selected knowledge unit one primary role and optional secondary roles:

| Unit role | Core question |
|---|---|
| phenomenon/question | What needs explaining? |
| definition/concept | What does this term mean here? |
| argument/claim | What is asserted, and on what assumptions? |
| mechanism/system | What parts interact to produce the result? |
| cause/contingency | Why did this occur, and what alternatives were possible? |
| evidence/case | What supports the claim, and how strongly? |
| chronology/turning point | What changed the trajectory? |
| method/rule/decision | What should be done, when, and with what trade-off? |
| proof/derivation | How does the conclusion follow from definitions and assumptions? |
| character/choice | What did the person choose under constraint? |
| scene/form/symbol | How does language, form, image, or silence create meaning? |
| interpretation/tradition | Which reading is being used, and what alternatives exist? |
| visual object | What information exists in composition, sequence, or text-image relation? |
| counterexample/limitation | Where does the claim weaken, fail, or require qualification? |
| cluster/constellation | How do independent works answer a shared question differently? |

Record prerequisites and do not show a conclusion before the viewer has the concepts needed to understand it.

## Depth Engine

| Engine ID | Reasoning pattern | Best fit |
|---|---|---|
| `system-mechanism` | parts → interactions → feedback → outcome → boundary | science, social systems, technology |
| `causal-contingency` | conditions → trigger → chain → turning point → alternatives | history, biography, economics |
| `argument-assumption` | question → claim → reasons → evidence → assumption → rival view | philosophy, social thought, criticism |
| `evidence-calibration` | claim → evidence type → directness → strength → limitation | academic, psychology, science |
| `procedure-tradeoff` | problem → prerequisites → steps → decision points → failure modes | methods, business, technology |
| `derivation-proof` | problem → definition → assumptions → derivation → proof intuition → boundary | mathematics, textbooks, technical theory |
| `character-choice` | situation → desire → constraint → choice → consequence → change | biography, fiction, drama |
| `close-reading-form` | passage/scene → formal feature → pattern → interpretation → alternatives | literature, poetry, classics |
| `interpretive-tradition` | text → historical context → school reading → rival reading → modern use | religion, philosophy, classics |
| `visual-analysis` | observe → composition → relation → symbol → context → interpretation | art, comics, picture books |
| `comparison-boundary` | common question → model A/B → discriminating case → scope | mixed arguments and rival theories |
| `cluster-constellation` | shared question → thematic clusters → contrast → network synthesis | essays, anthologies, short collections |

Use at most one primary and one supporting engine per unit. Do not add universal philosophical elevation; depth must come from the native evidence and reasoning of the unit.

## Narrative Mode

| Mode | Viewer experience |
|---|---|
| `question_to_model` | puzzling phenomenon → inadequate intuition → model → test → limit |
| `causal_investigation` | outcome → candidate causes → causal chain → contingency → judgment |
| `turning_points` | initial state → constraints → choices → irreversible turns → legacy |
| `mechanism_discovery` | observable effect → hidden mechanism → prediction → exception |
| `debate_dialectic` | contested question → positions → evidence → decisive difference → bounded verdict |
| `problem_to_method` | costly problem → failed approach → method → worked case → boundary |
| `guided_derivation` | question → definitions → steps → intuition → result → applicability |
| `scene_to_meaning` | scene/passage → detail → formal pattern → interpretation → ambiguity |
| `thematic_constellation` | shared question → clustered works → contrasts → emergent whole |
| `case_led_transfer` | concrete case → mechanism → generalization → transfer conditions |
| `visual_tour` | looking task → visual evidence → relation → cultural context → interpretation |

Choose one dominant mode for coherence. Use a secondary mode only for a clearly bounded segment and record the transition.

## Global Video Thesis

The Global Video Thesis is not the book's entire thesis. It is the one claim this video can responsibly establish within its duration.

Required fields:

- `statement`: one contestable sentence;
- `viewer_shift`: what the viewer will see differently afterward;
- `scope`: domain, population, period, or condition;
- `counter_thesis`: strongest material qualification or rival claim;
- `exclusion_rule`: what interesting content will be left out;
- `proof_obligations`: evidence and reasoning needed to earn the conclusion.

Score candidates 0–5 on thesis necessity, evidence strength, explanatory leverage, prerequisite cost, distinctiveness, and static visualizability. Evidence and thesis necessity are veto dimensions; visual appeal is never a substitute.

## Page relation vocabulary

Every page records one `thesis_relation`: `opens`, `defines`, `advances`, `evidences`, `explains`, `contrasts`, `qualifies`, `applies`, or `synthesizes`. Two adjacent pages should not repeat the same claim in different wording.
