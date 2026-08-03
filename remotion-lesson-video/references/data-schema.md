# 纯数据 Schema (lesson-inputs.ts)

## 设计原则

`lesson-inputs.ts` 是整条流水线的**单一数据源**。视频时间轴、口播字幕 cue、口播稿文档都从这里来。改时长只改 `duration`；改口播只改 `cues` 文本；改完跑 `buildLesson` 自动重算所有帧定位。

## 导出格式

```typescript
import type {LessonInput} from '../timeline';

export const lessonInputs = {
  concept: { /* LessonInput 对象 */ },
  application: { /* LessonInput 对象 */ },
  // ... 按需添加课时 key
} as const;
```

## LessonInput 字段详解

| 字段 | 类型 | 说明 |
|---|---|---|
| `compositionId` | `string` | Remotion Composition ID（如 `'ExpConcept'`），Root.tsx 中注册 |
| `lessonNumber` | `number` | 课时编号（用于生成 sceneId 前缀 `L1-xxx`） |
| `title` | `string` | 讲标题（如"指数函数的概念"） |
| `scope` | `string` | 所属章节范围（如"4.2 指数函数 · 第①讲"） |
| `label` | `string` | CourseChrome 左上角标签（如"高中数学 · 指数函数①"） |
| `status` | `string` | 状态标签（如"核心精讲"、"方法总结"） |
| `cover` | `CoverVisual` | 封面视觉数据（subject/titleLines/scope/subtitle） |
| `closing` | `ClosingVisual` | 结束页视觉数据（titleLines/takeaway/learningPath/subtitle） |
| `coverFrames?` | `number` | 封面帧数（默认 150） |
| `closingFrames?` | `number` | 结束页帧数（默认 210） |
| `targetFrames` | `number` | **期望总帧数** = cover + Σscenes.duration + closing；不对则 buildLesson 抛错 |
| `scenes` | `SceneInput[]` | 正文场景列表 |

### SceneInput

| 字段 | 类型 | 说明 |
|---|---|---|
| `slug` | `string` | 场景标识（如 `'c-hook'`、`'app-growth'`），唯一，用于映射渲染组件 |
| `kind` | `SceneKind` | 场景类型：'hook'\|'map'\|'concept'\|'method'\|'example'\|... |
| `title` | `string` | SceneFrame 标题栏显示的标题 |
| `context?` | `string` | SceneFrame 副标题（如"增长率恒定 vs 衰减率恒定"） |
| `index?` | `string` | 编号（如 "01"） |
| `duration` | `number` | **场景时长（帧）**——这是你唯一直接控制的帧级参数 |
| `cues` | `string[]` | 该场景的口播文本列表（按出现顺序）；编译器自动均分时间戳 |

## targetFrames 计算示例

```typescript
// cover(默认 150) + 3 个场景(420+420+480) + closing(默认 210)
targetFrames: 1680,
```

如果改了任一 scene 的 duration 但忘了更新 targetFrames，buildLesson 会抛出明确错误：

```
[ExpConcept] 时间轴总长度 1720 与目标 1680 不一致（检查各场景 duration + cover/closing 帧数）
```

## 口播稿自动生成

运行 `node scripts/gen-script.mjs` 即可从 lesson-inputs 数据自动生成 `口播稿.md`。每条 cue 输出为 `id：text` 格式，与视频字幕逐条一致。

> **不要手动编辑口播稿中的 cue 文本**——应修改 `lesson-inputs.ts` 后重新运行脚本。
