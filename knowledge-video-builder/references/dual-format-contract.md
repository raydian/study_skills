# Dual-Format Contract

## Contents

1. Single Source Of Truth
2. Shared And Aspect-Specific Data
3. Timeline And Caption Schema
4. Editorial Script Rules
5. Non-Rendering Validation

## Single Source Of Truth

Use one authored semantic timeline and one caption dataset for both `1920x1080` and `1080x1920` compositions.

Require both compositions to share:

- scene ids and order;
- editorial script cue ids;
- exact caption text;
- caption start and end times;
- scene boundaries;
- semantic reveal order;
- total duration.

Do not create a shorter vertical edit inside the same project. Create a separate project when a platform requires different content or duration.

## Shared And Aspect-Specific Data

Share:

```text
content data
scene data
authored timeline
Caption[] JSON
editorial script cues
semantic visual cue ids
```

Keep aspect-specific:

```text
layout component
font scale
panel geometry
diagram orientation
simultaneous item count
camera crop or visual framing
reveal cadence
transition presentation when geometry requires it
```

Do not create one oversized universal canvas and crop or scale it. Build each aspect ratio from shared semantic data and explicit adaptive layout configuration.

## Timeline And Caption Schema

Keep the frame-based scene timeline separate from the millisecond-based Remotion captions while deriving both from the same authored cue definitions.

Example timeline:

```json
{
  "fps": 30,
  "totalFrames": 9000,
  "scenes": [
    {
      "id": "cover",
      "startFrame": 0,
      "endFrame": 1,
      "visualCueIds": ["cover-title"]
    },
    {
      "id": "hook",
      "startFrame": 1,
      "endFrame": 151,
      "visualCueIds": ["hook-question"]
    }
  ]
}
```

Store subtitles as JSON using the Remotion `Caption` type:

```ts
import type {Caption} from "@remotion/captions";

type Caption = {
  text: string;
  startMs: number;
  endMs: number;
  timestampMs: number | null;
  confidence: number | null;
};
```

Example:

```json
[
  {
    "text": "为什么越努力记，反而忘得越快？",
    "startMs": 34,
    "endMs": 3200,
    "timestampMs": null,
    "confidence": null
  }
]
```

Require:

- no caption covers frame `0`;
- captions start no earlier than frame `1` converted to milliseconds;
- every caption belongs to one real scene;
- ranges are ordered, non-overlapping, and inside total duration;
- both compositions use the same caption JSON and total frame count;
- visual changes bind to stable visual cue ids, not array indexes.
- every caption cue renders in at most two lines in both aspect ratios;
- any cue that exceeds two lines in either format is split into consecutive, non-overlapping cues with separate time or frame ranges.

## Editorial Script Rules

Keep `口播稿.md` as an editorial source for captions and possible future human voice production. Do not synthesize or embed audio.

Avoid aspect-dependent wording:

- “看左边” / “看右边”;
- “上面的数据” / “下方这张表”;
- “横向比较” when the vertical layout is stacked;
- “三个卡片同时出现” when the vertical layout reveals them sequentially.

Refer to concepts by name. Split long cues at punctuation, clauses, or complete semantic units whenever either aspect ratio would exceed two subtitle lines. Give every resulting cue its own consecutive playback range. Update the shared script cue, caption JSON, and timeline together; do not patch one composition independently.

Never solve an overlong cue by:

- reducing subtitle font size below the visual-system minimum;
- using negative letter spacing or horizontal scaling;
- clipping, masking, ellipsizing, or hiding overflow;
- showing three or more lines;
- displaying two split cues at the same time.

## Non-Rendering Validation

Register two compositions:

```text
KnowledgeWide      1920x1080 @ 30fps
KnowledgeVertical  1080x1920 @ 30fps
```

Validate without media rendering:

- equal fps, duration, scene ids, and scene boundaries;
- identical caption count, text, and timing;
- complete large-title cover at frame `0` only;
- independent hook page starting at frame `1`;
- no caption at frame `0`;
- no direction-dependent script wording;
- no third subtitle line by deterministic text measurement in either format;
- every overlong source sentence is represented by multiple ordered, non-overlapping caption cues and playback ranges;
- no horizontal layout mechanically reused as vertical;
- no fixed page geometry, uniform scale transform, or unchanged multi-column grid shared across aspect ratios;
- vertical scenes respect their lower simultaneous-item limit and sequential reveal plan;
- no audio import, TTS integration, render script, or generated media output.

Do not run still or video rendering as part of validation.

## Studio Timeline Contract

Register named Remotion `Sequence` ranges for every shared semantic scene. Names must be human-readable and match storyboard order, so Studio exposes a navigable scene timeline rather than an undifferentiated root track.

Pure React/SVG compositions do not automatically produce an NLE-style thumbnail strip in Studio. Treat named scene ranges, frame counters, and the preview canvas as the supported navigation contract. Generate representative still frames only after a separate explicit user instruction for visual preview.
