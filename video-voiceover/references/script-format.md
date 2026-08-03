# Voiceover Script Format

The generator accepts JSON marks or Markdown scripts.

## JSON Marks

Use JSON when exact segmentation, scene binding, pauses, or speech rates matter.

```json
[
  {
    "id": "01-001",
    "scene": "01",
    "text": "同学们好，这节课我们完整朗读并解读《梦游天姥吟留别》。",
    "subtitle": "同学们好，这节课我们完整朗读并解读《梦游天姥吟留别》。",
    "tone": "亲切开场",
    "speechRate": -2,
    "pauseAfterMs": 260
  }
]
```

Supported optional fields:

- `id`: stable segment id. If omitted, generated from scene and order.
- `scene`: scene id or page id. If omitted, inferred from headings or sequence.
- `text`: text sent to TTS. Required.
- `subtitle`: subtitle text. Defaults to `text`.
- `tone`: human-readable narration intent. Used to detect 朗读/诵读.
- `speaker`: per-segment speaker override.
- `speechRate`: per-segment TTS speed override.
- `loudnessRate`: per-segment loudness override.
- `pauseAfterMs`: silence after the segment.

## Markdown Script

Markdown headings become scene boundaries. Paragraphs and bullet items become narration segments.

```markdown
## 01 开场

同学们好，这节课我们完整朗读并解读《梦游天姥吟留别》。

## 02 正式整篇原文朗读

海客谈瀛洲，烟涛微茫信难求。
越人语天姥，云霞明灭或可睹。

## 03 第一阶段解读

- 这一阶段先写梦游的缘起。
- 重点抓住“瀛洲”和“天姥”的对比。
```

## Long Chinese Literature

For 语文古诗文:

- Use a dedicated heading for `正式整篇原文朗读`.
- Preserve the whole original text, not only excerpts.
- Split by poem line or semantic unit.
- Do not merge many long lines into one TTS segment.
- Add explanation sections after the complete reading, stage by stage.
