# Quality gates

## Gate A — Input Integrity

- Source identity, edition, authorization, completeness, and locator scheme are known.
- Book-level synthesis and critical reading are available.
- High-impact knowledge units have stable `source_refs` and evidence records.
- Missing pages, OCR uncertainty, unresolved contradictions, and visual-resource gaps are explicit.

Failure is blocking when the video would need to invent, overstate, or misattribute a central claim.

## Gate B — Profile and Routing

- Book Profile describes knowledge structure, not only shelf genre.
- Every selected unit has a primary role, Depth Engine, prerequisites, evidence burden, and limitation.
- Mixed books use unit-level routing.
- Interpretive plurality and spoiler policy are honored.

## Gate C — Global Thesis

- One Global Video Thesis is contestable, source-supported, scoped, and suitable for the target duration.
- Viewer shift, counter-thesis, exclusion rule, and proof obligations are recorded.
- Every selected unit is necessary to open, advance, evidence, explain, contrast, qualify, apply, or synthesize the thesis.
- The ending is earned by preceding pages and does not add generic philosophical uplift.

## Gate D — Narrative

- One dominant Narrative Mode organizes the viewer experience.
- Prerequisite concepts precede dependent claims.
- Causal, chronological, procedural, and derivational order are preserved when applicable.
- Each page performs one cognitive move; adjacent pages do not paraphrase each other.
- The cumulative page durations fit the requested video length.

## Evidence Gate

- Every material page claim has `knowledge_unit_ids`, `source_refs`, attribution, evidence strength, directness, and limitations.
- Exact quotations match the sealed source and locator.
- Author view, quoted view, AI explanation/inference, external context, and critical analysis remain distinguishable.
- Case and anecdote are not generalized as proof.
- Association is not narrated as causation without causal support.
- AI-generated images, prompts, and reconstructions are never evidence.
- Every high-impact and low-confidence claim passes source-context sampling.

Any unsupported, misattributed, materially overstated, or underqualified high-impact claim is blocking.

## Gate F — Page Script

- Every page includes all canonical fields from the schema.
- Subtitle is the cognitive anchor rather than the full transcript.
- Voiceover is speakable, paced, and faithful to the page sources.
- Page purpose and thesis relation are specific.
- Duration supports both listening and reading.
- Title, bridges, and ending still have source or editorial provenance.

## Visual Legibility Gate

- Background is full-screen and static; transition is `hard_cut`.
- The image prompt is detailed, page-specific, and consistent with the visual bible.
- A low-detail text-safe zone is reserved before generation.
- At 1920×1080, normal subtitle size is at least 64 px; weight is at least 700; local contrast target is at least 7:1.
- Subtitle uses 1–3 syntactically meaningful lines and respects line-length guidance.
- A scrim or solid subtitle box stabilizes contrast.
- No prompt asks the image model to render the subtitle, exact quotation, equation, chart labels, or data values.
- Negative prompt forbids accidental text, logos, watermarks, frames, anatomy defects, and safe-zone clutter.
- Actual images are inspected at master and phone-preview sizes.

## Gate H — Static Rhythm and Continuity

- Page changes correspond to reasoning changes.
- Scale, viewpoint, visual function, light, and scene type vary enough to prevent monotony.
- Palette, motif, era/culture, and recurring characters/objects remain coherent.
- No pan, zoom, parallax, animated highlight, motion graphic, or simulated camera movement appears.
- Dense mechanisms or proofs are split into successive static states rather than compressed into one overloaded image.

## Gate I — Ethical and Production Safety

- Copyright, quotation length, book-cover use, and source authorization are respected.
- Real people, trauma, violence, religion, culture, and identity are depicted without fabricated certainty or sensationalism.
- Reconstruction, metaphor, and editorial interpretation are labeled in production metadata where a viewer could mistake them for documentation.
- Generated images contain no accidental brand marks, signatures, private information, or misleading documentary cues.

## Gate J — Remotion Production

- `engine` is `remotion`; one registered composition owns dimensions, fps, and the estimated silent timeline.
- Before any project-local installation, the enclosing `video/` root is searched for a compatible shared `node_modules`.
- The project `node_modules` is a verified symbolic link whose resolved target stays inside that `video/` root; a full project-local dependency copy is blocking.
- Shared `remotion`, `react`, and `react-dom` packages resolve from the project and satisfy its declared versions; incompatible shared dependencies are not silently modified.
- Page frame ranges are positive, contiguous, non-overlapping, and match the composition's exclusive final frame.
- Every page has an immutable `P###` ID, a concise page name, and a unique `studio_sequence_name` equal to `P###｜page name`.
- Pages are assembled as adjacent, explicit authored JSX `Series.Sequence` blocks with literal `name` props, no `.map()` generation, negative offset, transition overlap, or hidden duration drift.
- Each page image exists under Remotion `public/` and is loaded with `staticFile()`.
- Each page remains pixel-static across its first, middle, and last visible frames.
- No `useCurrentFrame()`, `interpolate()`, CSS transition, CSS animation, animated component, pan, zoom, or parallax changes page pixels.
- Local CJK fonts load before measurement; actual subtitle lines fit without dropping below the minimum size.
- Before Studio approval there is no audio directory, audio asset, `<Audio>` component, `@remotion/media` dependency, TTS call, codec, output path, or render command.
- The complete silent composition is inspected in Remotion Studio; every page appears as a separately selectable timeline item showing its correct number and name, order and duration match `timeline.json`, and state remains `pending` until explicit user confirmation.
- QA findings and revision requests cite the stable page ID, such as `[P014]`, so the script, image, timeline item, JSX block, and later voiceover mark can be located directly.
- `voiceover_handoff.status` remains blocked while Studio confirmation is pending.
- The approved handoff uses `video-voiceover`, `--sync-remotion`, measured audio timing, `render_after_voiceover: false`, and `preview_after_voiceover: true`.
- After voiceover synchronization, Studio is reopened for timing review; no still or video is rendered.

## Completion rule

The silent visual stage completes only after all applicable gates, zero blocking issues, no dangling `source_refs`, no missing page fields, and explicit Remotion Studio confirmation. The voiceover stage completes only after `video-voiceover` synchronization and a second Studio review. This skill never renders; rendering requires a separate explicit user request. Record accepted non-blocking risks and the rationale in `qa-report.md`.
