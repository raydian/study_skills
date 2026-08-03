# Audio Voiceover And Subtitle Sync

Use this reference when the user asks to generate narration audio, TTS, dubbing, or a final video with voiceover.

## Required Order

1. Create or update the teaching script.
2. Create a speech marker file before TTS generation.
3. Generate narration from the marker file with exactly one marker segment per subtitle cue.
4. Measure every generated audio segment with `ffprobe`.
5. Concatenate segments and marked pauses into one final audio file.
6. Use measured durations to regenerate subtitle timings, scene durations, and `timeline.json`.
7. Bind measured cues to stable visual steps and drive Remotion frame states from the same timing data.
8. Add the final audio to Remotion with `<Audio src={staticFile("audio/voiceover.mp3")} />`.
9. Validate with typecheck, still frames, and `ffprobe` on the final video.

Do not rely on estimated reading speed once audio exists.
Do not leave scene animation checkpoints on old fixed-frame estimates once audio exists. Current-line highlights, current-card emphasis, answer-step reveals, and reading spotlights must follow the measured speech/subtitle span.

## Speech Marker File

Create a marker file such as:

```text
voiceover/voiceover_marks.json
```

Each segment should include:

- `id`: stable segment id, usually `<scene>-<index>`.
- `scene`: scene id.
- `text`: exact TTS text, already split to fit at most two rendered subtitle lines.
- `subtitle`: screen subtitle text; require it to be exactly identical to `text`.
- `tone`: teacher delivery note, such as `亲切开场`, `朗读明亮`, `设问推进`, `结论加重`.
- `speechRate`: integer speech-rate adjustment for TTS.
- `pauseAfterMs`: explicit pause after the segment.
- `visualCueId` or `stepId`: optional stable visual-state key. Reuse it across consecutive subtitle segments that explain the same board, graph, formula, or solution step.

Recommended segment size: one short clause, one recitation line, or one answer sub-step that renders in one or two lines. Prefer one line when the complete cue fits, but use actual layout measurement rather than character count as the final authority.

The marker `text` actually sent to TTS is the source of truth for audio content, subtitle content, and timing. Require `subtitle === text`; never summarize, shorten, omit, paraphrase, or rewrite the spoken wording. Add a validation that every final subtitle matches the corresponding marker by id, scene, and exact text.

## Verbatim Two-Line Segmentation

- Keep every bottom subtitle to at most two rendered lines at the final resolution, approved font size, and safe width. Prefer one line when the complete verbatim cue fits.
- Split long narration before TTS at punctuation, clause boundaries, formula transformations, question/answer turns, enumerated conditions, or reasoning steps.
- Preserve the complete spoken wording across the split cues; do not delete connective language, conditions, reasons, or warnings merely to shorten the subtitle.
- Give every split marker its own id, audio file, measured start/end, and subtitle cue.
- Do not insert arbitrary equal-duration slices. Timing must follow the actual audio boundary of the spoken subphrase.
- If audio is already generated, regenerate only the affected marker segments and rebuild the concatenated audio/timeline. If regeneration is unavailable, use word- or phrase-level alignment timestamps; never estimate sub-cue times from character ratios.
- Keep multiple subtitle cues on the same `visualCueId`/`stepId` when they explain one visual state. Subtitle splitting must not accidentally advance a formula step, graph state, or answer reveal.

## Canonical Audio-To-Frame Chain

Use one timing chain:

```text
measured audio cue -> subtitle cue -> visualCueId/stepId -> Remotion frame state
```

- Every narration cue must belong to a real scene and a stable visual step.
- A drawing, reveal, emphasis, formula transformation, conclusion, or answer state must occur inside the measured spoken interval that explains it.
- A visual conclusion must not appear before its spoken cue.
- A visual step must not remain active after narration advances unless consecutive cues intentionally share the same `visualCueId`/`stepId`.
- When narration changes, regenerate or remeasure affected audio and update subtitle ranges, scene boundaries, visual-step boundaries, and total frames together.
- During measured silence, hold the last meaningful visual state or an intentional thinking state.

## Doubao TTS

Use `$byted-text-to-speech` when generating audio with Volcengine Doubao.

Use the configured subject defaults unless the user specifies another voice:

- 数学、物理、化学、生物: `zh_female_yingyujiaoxue_uranus_bigtts`.
- 语文、英语、地理、历史: `zh_male_yuanboxiaoshu_uranus_bigtts`.

Recommended settings:

- normal explanation: `speechRate` around `0` to `5`;
- poem or classical recitation: `speechRate` around `-10` to `-18`;
- key conclusion or question: slow slightly and add a longer `pauseAfterMs`;
- keep sample rate stable across segments, usually `24000`.
- for reading-heavy Chinese segments, especially recitation, tune pauses and `speechRate` at marker level instead of trying to repair rhythm only in editing.

Chinese voice usage rules:

- use a calm senior-teacher delivery for explanation, not a theatrical performance;
- use a slower, more measured tone for poetry, prose excerpts, and classical Chinese recitation;
- use short marker segments for quoted text, current-line reading, questions, answer steps, and transitions;
- for expressive reading, split by line, couplet, sentence group, or emotional turn rather than by raw character count;
- keep the same speaker throughout one video unless the user explicitly requests multiple voices.

If environment variables are stored in shell startup files, load them before running the TTS script. Do not print API keys.

## Timing And Subtitle Rules

Generate timing from measured audio:

- use `ffprobe` to measure each segment duration;
- convert seconds to frames with the project FPS;
- set each subtitle `start` and `end` to the measured speech span;
- include `pauseAfterMs` in scene duration, but do not keep the subtitle visible through the whole pause unless the pause is meant for reading;
- update `timeline.json` and `TOTAL_FRAMES` from the final scene durations;
- when the project uses a TypeScript timing source, update that source from the generated timing record too; derive each scene boundary from the measured global start of its first subtitle, then derive the final scene from `totalFrames`;
- store a machine-readable timing record such as `voiceover/audio_timeline.json`.
- if the spoken phrase changes, the subtitle should also change. Do not leave an outdated subtitle block on screen to fill silence.
- if there is a silent gap between two spoken segments, the subtitle may disappear, but the main visual should hold the previous meaningful state or an intentional pause state instead of reverting to a default prompt.
- if a scene has visual states keyed to speech, expose the measured timings to the scene component or derive them from the same subtitle data. Avoid separate magic numbers such as `start + 180` for recitation or answer-step highlights.

Bottom subtitles must remain readable:

- at most two rendered lines, with one line preferred when the complete verbatim cue fits;
- split long examples, answers, conditions, and recitation text into multiple measured narration/subtitle segments;
- keep screen subtitles identical to the spoken segment text;
- verify dense answer scenes with still-frame renders.
- when subtitle text would produce a third line, split by semantic unit or pause point, not by arbitrary character count; then regenerate or align timing for each subphrase.

## Poetry And Classical Recitation

For Chinese poetry or classical-text reading scenes:

- mark each line or couplet as a separate segment;
- use a slower speech rate than explanation scenes;
- add pauses after semantic units, especially before major turns or questions;
- describe tone in the marker file: opening, image expansion, emotional turn, question, or closing force;
- make the visual highlight follow timed subtitle segments, not hard-coded frame estimates;
- keep line-by-line reveal and current-line emphasis synchronized with audio.
- use explicit pauses to preserve emotional rhythm between lines, turns, and closing emphasis.
- for a full or partial poem reading, each highlighted line/couplet should remain active until its measured audio segment ends, even if later lines have already been revealed.

## Validation

Before finishing:

- run typecheck or lint;
- render still frames for any scene with dense text, recitation, subtitles, or reported visual issues;
- check the final audio file exists under `public/audio/`;
- use `ffprobe` to confirm the rendered video has both video and audio streams and expected duration;
- inspect that subtitles never exceed two rendered lines and do not cover important visual labels.
- verify the final marker count and subtitle count match, ids/scenes align, and every subtitle string equals the exact TTS `text`.
- render the longest cues at the start, middle, and end of their spans; reject any third line, clipping, hidden overflow, unsafe font shrinking, or overlap.
- if the user asks for a dubbed final deliverable, spot-check the rendered video for lip-independent sync quality: spoken phrase, subtitle change, and scene emphasis should align closely by ear and by frame.
- after fixing an audio-sync issue in a project that already has a rendered output, re-render the final video and verify the output still contains both video and audio streams.
- do not report an existing MP4 as the new deliverable until its `ffprobe` duration agrees with the revised measured timeline.
