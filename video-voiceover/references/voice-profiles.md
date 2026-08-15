# Subject Voice Profiles

These profiles are defaults for high-school learning videos. Speaker availability depends on the connected Volcengine/Doubao account, so keep `--speaker` available for overrides.

## Stable Local Speaker IDs

- `zh_female_yingyujiaoxue_uranus_bigtts`: female classroom-teaching voice, used by mathematics, physics, chemistry, and biology.
- `zh_male_yuanboxiaoshu_uranus_bigtts`: male explanatory voice, used by Chinese, English, geography, and history.

Close-reading book explainer videos must use `zh_male_yuanboxiaoshu_uranus_bigtts` unless the user explicitly requests another speaker.

Do not invent a speaker ID when the account catalog is unknown. Use one of the stable IDs above or ask the user for an account-specific speaker ID.

## Profiles

| Subject | Default speaker | Speech rate | Pause | Style |
| --- | --- | ---: | ---: | --- |
| 语文 | `zh_male_yuanboxiaoshu_uranus_bigtts` | -2 | 260 ms | Literary, calm, interpretive |
| 语文朗读/诵读 | `zh_male_yuanboxiaoshu_uranus_bigtts` | -14 | 420 ms | Formal whole-text reading, line-by-line breathing |
| 数学 | `zh_female_yingyujiaoxue_uranus_bigtts` | 2 | 180 ms | Precise, compact, step-by-step |
| 英语 | `zh_male_yuanboxiaoshu_uranus_bigtts` | 0 | 220 ms | Clear bilingual terms preserved |
| 物理 | `zh_female_yingyujiaoxue_uranus_bigtts` | 1 | 200 ms | Crisp, model/process oriented |
| 化学 | `zh_female_yingyujiaoxue_uranus_bigtts` | 1 | 210 ms | Clear process and experiment narration |
| 生物 | `zh_female_yingyujiaoxue_uranus_bigtts` | 0 | 220 ms | Gentle, concept-rich explanation |
| 历史 | `zh_male_yuanboxiaoshu_uranus_bigtts` | -1 | 240 ms | Narrative, composed, causal |
| 地理 | `zh_male_yuanboxiaoshu_uranus_bigtts` | 0 | 220 ms | Map-reading and regional explanation |
| 精读图书视频讲解 | `zh_male_yuanboxiaoshu_uranus_bigtts` | 0 | 240 ms | Composed, engaging close reading and interpretation |

## Adjustment Rules

- For original literary reading, lower speed and lengthen pause. This is required for long Chinese poems and classical prose.
- For formula-heavy math or physics explanation, avoid very slow narration; clarity comes from segmentation and pauses after formulas.
- For English scripts, preserve English terms and punctuation. If the account has a better English or bilingual voice, pass it with `--speaker`.
- For videos with dense captions, prefer shorter segments and measured timing over long paragraph synthesis.
- If a generated voice feels too rushed, reduce `speechRate` in the marks or pass a slower subject profile rather than stretching audio afterward.
- Set delivery parameters for content quality before synthesis. Once the voiceover is approved or used as the synchronization source, do not change its speaker, speech rate, pauses, tone, or prosody to fit the picture; retime the video and subtitles instead.
