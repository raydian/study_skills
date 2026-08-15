---
name: video-voiceover
description: Generate and synchronize Doubao TTS voiceover audio for high-school subject and close-reading book explainer videos. Use when the user asks to create, add, regenerate, verify, or sync 配音, 旁白, 朗读音频, voiceover, TTS audio, narration, subtitles, or video timing from an audio script/口播稿/配音稿.
---

# Video Voiceover

Use this skill to turn a video directory plus an audio script into narration audio for a high-school subject video. The default engine is Volcengine/Doubao TTS, using the same API style as the project video workflow.

## Required Inputs

The normal user-facing inputs are only:

1. `video_dir`: the video project directory, for example `video/语文/03-梦游天姥吟留别`.
2. `script`: the audio script/口播稿/配音稿 file, or an explicit pasted script to save and synthesize.

If subject is not supplied, infer it from the path, especially `video/<学科>/<项目名>`.

## API Key Rules

- Use `MODEL_SPEECH_API_KEY` from the environment by default.
- Optional environment variables: `MODEL_SPEECH_API_BASE`, `MODEL_SPEECH_TTS_RESOURCE_ID`.
- Never write the API key into a video directory, generated JSON, source file, commit, log, or final answer.
- Never print the API key while debugging. If the key is missing, report only that `MODEL_SPEECH_API_KEY` is not set.
- If the user gives a different key location, pass it as `--api-key-env <ENV_NAME>` rather than copying the key.

## Voice Rules

Use subject-specific voice profiles. Read `references/voice-profiles.md` when choosing or adjusting the profile.

- 数学、物理、化学、生物: default speaker `zh_female_yingyujiaoxue_uranus_bigtts`.
- 语文、英语、地理、历史: default speaker `zh_male_yuanboxiaoshu_uranus_bigtts`.
- 精读图书视频讲解: required speaker `zh_male_yuanboxiaoshu_uranus_bigtts`.
- 语文: calm, literary, slower for formal whole-text reading.
- 数学: precise, steady, slightly faster explanation.
- 英语: clear bilingual classroom tone, preserving English terms.
- 物理: crisp experiment-and-model explanation.
- 化学: clear process explanation.
- 生物: gentle conceptual explanation.
- 历史: narrative and composed.
- 地理: broad, explanatory, map-reading tone.

Known speaker IDs above are the local stable defaults. If a video project or user requires another account-specific voice, pass `--speaker`.

Choose speech rate, pauses, and tone from the content before synthesis. After generating the approved voiceover, treat those delivery choices as locked: never change TTS speed, pause intervals, tone, or stretch/compress the audio merely to fit an existing video duration.

## Script Format

Read `references/script-format.md` if the provided script is not already segmented. Prefer JSON marks for exact control; Markdown 口播稿 is also supported.

For long literary texts, especially 语文古诗文, keep the formal original reading as separate marked segments rather than treating it as a brief excerpt. Use slower speech and longer pauses for reading/诵读 segments.

## Generate Audio

Run the bundled script:

```bash
python3 skills/video-voiceover/scripts/generate_voiceover.py \
  --video-dir video/语文/03-梦游天姥吟留别 \
  --script video/语文/03-梦游天姥吟留别/口播稿.md \
  --subject 语文
```

Typical outputs:

- `<video_dir>/voiceover/voiceover_marks.json`
- `<video_dir>/voiceover/audio_timeline.json`
- `<video_dir>/voiceover/segments/*.mp3`
- `<video_dir>/public/audio/voiceover.mp3`

Use `--dry-run` to parse and normalize the marks without calling the TTS API.

Use `--sync-remotion` when the project has `src/data/subtitles.ts` and the voiceover should drive scene/subtitle timing. The script measures real audio durations with `ffprobe`, then syncs timings from measured audio rather than estimated text length. If the project stores scene durations in `src/timeline.ts` (or another project-owned timing file), update that file from `voiceover/audio_timeline.json` after generation; do not leave earlier estimated durations in place.

### Sync Script Pitfalls (reusable)

When a project owns `src/data/timeline.ts` with an estimated-text timeline and you write a custom `scripts/sync_timeline_from_audio.cjs`:

1. **Idempotency**: do NOT overwrite `voiceover/audio_timeline.json` in place. Write the cover-offset version to `voiceover/audio_timeline_synced.json` and rewrite `timeline.ts` from that; otherwise re-running the script double-applies the cover offset.
2. **Never parse scene metadata from the existing timeline.ts**: the first sync rewrites that file, so a regex over `SCENE_SEEDS` breaks on the second run (and `[a-z0-9]+` misses camelCase ids like `p1Joy`/`p4Water`). Embed a fixed `SCENE_META` table (id/title/context/mode) in the script and take cue texts from `voiceover/voiceover_marks.json` (identical to the TTS segments).
3. **Cover lead silence**: prepend 75 frames (2.5 s) to the audio timeline and add the same 75 frames to the cover scene duration, then also prepend 2.5 s of silence to the MP3 (`ffmpeg concat anullsrc`) so audio, subtitles and video stay aligned from frame 0.
4. **Recitation detection**: the generator's `is_recitation` heuristic flags any short quoted classical line as 朗读 (-14 slow). For lesson scripts that quote lines inside explanation scenes, write explicit `speechRate`/`pauseAfterMs`/`tone` into `voiceover_marks.json` (朗读 scenes -14/420, explanation scenes -2/260) instead of relying on the heuristic.
5. **Global subtitle overlap**: in the composition, the global `<Subtitle>` renders the cover's cue at frame 0 and overrides the cover page's own delayed subtitle. Restrict the global Subtitle to `frame >= SCENE_STARTS.read1 && frame < SCENE_STARTS.closing` so cover/closing pages manage their own subtitle.

## Mandatory Three-Source Synchronization

Apply this workflow to every video voiceover task, including close-reading book explainers:

1. Inspect the actual video playback content, scene order, current frame count, subtitle content/timing, and generated voiceover before declaring the task complete.
2. Use the measured voiceover timeline as the single timing source of truth. Make each subtitle's text correspond to the spoken segment and make its visible interval follow that segment's measured audio interval.
3. Make each visual scene cover the matching narration and subtitle interval. Adjust scene duration, transitions, composition duration, and playback frame counts to the voiceover timeline.
4. If video duration and voiceover duration differ, change the video timing and frame counts. Do not solve the mismatch by changing voiceover speed, pause intervals, tone, prosody, or by time-stretching/compressing the audio.
5. Derive all scene boundaries from cumulative global audio times converted at the composition FPS. Ensure scene frame counts sum exactly to the composition's total frame count; do not independently round scene durations and accumulate drift.
6. Re-render or preview the complete result and verify the same content is aligned across all three sources: visuals, subtitles, and voiceover.

## After Generation

1. Confirm `public/audio/voiceover.mp3` exists and has nonzero duration.
2. Confirm subtitle timings in `voiceover/audio_timeline.json` (raw) and `voiceover/audio_timeline_synced.json` (with cover offset).
3. Ensure the video composition uses `staticFile("audio/voiceover.mp3")` for narration.
4. Render or preview the complete video and inspect playback content, scene order, subtitles, and narration together; check that there is no long blank tail, silent missing section, subtitle-free ending, mismatched line, or early visual cut.
5. Verify every subtitle is inside its matching scene and each scene starts and ends on cumulative frame boundaries derived from measured audio. Confirm the sum of scene frames equals the composition's total frames.
6. Run a whole-video silence check: extract silence ranges with `ffmpeg -af silencedetect=noise=-38dB:d=0.4` and assert every subtitle `start` falls inside a silence range (0 mismatches), and the last subtitle `end` is before the audio total (no blank tail).
7. Confirm the video duration matches the voiceover-driven total within one frame. Resolve any mismatch only by changing video timing/frame counts and regenerating subtitle timing, never by altering the approved voiceover delivery.
8. If a final MP4 already exists, re-render it and confirm its modification time, duration, and video/audio streams with `ffprobe` before calling it updated.
