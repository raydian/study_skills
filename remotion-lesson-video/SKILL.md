---
name: remotion-lesson-video
description: 数据驱动 Remotion 课时视频工程范式。在创建或重构高中学科知识点教学视频（Remotion 工程）时使用此技能，确保产出采用「纯数据层 + 时间轴编译器 + 统一引擎 + 薄包装组件」架构，自带时间轴自校验、口播稿↔字幕一致性守卫、KaTeX 公式守卫、CSS 动画禁止守卫。触发词：remotion 视频架构, 数据驱动视频, 课时引擎, 视频工程范式, lesson video architecture。
---

# 数据驱动课时视频工程（Remotion Lesson Video）

## 概述

本技能定义了一套 **数据驱动的 Remotion 课时视频工程范式**。它将传统"手写胖组件+硬编码帧偏移"的视频工程升级为四层分离架构：

```
types/          ← 场景、口播、课时的类型定义
  ↓
data/           ← 纯数据：每讲的时长、标题、口播文本（单一数据源）
  ↓
timeline.ts     ← 编译器：自动算场景起点、均分 cue 时间戳、断言总帧数
  ↓
lessons/*.tsx   ← 薄包装（4 行）：每个 Composition 只是一个数据绑定
shared/LessonVideo.tsx ← 统一渲染引擎：cover / 场景 / closing 全部复用
```

**核心价值**：改任一段时长后 `buildLesson` 自动重算所有帧偏移，对不上直接抛错——把"时间轴错位"变成编译期错误。口播稿由 `gen-script.mjs` 从同一数据源生成，杜绝手抄不一致。

## 适用范围

任何使用 Remotion 创建的高中学科**单课时教学视频**项目（数学、物理、化学等），尤其是：
- 新建一个知识点视频工程时（应从数学模板派生）
- 重构现有"胖组件"视频工程为数据驱动架构时
- 需要给视频工程添加时间轴自校验和口播稿同步机制时

## 工作流

### 从模板新建（推荐）

1. 用 `create_math_video.py` 或手动从 `video/数学/数学视频模板/` 复制出新工程目录。
2. 编辑 `src/data/lesson-inputs.ts`：
   - 把占位 `template` 改成你的课时 key（如 `'concept'`）。
   - 填写 compositionId、title、scope、label、cover/closing 视觉信息。
   - 定义 scenes 数组（每个 slug、kind、title、duration、cues）。
   - 设定 targetFrames（= coverFrames + Σscenes.duration + closingFrames；不对会报错）。
3. 编辑 `src/lessons/*Scenes.tsx`：
   - 删除 TemplateScenes 的占位内容。
   - 为你的每个 scene slug 创建对应的 React 函数式组件（只渲染 SceneFrame 内部内容）。
4. 编辑 `src/data/lessons.tsx`：
   - 在 RENDERERS 映射表中把 slug 关联到你的场景组件。
5. 编辑 `src/Root.tsx`：注册新 CompositionId。
6. 运行验证：
   ```bash
   tsc --noEmit && vitest run    # 类型 + 守卫测试
   node scripts/gen-script.mjs   # 从数据生成 口播稿.md
   ```

### 重构现有工程到数据驱动

1. 在现有工程中创建 `src/timeline.ts`（复制参考实现）、`src/data/lesson-inputs.ts`（从现有场景提取纯数据）。
2. 提取各视频的 JSX 内容为 `src/lessons/*Scenes.tsx`（无帧逻辑，只做内容渲染）。
3. 创建 `src/shared/LessonVideo.tsx`（统一引擎）。
4. 创建薄包装 `src/lessons/*Video.tsx`。
5. 删除旧胖组件和 `VideoShell.tsx`。
6. 添加 3 组守卫测试（见下方）。
7. 运行 `tsc --noEmit && vitest run` 验证。

## 必须包含的文件清单

| 文件 | 作用 | 是否必须 |
|---|---|---|
| `src/timeline.ts` | 时间轴编译器（buildLesson） | ✅ 必须 |
| `src/data/lesson-inputs.ts` | 纯数据输入（单一数据源） | ✅ 必须 |
| `src/data/lessons.tsx` | 数据→带渲染函数的 spec 构建 | ✅ 必须 |
| `src/shared/LessonVideo.tsx` | 统一渲染引擎 | ✅ 必须 |
| `src/lessons/*Scenes.tsx` | 各讲专属场景组件 | ✅ 至少 1 个 |
| `src/lessons/*Video.tsx` | 薄包装（~4行） | ✅ 每个 Composition 1 个 |
| `scripts/gen-script.mjs` | 从数据自动生成口播稿 | ✅ 推荐 |
| `src/__tests__/timeline.test.ts` | 编译器单元测试（≥5 case） | ✅ 推荐 |
| `src/__tests__/source-guard.test.ts` | 源码守卫测试（4 条规则） | ✅ 推荐 |
| `src/__tests__/script-sync.test.ts` | 口播稿↔字幕逐条一致测试 | ✅ 推荐 |

## 守卫测试规范

每次创建或修改课时视频工程，以下 4 类守卫测试必须通过：

1. **禁止 CSS animation/transition**：递归扫描 src 下所有 .ts/.tsx 文件，不允许出现 CSS `animation:` 或 `transition:` 属性（Remotion 必须用帧驱动 interpolate 做动画）。
2. **Composition 注册正确性**：Root.tsx 恰好注册预期的 CompositionId 数量，无残留旧模板/旧课时引用。
3. **KaTeX 公式守卫**：任何含 LaTeX 标记（`\frac`、`^{` 等）的 .tsx 文件，必须使用 `<MathFormula>` 组件渲染公式。
4. **口播稿 ↔ 字幕逐条一致**：从 `lessonInputs` + `buildLesson` 编译出的每条 cue（id：text），必须在 `口播稿.md` 中逐条出现。

## 参考文档

- [references/timeline-compiler.md](references/timeline-compiler.md) — 时间轴编译器完整代码与设计说明
- [references/data-schema.md](references/data-schema.md) — 纯数据 schema（LessonInput / SceneInput / NarrationCue）
- [references/lesson-engine.md](references/lesson-engine.md) — 统一渲染引擎 + 薄包装 + 数据构建层完整代码
- [references/guard-tests.md](references/guard-tests.md) — 三组守卫测试完整代码与覆盖说明
- [references/scaffold.md](references/scaffold.md) — 如何从数学模板派生新工程的详细步骤

## 与 subject-videos 技能的关系

`subject-videos` 负责教学内容设计（分镜、口播稿写作、视觉系统）。`remotion-lesson-video` 负责工程架构（数据驱动、时间轴自校验、守卫测试）。两者互补：

- **先**按 `subject-videos` 设计教学内容和分镜；
- **再**按本技能的数据驱动架构实现工程；
- **最后**运行本技能的守卫测试确保质量。

## 版本记录

- v1.0 (2026-07-21)：基于 Codex 五讲重制版范式提炼，首次沉淀。已在 `4.2-指数函数` 工程中完成 Tier 1-3 升级并验证。
