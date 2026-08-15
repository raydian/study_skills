# Video script schema

`video-script.json` is UTF-8 JSON and the canonical production contract. Use `schema_version: 3`. Version 3 makes the initial Remotion project silent, forbids rendering, requires shared dependency reuse, gives every Studio timeline page a stable number and name, and gates the `video-voiceover` handoff on explicit Studio confirmation.

## Root object

| Field | Requirement |
|---|---|
| `project` | title, book title, audience, target duration, aspect ratio, resolution, spoiler policy |
| `global_video_thesis` | statement, viewer shift, scope, counter-thesis |
| `book_profile` | primary/secondary types and knowledge-structure scores |
| `narrative_plan` | Narrative Mode, arc steps, selected knowledge-unit IDs |
| `visual_bible` | style, palette, recurring motifs, continuity, forbidden elements |
| `remotion` | engine, composition ID, fps, dimensions, estimated total frames, Studio state, no-render/audio policies, shared-dependency policy, explicit named-timeline mode |
| `voiceover_handoff` | gated `video-voiceover` script, synchronization, preview, and no-render policy |
| `pages` | ordered array of complete page records |

Store the thesis exclusion rule and proof obligations in `video-brief.json` if they are not repeated in the canonical script.

Use this Remotion root object for a 1920×1080, 30 fps production:

```json
{
  "engine": "remotion",
  "composition_id": "DeepBookVideo",
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "duration_in_frames": 300,
  "studio_confirmation": "pending",
  "render_policy": "do_not_render",
  "audio_policy": "no_audio_before_studio_confirmation",
  "dependency_policy": "reuse_video_shared_node_modules_symlink",
  "studio_timeline_mode": "explicit_named_sequences"
}
```

Before Studio confirmation, use:

```json
{
  "skill": "video-voiceover",
  "status": "blocked_until_studio_confirmed",
  "script_file": "voiceover-script.json",
  "sync_remotion": true,
  "subject_hint": "历史",
  "render_after_voiceover": false,
  "preview_after_voiceover": true
}
```

After explicit confirmation, change only the Studio state to `approved` and the handoff status to `ready`; then invoke `video-voiceover`. For unsupported book profiles, set `subject_hint` to `requires_user_selection` until a supported subject or speaker is chosen.

## Required page record

Every page, including title, hook, section bridge, quotation, recap, and ending, requires:

```json
{
  "page_id": "P001",
  "page_name": "开场：看不见的规则",
  "studio_sequence_name": "P001｜开场：看不见的规则",
  "sequence": 1,
  "page_type": "hook",
  "page_purpose": "用一个反常识问题建立全片认知张力。",
  "thesis_relation": "opens",
  "content_route": {
    "primary_role": "argument",
    "depth_engine": "argument-assumption",
    "reasoning_move": "把常见解释改写为作者真正追问的问题。"
  },
  "claim": "作者把部分失败重新解释为结构性规则对行动边界的提前限定。",
  "knowledge_unit_ids": ["ku-claim-0001"],
  "source_refs": [
    {"ref": "ch01-p003", "pages": ["8"], "relation": "states"}
  ],
  "attribution": "author_claim",
  "evidence_quality": {
    "strength": "moderate",
    "directness": "direct",
    "limitations": ["开场只提出问题，证据在后续页面展开。"]
  },
  "subtitle": {
    "text": "真正限制我们的，也许不是能力，而是看不见的规则。",
    "lines": ["真正限制我们的，也许不是能力", "而是看不见的规则"],
    "placement": "lower_third",
    "font_family": "Noto Sans CJK SC",
    "font_size_px": 72,
    "font_weight": 700,
    "text_color": "#FFFFFF",
    "background_treatment": "solid_scrim_72pct",
    "contrast_ratio_target": 7.0
  },
  "voiceover": {
    "text": "我们通常把失败归因于能力不足，但作者追问的是：是否有一套看不见的规则，提前划定了行动边界？",
    "delivery": "克制、清晰，在问句前短暂停顿。"
  },
  "duration_seconds": 10,
  "remotion_timeline": {
    "start_frame": 0,
    "duration_in_frames": 300,
    "end_frame_exclusive": 300,
    "image_src": "images/P001.png"
  },
  "visual": {
    "function": "symbolize",
    "image_prompt": {
      "subject": "一位人物站在由透明边界切割的空间中",
      "setting": "抽象但可信的现代城市边缘",
      "action": "人物伸手触碰不可见边界",
      "era_culture": "当代中国城市语境，服饰与建筑准确",
      "art_direction": "电影感写实摄影，避免概念海报俗套",
      "palette": "深蓝灰背景配一处暖色人物光",
      "lighting": "侧逆光勾勒轮廓，字幕区保持均匀暗部",
      "camera": "35mm 中远景，平视",
      "composition": "人物置于右侧三分线，画面下方留连续暗区",
      "symbolic_elements": ["透明边界", "远处开放通道"],
      "continuity": "沿用全片深蓝灰与暖色主体的视觉母题",
      "safe_text_area": "下方 36% 无人物、无高光、无复杂纹理",
      "realism_constraints": ["手部结构正常", "城市透视正确", "不生成可核验数据"],
      "negative_prompt": "文字、字母、数字、书名、标志、水印、边框、畸形手、杂乱字幕区",
      "rendered_prompt": "16:9 全屏电影感写实画面：当代中国城市边缘，一位人物站在由透明边界切割的空间中，伸手触碰不可见边界。35mm 平视中远景，人物位于右侧三分线，深蓝灰环境以暖色侧逆光勾勒主体；画面下方 36% 保持连续、均匀、低纹理暗区，禁止人物、高光和复杂物体进入字幕安全区。透明边界与远处开放通道形成克制象征。建筑透视、服饰、手部结构准确。不生成文字、字母、数字、书名、标志、水印、边框或可核验数据。"
    },
    "composition": {
      "focal_point": "右侧人物与边界接触处",
      "depth_layers": ["前景暗部", "中景人物", "远景通道"],
      "text_safe_zone": "bottom_36_percent",
      "reading_order": "先人物，再边界，最后字幕",
      "crop_safety": "兼容 16:9 中心裁切"
    },
    "readability": {
      "background_control": "字幕区降细节并压暗",
      "local_contrast": "白字对深色实底",
      "busy_area_avoidance": "字幕区不出现脸、手、边缘线或光源",
      "subtitle_box": "黑色实底 72% 不透明度并保留内边距",
      "min_font_px": 64
    }
  },
  "transition": "hard_cut"
}
```

Production prompts must assemble every structured field into a detailed, directly usable image-generation instruction like the example above.

## Controlled vocabularies

- `page_type`: `title`, `hook`, `context`, `question`, `definition`, `claim`, `mechanism`, `evidence`, `case`, `turning_point`, `method`, `derivation`, `close_reading`, `counterpoint`, `limitation`, `application`, `synthesis`, `ending`, `credits`.
- `thesis_relation`: `opens`, `defines`, `advances`, `evidences`, `explains`, `contrasts`, `qualifies`, `applies`, `synthesizes`.
- `evidence_quality.strength`: `strong`, `moderate`, `weak`, `not_applicable`.
- `evidence_quality.directness`: `direct`, `indirect`, `anecdotal`, `inferred`, `not_applicable`.
- `transition`: only `hard_cut` for this static format.

## Page identity and Studio naming

- `page_id` must match `P\d{3,}` and remains stable after assignment. Reordering a page changes `sequence`, not its ID.
- `page_name` is a concise human-readable description of the page's reasoning function or content.
- `studio_sequence_name` must equal `page_id + "｜" + page_name` exactly and be unique.
- Use the same ID in image filenames, `timeline.json`, explicit `Series.Sequence` markup, voiceover `scene`, QA reports, and revision requests.
- `BookVideo.tsx` contains one explicit named sequence per page. Runtime `.map()` generation of Studio page sequences is forbidden because pages must remain individually visible and addressable in Studio.

## Source and claim rules

Title and credits pages still cite the manifest, bibliographic source, or production source record. A page containing only an editorial navigation line uses `attribution: editorial_note` and explains why evidence strength is `not_applicable`.

One page should normally carry one material claim. If two claims need different evidence, Depth Engines, limitations, or subtitle anchors, use two pages.

## Duration and totals

`project.target_duration_seconds` must equal the sum of page durations within a small editorial tolerance. Sequence values are unique, contiguous, and start at 1. Page IDs and Studio sequence names are unique.

Remotion frame ranges are exact and contiguous. The first `start_frame` is 0; each page's `end_frame_exclusive` equals `start_frame + duration_in_frames`; the next page starts at that exclusive end; the root `remotion.duration_in_frames` equals the final exclusive end. Compute boundaries from cumulative seconds as defined in [remotion-production.md](remotion-production.md), not by rounding every page independently.

The initial script and project contain no `audio_src`, codec, output file, or render command. The project `node_modules` is a verified symbolic link to a compatible shared directory inside the enclosing `video/` root. Estimated page timings and visible `P###｜page name` timeline items are reviewed in Studio. After approval, `video-voiceover --sync-remotion` writes measured timings into the Remotion project's `src/timeline.json`; it must preserve scene IDs and names and does not authorize rendering.
