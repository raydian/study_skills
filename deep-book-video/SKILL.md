---
name: deep-book-video
description: Use when turning a source-backed deep-book knowledge package into a silent Remotion Studio book-video project with full-screen AI image backgrounds, large high-contrast subtitles, source-traceable page scripts, and a gated handoff to the video-voiceover skill after visual confirmation.
---

# Deep Book Video

## Overview

Transform a deep-book knowledge base into a source-faithful static visual project for Remotion Studio. This skill finishes at a silent Studio-confirmed composition and a compatible voiceover handoff; it does not synthesize audio or render a video file.

## Non-negotiable contract

1. Require a complete, source-backed knowledge package or run a blocking input audit. Read [input-contract.md](references/input-contract.md).
2. Build one Book Profile, then classify every selected unit with the Content Unit Router. Never let the book's shelf category dictate every unit's treatment.
3. Select a Depth Engine and Narrative Mode from [routing-and-engines.md](references/routing-and-engines.md); hybrids are explicit, not accidental.
4. Write one Global Video Thesis before selecting pages. Every page must open, advance, evidence, qualify, contrast, apply, or synthesize it.
5. Keep Source, author claim, quoted view, AI inference, critical analysis, subtitle, voiceover, and AI image distinct. Every material page claim requires `source_refs`, attribution, evidence quality, and limitations.
6. Treat the generated background as illustration. Never use an AI-generated object, diagram, quotation, number, costume, place, or face as factual evidence.
7. Use Remotion as the only assembly, timing, and Studio-preview layer. Read [remotion-production.md](references/remotion-production.md) before creating or editing the Remotion project.
8. Before any dependency installation, search inside the intended `video/` root for a compatible shared `node_modules`. Reuse it through a symbolic link; never keep a full project-local copy when a valid shared tree exists. Read [remotion-project-setup.md](references/remotion-project-setup.md).
9. Give every page a stable `P###` ID, concise name, and exact `studio_sequence_name`. Author one literal, named `Series.Sequence` per page as explicit authored JSX; never generate Studio timeline pages with `.map()`.
10. Use full-screen static images only. Do not specify pan, zoom, parallax, animated text, animated highlights, simulated camera movement, or motion graphics. The only transition is `hard_cut`.
11. Make subtitles large, sparse, high contrast, and independently readable. Do not paste the full voiceover into the subtitle field.
12. Keep the initial Remotion project silent. Do not create audio assets, add `<Audio>`, or invoke TTS before explicit Studio confirmation.
13. Give every page all required fields in [video-script-schema.md](references/video-script-schema.md), including a detailed `image_prompt`, subtitle, future voiceover text, duration estimate, page purpose, knowledge sources, visual composition, readability constraints, and exact Remotion frame range.
14. Stop at the Studio Confirmation Gate and wait for explicit user approval. Only then hand off to `video-voiceover` with `--sync-remotion`.
15. **MUST NOT render** a still image, preview MP4, or final video in this skill. After voiceover, return to Remotion Studio for synchronization review; still do not render.
16. Do not finalize with any blocking quality-gate failure.

## Required references

Before drafting, read:

- [input-contract.md](references/input-contract.md) for accepted knowledge bases and provenance.
- [routing-and-engines.md](references/routing-and-engines.md) for Book Profile × unit routing × Depth Engine × Narrative Mode.
- [static-visual-principles.md](references/static-visual-principles.md) for the limitations of this format and the fixed remedies.
- [video-script-schema.md](references/video-script-schema.md) for the output contract.
- [remotion-project-setup.md](references/remotion-project-setup.md) for shared `node_modules`, symbolic-link validation, stable page IDs, and explicit named Studio sequences.
- [remotion-production.md](references/remotion-production.md) for the silent composition, frame math, Studio Confirmation Gate, and `video-voiceover` handoff.
- [quality-gates.md](references/quality-gates.md) for completion criteria.

## Workflow

### 0 — Audit input

Inventory manifest, book map, core thesis, argument map, critical reading, knowledge units, evidence ledger, locators, source authorization, visual resources, unresolved gaps, and spoiler sensitivity. Produce `input-audit.md`. Stop final scripting if a high-impact claim lacks stable provenance.

### 1 — Profile the book

Create `book-profile.json` with primary and secondary types, knowledge-structure scores, chronology, evidence forms, core reader value, interpretive plurality, visual dependence, and spoiler policy. A profile sets priors only.

### 2 — Route content units

Create `routes.json`. For each candidate unit record its function, reasoning demand, evidence burden, selected Depth Engine, possible visual role, prerequisites, limitations, and relationship to other units. Route mixed books unit by unit.

### 3 — Establish the Global Video Thesis

Write one contestable sentence, the viewer's intended cognitive shift, scope, counter-thesis, and exclusion rule. Score candidate units by thesis necessity, evidence strength, explanatory leverage, and visualizability. Do not select a unit only because it is famous or easy to illustrate.

### 4 — Choose the Narrative Mode and arc

Choose the dominant Narrative Mode from the thesis and selected routes. Build an arc with explicit page functions. Preserve necessary prerequisites and causal order; use chronology only when time explains the result. For collections, cluster around a question rather than inventing false linearity.

### 5 — Write the page script

Use `video-script.json` as the canonical script. One page equals one cognitive beat. Write the claim and source record first, then voiceover, then compress the current anchor into subtitle lines. Set duration from spoken length and reading load; split overloaded pages.

Every page must include:

- stable `page_id`, concise `page_name`, exact `studio_sequence_name`, sequence, page type, purpose, and thesis relation;
- content route, explicit page claim, knowledge-unit IDs, `source_refs`, attribution, evidence quality, and limitations;
- subtitle text plus typography and contrast rules;
- voiceover text plus delivery direction;
- duration;
- exact Remotion `start_frame`, `duration_in_frames`, and exclusive end frame;
- Remotion-relative image path; no audio path before confirmation;
- detailed image-generation description;
- composition, safe-text zone, crop safety, and readability controls;
- `hard_cut` transition.

### 6 — Direct static visuals

Create a global visual bible before page prompts. Keep a controlled palette, motif system, era/culture rules, character continuity, and forbidden elements. Each page prompt must specify subject, setting, action/state, era/culture, art direction, palette, light, lens/camera, composition, symbolism, continuity, safe text area, realism constraints, negative prompt, and one assembled generation prompt.

Reserve a calm text-safe zone in the generated image. Add all real subtitles later in layout; prompts must prohibit generated letters, numbers, book titles, logos, and watermarks. For quantitative or technical claims, use the background metaphorically and keep exact values in sourced subtitle/voiceover, never in AI-rendered charts.

### 7 — Assemble with Remotion

Resolve the enclosing `video/` root before creating the project. Search it for a compatible shared `node_modules`, create a symbolic link from the project, and record the resolved dependency target. If none exists, create the shared dependency tree once under that root and link the project to it. Never silently replace an existing directory or incompatible link.

Create or reuse a Remotion project. Put generated images and local CJK fonts under `public/`; reference them with `staticFile()`. Register one `DeepBookVideo` composition. Assemble pages as contiguous, explicitly authored `Series.Sequence` blocks with no overlap or offset. Each block must carry the literal `studio_sequence_name` in its `name` prop and contain one full-screen static image plus one static subtitle panel. Do not generate page sequences with `.map()`. Do not install or use `@remotion/media`, add `<Audio>`, create `public/audio`, or invoke TTS at this stage. Do not use `useCurrentFrame()`, `interpolate()`, CSS transitions, CSS animations, or animated components in page visuals.

Compute frame boundaries from cumulative time at the declared fps. Make `end_frame_exclusive = start_frame + duration_in_frames`; make the composition duration equal the final exclusive end frame. Read [remotion-production.md](references/remotion-production.md) for the required component and asset layout.

### 8 — Validate the silent project

Run all pre-confirmation gates in [quality-gates.md](references/quality-gates.md). Sample every high-impact and low-confidence claim against its source context. Inspect the generated source images directly and verify the complete silent composition in Studio.

Run the structural checks before opening Studio:

```bash
python3 scripts/validate_video_script.py /absolute/path/to/video-script.json
python3 scripts/validate_remotion_project.py /absolute/path/to/remotion --video-root /absolute/path/to/video
python3 -m unittest discover -s tests -p 'test_*.py'
```

The validators check observable script structure, the shared dependency link, explicit named timeline pages, the audio prohibition, Studio gate, and no-render policy. Human review remains mandatory for thesis coherence, fidelity, aesthetics, pacing, and image accuracy.

### 9 — Studio Confirmation Gate

Start `npx remotion studio --no-open`, open the printed Studio URL, and review the entire silent composition. Confirm that every page is a distinct timeline item displaying its `P###｜page name`, and that clicking it seeks to the intended page with the correct duration. Check every subtitle, crop, hard cut, estimated hold time, typography, and source-driven visual choice. Do not use `npx remotion still` or `npx remotion render`.

Set `remotion.studio_confirmation: pending` and `voiceover_handoff.status: blocked_until_studio_confirmed` until the user explicitly confirms the Studio result. Stop and ask for confirmation. Do not infer approval from a successful build or Studio launch.

### 10 — Hand off to video-voiceover

After explicit approval, set `remotion.studio_confirmation: approved` and `voiceover_handoff.status: ready`. Produce `voiceover-script.json` in the JSON-marks format required by `video-voiceover`: bind every mark to its `page_id`, use the page voiceover text as `text`, preserve the large page anchor as `subtitle`, and carry delivery direction as `tone`.

Invoke `video-voiceover` with the Remotion project directory, the generated script, and `--sync-remotion`. For book types outside its established subject profiles, require an explicit supported subject or speaker choice; do not invent a speaker ID. The handoff must state `render_after_voiceover: false` and `preview_after_voiceover: true`.

After real audio durations update the timeline, reopen Remotion Studio and review synchronization. **MUST NOT render** after this second review unless the user starts a separate task explicitly requesting rendering.

## Output package

```text
video-slug/
├── input-audit.md
├── book-profile.json
├── routes.json
├── video-brief.json
├── video-script.json
├── source-map.json
├── qa-report.md
└── remotion/
    ├── package.json
    ├── node_modules -> <shared node_modules inside video root>
    ├── dependency-link.json
    ├── voiceover-script.json
    ├── voiceover-handoff.json
    ├── src/
    │   ├── Root.tsx
    │   ├── BookVideo.tsx
    │   ├── timeline.json
    │   ├── components/StaticBookPage.tsx
    │   └── data/
    │       ├── video-script.json
    │       └── subtitles.ts
    ├── public/
    │   ├── images/p001.png
    │   └── fonts/
    └── (no rendered output)
```

`video-script.json` is canonical. A human-readable table or production sheet may be derived from it but must not replace or diverge from it.

## Quick routing reference

| Content need | Typical Depth Engine | Typical Narrative Mode |
|---|---|---|
| Explain a world model | system-mechanism | question-to-model |
| Explain why an event happened | causal-contingency | causal-investigation |
| Follow a person through choices | character-choice | turning-points |
| Teach a method | procedure-tradeoff | problem-to-method |
| Explain proof or derivation | derivation-proof | guided-derivation |
| Interpret literature or classics | close-reading-form | scene-to-meaning |
| Compare rival explanations | argument-assumption | debate-dialectic |
| Connect independent essays/stories | cluster-constellation | thematic-constellation |

## Common failures

| Failure | Correction |
|---|---|
| Chapter-by-chapter summary | Re-select units through the Global Video Thesis. |
| One engine for the whole book | Re-route each content unit. |
| Decorative image unrelated to reasoning | Give the image a page-specific visual function and thesis relation. |
| AI image used as historical/scientific proof | Cite the source; label the image as reconstruction or metaphor. |
| Full voiceover copied into subtitle | Reduce to one claim, contrast, question, or conclusion in 1–3 lines. |
| Busy full-screen art behind text | Reserve a low-detail safe zone and add a solid/semi-opaque scrim. |
| Exact chart requested from image generation | Keep exact data in sourced text or a deterministic overlay. |
| Visual sameness | Vary scale, viewpoint, scene function, and light while preserving the visual bible. |
| Philosophical uplift added to every ending | End at the depth native to this book and thesis. |
| Smooth but unsupported narration | Downgrade, qualify, cite, or remove the claim. |
| Seconds converted to frames independently | Derive all page boundaries from cumulative time and verify the final exclusive frame. |
| Every video project installs its own dependencies | Search the `video/` root first, verify compatibility, and link the project to one shared `node_modules`. |
| Existing project modules are overwritten to force reuse | Stop, report the conflict, and resolve compatibility before changing the link or shared tree. |
| Studio timeline shows anonymous or aggregated pages | Give every page `P###｜page name` and author each named `Series.Sequence` explicitly, without `.map()`. |
| A reported problem cannot be located quickly | Carry the stable `P###` ID through script, image, timeline, JSX, voiceover marks, and QA notes. |
| CSS animation added “just for polish” | Remove it; this format requires identical pixels throughout each page interval. |
| Audio created while building visuals | Remove it; wait for explicit Studio confirmation, then use `video-voiceover`. |
| Studio launched and treated as approval | Stop and obtain explicit user confirmation before voiceover. |
| A still or MP4 is rendered for QA | Use Remotion Studio only; rendering is outside this skill. |
| Voiceover overwrites the large subtitle with transcript text | Keep page subtitle as the cognitive anchor; pass full narration only in the mark's `text`. |
