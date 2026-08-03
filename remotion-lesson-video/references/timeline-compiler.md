# 时间轴编译器 (timeline.ts)

## 设计目标

把"填时长 + 填口播文本"的纯数据，编译成带精确帧定位的 LessonSpec。

对齐 Codex 五讲重制版的三条原则：

1. **场景起点自动累加**：杜绝手抄帧偏移；
2. **cue 按时长均分并留白**：杜绝手抄 at 帧号；
3. **总帧数自校验**：不对直接抛错，把"时间轴错位"变成编译期错误。

## 完整代码

```typescript
// 时间轴编译器：把"填时长 + 填口播文本"的纯数据，编译成带精确帧定位的 LessonSpec。
// 设计目标（对齐 Codex 五讲重制版）：
//   1. 场景起点(from)由时长自动累加，杜绝手抄帧偏移；
//   2. 口播 cue 按场景时长均分并留白，杜绝手抄 at 帧号；
//   3. 编译后断言 总帧数 === targetFrames，否则抛错（自校验）。
//
// 本文件为纯数据/纯逻辑，不依赖 React / JSX，可被测试与脚本直接导入。

export type SceneKind =
  | 'cover' | 'hook' | 'map' | 'concept' | 'method'
  | 'example' | 'misconception' | 'review' | 'closing';

export type CoverVisual = {
  subject: string;
  titleLines: readonly string[];
  scope: string;
  subtitle: string;
};

export type ClosingVisual = {
  titleLines: readonly string[];
  takeaway: string;
  learningPath: readonly string[];
  subtitle: string;
};

/** 单个场景的输入（纯数据，无渲染逻辑） */
export type SceneInput = {
  slug: string;
  kind: SceneKind;
  title: string;
  context?: string;
  index?: string;           // 如 "01"；cover/closing 可不填
  duration: number;         // 帧
  cues: readonly string[];  // 口播文本列表；编译器负责均分时间戳
};

/** 一节课的完整输入 */
export type LessonInput = {
  compositionId: string;
  lessonNumber: number;
  title: string;
  scope: string;
  label: string;            // CourseChrome 左上角标签
  status: string;
  cover: CoverVisual;
  closing: ClosingVisual;
  coverFrames?: number;     // 默认 150
  closingFrames?: number;    // 默认 210
  targetFrames: number;      // 期望总帧数；不对则抛错
  scenes: readonly SceneInput[];
};

export type NarrationCue = {
  id: string;
  sceneId: string;
  start: number;
  end: number;
  text: string;
  subtitle: string;          // 通常与 text 相同
};

export type BuiltScene = {
  id: string;
  slug: string;
  kind: SceneKind;
  title: string;
  context?: string;
  index?: string;
  from: number;
  durationInFrames: number;
};

export type LessonSpec = Omit<LessonInput, 'scenes' | 'coverFrames' | 'closingFrames'> & {
  coverFrames: number;
  closingFrames: number;
  fps: number;
  width: number;
  height: number;
  durationInFrames: number;
  scenes: BuiltScene[];
  cues: NarrationCue[];
};
```

### buildLesson 编译函数

```typescript
const DEFAULT_COVER_FRAMES = 150;
const DEFAULT_CLOSING_FRAMES = 210;
const CANVAS = {fps: 30, width: 1920, height: 1080};
const CUE_PADDING_RATIO = 0.05;    // cue 两端各留 5% 空白
const CUE_PADDING_CAP = 45;        // 最大 padding 帧

export const buildLesson = (input: LessonInput): LessonSpec => {
  const cover = input.coverFrames ?? DEFAULT_COVER_FRAMES;
  const closing = input.closingFrames ?? DEFAULT_CLOSING_FRAMES;

  const scenes: BuiltScene[] = [];
  const cues: NarrationCue[] = [];
  let cursor = 0;

  const pushScene = (
    slug, kind, title, duration,
    opts = {},
  ) => {
    const sceneId = `L${input.lessonNumber}-${slug}`;
    scenes.push({id: sceneId, slug, kind, title,
      context: opts.context, index: opts.index,
      from: cursor, durationInFrames: duration});

    const texts = opts.cueTexts ?? [];
    if (texts.length > 0) {
      const padding = Math.min(CUE_PADDING_CAP, Math.floor(duration * CUE_PADDING_RATIO));
      const usable = Math.max(texts.length, duration - padding * 2);
      const cueDuration = Math.max(1, Math.floor(usable / texts.length));
      texts.forEach((text, i) => {
        const start = cursor + padding + i * cueDuration;
        const end = i === texts.length - 1 ? cursor + duration - padding : start + cueDuration;
        cues.push({id: `${sceneId}-C${i+1}`, sceneId, start, end, text, subtitle: text});
      });
    }
    cursor += duration;
  };

  pushScene('cover', 'cover', 'cover', cover, {cueTexts: [input.cover.subtitle]});
  for (const s of input.scenes)
    pushScene(s.slug, s.kind, s.title, s.duration,
      {context: s.context, index: s.index, cueTexts: s.cues});
  pushScene('closing', 'closing', 'closing', closing, {cueTexts: [input.closing.subtitle]});

  if (cursor !== input.targetFrames) throw new Error(
    `[${input.compositionId}] 时间轴总长度 ${cursor} 与目标 ${input.targetFrames} 不一致`);

  return {...input, coverFrames: cover, closingFrames: closing,
    ...CANVAS, durationInFrames: cursor, scenes, cues};
};
```

## 使用方式

```typescript
import {buildLesson, LessonInput} from './timeline';
import {lessonInputs} from './data/lesson-inputs';

const spec = buildLesson(lessonInputs.concept);  // 自动算所有 from/at/end
console.log(spec.scenes[0].from);               // 0 (cover)
console.log(spec.scenes[2].from);               // 150+420=570 (第二个正文场景起点)
console.log(spec.cues);                          // 所有 cue 的精确帧范围
```
