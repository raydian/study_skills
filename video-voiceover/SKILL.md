---
name: video-voiceover
agent_created: true
description: Generate subject-specific Doubao TTS voiceover audio for high-school subject video projects. Use when the user asks to create, add, regenerate, or sync 配音, 旁白, 朗读音频, voiceover, TTS audio, or narration for a video directory from an audio script/口播稿/配音稿.
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
- 语文: calm, literary, slower for formal whole-text reading.
- 数学: precise, steady, slightly faster explanation.
- 英语: clear bilingual classroom tone, preserving English terms.
- 物理: crisp experiment-and-model explanation.
- 化学: clear process explanation.
- 生物: gentle conceptual explanation.
- 历史: narrative and composed.
- 地理: broad, explanatory, map-reading tone.

Known speaker IDs above are the local stable defaults. If a video project or user requires another account-specific voice, pass `--speaker`.

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

## After Generation

1. Confirm `public/audio/voiceover.mp3` exists and has nonzero duration.
2. Confirm subtitle timings in `voiceover/audio_timeline.json`.
3. Ensure the video composition uses `staticFile("audio/voiceover.mp3")` for narration.
4. Render or preview the video and check that there is no long blank tail, silent missing section, or subtitle-free ending.
5. Verify every subtitle is inside its scene and each scene starts at the measured global start of its first subtitle. Do not sum independently rounded scene durations when those values can drift by frames.
6. If a final MP4 already exists, re-render it and confirm its modification time, duration, and video/audio streams with `ffprobe` before calling it updated.
