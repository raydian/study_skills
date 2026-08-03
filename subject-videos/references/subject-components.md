# Subject Components

All components must be Remotion-controlled. Do not let libraries run their own timeline, autoplay, user interaction playback, animation loop, or physics clock. Pass `frame`, `progress`, `durationFrames`, `data`, and `theme` as props.

## 数学

Allowed tools:

- KaTeX: formulas and step-by-step derivations.
- JSXGraph: geometry, coordinate systems, function graphs.
- ECharts: statistics, function comparison, data charts.

Patterns:

- FormulaBoard: reveal derivation by frame range.
- GraphScene: compute visible domain/range from `progress`.
- GeometryProof: show givens, auxiliary lines, and conclusion in ordered steps.

## 语文

Recommended tools:

- SVG/React diagrams for paragraph structure, reading paths, character relationships, plot timelines, emotion curves, imagery networks, and answer templates.
- Mermaid for argument structure, narrative structure, comparison maps, and text interpretation flows when it stays readable.
- ECharts only for simple emotion curves, reading-evidence distributions, or comparison charts.

Patterns:

- TextSpotlight: reveal a selected sentence or short passage line by line, with keyword underline and margin notes.
- CloseReadingBoard: show “写了什么 -> 怎么写 -> 为什么这样写 -> 表达什么 -> 怎么答”.
- GenreRouteMap: choose the explanation path by genre instead of using one universal script structure.
- EmotionCurve: trace emotional change across paragraphs, stanzas, or plot stages.
- ImageryWeb: connect images such as moon, willow, wild goose, rain, wine, boat, flower, wind, and their emotional meanings.
- CharacterPlotMap: reveal characters, conflicts, plot stages, and theme links.
- ArgumentChain: reveal claim, evidence, reasoning, method, and conclusion.
- ClassicalSentenceBoard: split classical Chinese into key words, sentence pattern, adjusted word order, and fluent translation.
- AnswerBuilder: turn evidence and method into a scored answer step by step.

Chinese page layout patterns:

- ReadingFocusLayout: left or center shows the active quote/line in large readable type; side panel keeps a compact route such as emotional curve, structure path, or genre-reading steps.
- CloseReadingLayout: selected quote on one side, annotation/evidence/effect chain on the other; avoid full-page paragraphs.
- AnswerTransferLayout: full question, task parsing, evidence, one or more substantive reasoning paths, answer synthesis, and score check; weak-answer/strong-answer contrast may support the worked solution.
- ReviewLayout: return to the route map and light up completed steps instead of listing every detail again.

Timing behavior for reading components:

- visual state must be derived from the measured narration/subtitle timeline;
- during pauses between narration segments, hold the previous meaningful text or display a deliberate pause prompt;
- do not fall back to the first line, first subtitle, or a generic “overall impression” prompt during segment gaps;
- if a component uses an active segment index, choose the latest segment whose `start` is not greater than the current frame when the current frame is between segments.

Chinese structure routing:

- Use `chinese-video-structure.md` for the flexible seven-module teaching arc, article-specific scene decomposition, genre routes, evidence units, theme/core-idea placement, and real worked-example transfer.
- Do not infer one scene or page from one module or one node in a genre route.
- Use this file only to select the visual component that best expresses the current quote, evidence relation, structure, theme synthesis, or solution step.
- Keep the teacher voice professional, mature, knowledge-rich, and grounded in visible text evidence.

## 物理

Allowed tools:

- p5.js: schematic motion, vectors, waves.
- Matter.js: simple deterministic 2D mechanics.
- Three.js: 3D spatial scenes and fields.
- Rapier: physics simulation only when state is deterministic or precomputed by frame.

Patterns:

- MotionDiagram: position, velocity, acceleration derived from frame.
- ForceAnalysis: reveal object, forces, resultant, equation, conclusion.
- ExperimentScene: show apparatus, measurement, data, graph, conclusion.
- ModelTransition: transform a real scene into the selected object, process stages, assumptions, reference frame, and direction convention.
- QuantityBinding: bind every symbol, vector, sign, and unit to the object or process shown on screen.
- RepresentationBridge: keep one physical situation consistent across verbal, diagram, formula, vector, and graph representations.
- DifficultyConflict: show the plausible intuition, conflicting evidence, corrected model, and judgment cue.
- MisconceptionContrast: show the wrong path, failure evidence, correct path, and one-line prevention cue.
- MotherProblemBoard: reveal task parsing, model selection, diagram, law choice, equations, solution, and checks one semantic step at a time.
- SingleVariableVariant: change exactly one condition and highlight which model assumptions, equations, or conclusions remain valid.

Physics structure routing:

- Use `physics-video-structure.md` to select the concept/law, experiment/inquiry, calculation/method, or phenomenon/mechanism route.
- Keep components frame-driven and bind narration-led states to stable `stepId`/`visualCueId` values once audio exists.
- Treat the route stages as teaching purposes, not one-component-per-stage or fixed pages.

## 化学

Allowed tools:

- 3Dmol.js: molecular and crystal structures.
- Kekule.js: structural formulas and reaction structures.
- Mermaid: reaction classification, process, and experiment flow.
- ECharts: data, curves, comparison charts.

Patterns:

- MacroMicroSymbol: macro phenomenon, microscopic particles, symbolic equation.
- ReactionPath: reactants, conditions, electron/ion transfer, products.
- LabProcedure: apparatus, operation steps, observations, conclusion.

## 生物

Recommended tools:

- SVG/React diagrams for cells, organs, systems, and ecological flows.
- ECharts for experiment data and population/ecology curves.
- Three.js only for spatial structures when it adds learning value.

Patterns:

- StructureFunction: structure labels, function arrows, result.
- ProcessCycle: stage-by-stage frame-driven cycle.
- EvidenceChain: experiment setup, data, inference, conclusion.

## 地理

Allowed tools:

- Leaflet: map-based explanation.
- MapLibre: vector map scenes.
- OpenLayers: layered geographic data.
- deck.gl: spatial flows, point layers, arcs.
- Three.js: terrain, earth, atmosphere, or 3D process scenes.

Patterns:

- RegionMap: location, elements, spatial pattern.
- ProcessCrossSection: terrain/climate/water/urban mechanism.
- HumanLandSystem: resource, production, transport, management, impact.

## 历史

Allowed tools:

- vis-timeline: chronology and event relationships.
- Cytoscape.js: actors, institutions, alliances, causal networks.
- Mermaid: process, cause-effect, comparison diagrams.
- Leaflet: historical geography and routes.

Patterns:

- TimelineLecture: background, turning point, result, influence.
- CauseNetwork: multi-cause graph with weighted emphasis.
- InstitutionMechanism: how a system works in practice.

## Cross-Subject Rules

- Components must be readable at 1920x1080.
- Keep labels concise; put longer explanation in voiceover.
- Prefer progressive reveal over showing a full dense diagram at once.
- Use color consistently: neutral base, one accent for current focus, one warning color for common mistakes.
