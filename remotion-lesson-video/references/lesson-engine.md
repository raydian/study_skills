# 统一渲染引擎 (LessonVideo + 薄包装 + 数据构建层)

## 架构概览

```
lesson-inputs.ts (纯数据)
    ↓  buildLesson() 编译
lessons.tsx        (数据 → 带 render 函数的 ResolvedLesson)
    ↓
*Video.tsx         (~4行薄包装: <LessonVideo lesson={lessons.xxx} />)
    ↓
LessonVideo.tsx    (统一引擎: cover/场景/closing 全部复用)
    ↓
SceneFrame / Subtitle / Background / CourseChrome
    ↓
*Scenes.tsx       (bespoke 场景内容，只写"画面内部")
```

## LessonVideo.tsx — 统一引擎

```tsx
import React from 'react';
import {AbsoluteFill, Sequence, useCurrentFrame} from 'remotion';
import {Background} from '../components/Background';
import {CourseChrome} from '../components/CourseChrome';
import {Subtitle} from '../components/Subtitle';
import {CoverPage} from '../components/CoverPage';
import {ClosingPage} from '../components/ClosingPage';
import {SceneFrame} from '../components/SceneFrame';
import {STYLE} from '../config/video-style';
import type {LessonSpec, BuiltScene} from '../timeline';

export type ResolvedScene = BuiltScene & {render?: React.FC};
export type ResolvedLesson = Omit<LessonSpec, 'scenes'> & {scenes: ResolvedScene[]};

// 取当前帧应显示的字幕：取 start<=frame 的最后一个 cue
const activeSubtitle = (lesson: ResolvedLesson, frame: number): string => {
  let text = '';
  for (const c of lesson.cues) {
    if (c.start <= frame) text = c.subtitle;
    else break;
  }
  return text;
};

export const LessonVideo: React.FC<{lesson: ResolvedLesson}> = ({lesson}) => {
  const frame = useCurrentFrame();
  const subtitle = activeSubtitle(lesson, frame);

  return (
    <AbsoluteFill style={{color: STYLE.colors.textPrimary, fontFamily: STYLE.fonts.sans}}>
      {lesson.scenes.map((scene) => {
        if (scene.kind === 'cover') {
          return (
            <Sequence key={scene.id} from={scene.from}
              durationInFrames={scene.durationInFrames} name="cover">
              <CoverPage frame={frame - scene.from}
                durationInFrames={scene.durationInFrames} {...lesson.cover} />
            </Sequence>
          );
        }
        if (scene.kind === 'closing') {
          return (
            <Sequence key={scene.id} from={scene.from}
              durationInFrames={scene.durationInFrames} name="closing">
              <ClosingPage frame={frame - scene.from}
                durationInFrames={scene.durationInFrames} {...lesson.closing} />
            </Sequence>
          );
        }
        // 正文场景：引擎统一提供背景、标题栏、字幕；内容委托给 scene.render
        return (
          <Sequence key={scene.id} from={scene.from}
            durationInFrames={scene.durationInFrames} name={scene.slug}>
            <AbsoluteFill>
              <Background frame={frame} />
              <CourseChrome frame={frame}
                durationInFrames={lesson.durationInFrames}
                label={lesson.label} status={lesson.status} />
              <SceneFrame index={scene.index ?? ''} title={scene.title}
                context={scene.context}>
                {scene.render ? <scene.render /> : null}
              </SceneFrame>
              <Subtitle text={subtitle} />
            </AbsoluteFill>
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
```

## 薄包装组件（~4 行）

每个 Composition 只是一个数据绑定：

```tsx
import {LessonVideo} from '../shared/LessonVideo';
import {lessons} from '../data/lessons';

export const ConceptVideo: React.FC = () =>
  <LessonVideo lesson={lessons.concept} />;
```

**关键点**：这里没有任何场景逻辑或帧计算。所有时间轴和字幕都由 `buildLesson` + `LessonVideo` 处理。

## 数据构建层 (lessons.tsx)

把 slug 映射到对应的场景渲染函数：

```tsx
import {buildLesson} from '../timeline';
import {lessonInputs} from './lesson-inputs';
import {ConceptScenes} from '../lessons/ConceptScenes';
import {ApplicationScenes} from '../lessons/ApplicationScenes';
import type {ResolvedLesson} from '../shared/LessonVideo';

const RENDERERS: Record<string, React.FC> = {
  'c-hook': ConceptScenes.HookScene,
  'c-def': ConceptScenes.DefScene,
  // ... 每个 scene slug → 对应的 React 函数式组件
};

export const buildResolvedLesson = (key: keyof typeof lessonInputs): ResolvedLesson => {
  const spec = buildLesson(lessonInputs[key]);
  return {
    ...spec,
    scenes: spec.scenes.map((s) => ({
      ...s,
      render: s.kind === 'cover' || s.kind === 'closing' ? undefined : RENDERERS[s.slug],
    })),
  };
};

export const lessons = Object.fromEntries(
  (Object.keys(lessonInputs) as (keyof typeof lessonInputs)[])
    .map((k) => [k, buildResolvedLesson(k)]),
) as Record<keyof typeof lessonInputs, ResolvedLesson>;
```

## Root.tsx 注册

```tsx
import {Composition} from 'remotion';
import {ConceptVideo} from './lessons/ConceptVideo';
import {lessons} from './data/lessons';
import {STYLE} from './config/video-style';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="ExpConcept" component={ConceptVideo}
      durationInFrames={lessons.concept.durationInFrames}
      fps={STYLE.canvas.fps} width={STYLE.canvas.width} height={STYLE.canvas.height} />
    {/* 每个课时一个 Composition */}
  </>
);
```
