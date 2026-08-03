# 从数学模板派生新工程（Scaffold）

## 前置条件

- 已安装 `video/数学/数学视频模板/`（已升级为数据驱动范式）。
- `video/数学/node_modules/` 存在且包含 remotion/katex/d3 等依赖。

## 方法 A：使用 create_math_video.py 脚本

```bash
python3 scripts/create_math_video.py "5.1-对数函数" --composition-id ExpLogarithm
```

脚本会从模板复制目录、创建 node_modules 软链接、初始化 git。复制后按方法 B 的步骤 2-6 编辑内容。

## 方法 B：手动派生

### 步骤 1：复制模板

```bash
cd video/数学
cp -R 数学视频模板 新知识点工程名
# 或用 python3 scripts/create_math_video.py "新知识点" --composition-id ExpNewKey
```

确保新工程的 `node_modules` 是指向 `../node_modules` 的软链接（脚本自动处理）。

### 步骤 2：编辑纯数据 (`src/data/lesson-inputs.ts`)

把占位 `template` 改成你的课时 key，填写：

```typescript
const myLesson: LessonInput = {
  compositionId: 'ExpLogarithm',   // Root.tsx 注册的 ID
  lessonNumber: 1,
  title: '对数函数的概念',
  scope: '5.1 对数函数 · 第①讲',
  label: '高中数学 · 对数函数①',
  status: '核心精讲',
  cover: {
    subject: '高中数学',
    titleLines: ['对数函数的概念'],
    scope: '5.1 对数函数 · 第①讲',
    subtitle: '从指数反过来的问题出发。',
  },
  closing: { /* ... */ },
  targetFrames: 1680,              // = cover(150) + scenes总时长 + closing(210)
  scenes: [
    { slug: 'hook', kind: 'hook', title: '引入', duration: 420, cues: [...] },
    { slug: 'def', kind: 'concept', title: '定义', duration: 480, cues: [...] },
    // ... 按需添加场景
  ],
};

export const lessonInputs = { myLesson };
```

**关键**：targetFrames 必须等于 cover + Σscenes.duration + closing，否则 buildLesson 抛错。

### 步骤 3：编写场景组件 (`src/lessons/*Scenes.tsx`)

删除 TemplateScenes.tsx，为每个 scene slug 创建对应的组件：

```tsx
// src/lessons/MyLessonScenes.tsx
export const MyLessonScenes = {
  HookScene: () => (
    // 只写 SceneFrame 内部的教学内容
    <div style={{...}}>你的钩子内容</div>
  ),
  DefScene: () => (
    <div style={{...}}>
      定义内容...
      <MathFormula latex="y = \log_a x" />
    </div>
  ),
};
```

**约定**：引擎已提供 Background / CourseChrome / SceneFrame / Subtitle，这里只写画面内部的教学内容。

### 步骤 4：更新数据构建层 (`src/data/lessons.tsx`)

在 RENDERERS 映射表中注册：

```typescript
import {MyLessonScenes} from '../lessons/MyLessonScenes';

const RENDERERS: Record<string, React.FC> = {
  'hook': MyLessonScenes.HookScene,
  'def': MyLessonScenes.DefScene,
};
```

### 步骤 5：更新 Root 和薄包装

```tsx
// src/lessons/MyLessonVideo.tsx
export const MyLessonVideo = () => <LessonVideo lesson={lessons.myLesson} />;

// src/Root.tsx — 注册新 Composition
<Composition id="ExpLogarithm" component={MyLessonVideo}
  durationInFrames={lessons.myLesson.durationInFrames} ... />
```

### 步骤 6：验证

```bash
tsc --noEmit          # 类型检查
vitest run            # 守卫测试（应全部通过）
node scripts/gen-script.mjs  # 生成口播稿.md
npx remotion still ExpLogarithm output/test.png 0  # 渲染一帧确认
```

## 多课时工程

如果一节知识点拆成多个视频（如 Codex 五讲重制版），只需：

1. 在 `lesson-inputs.ts` 中导出多组 LessonInput。
2. 为每组创建 *Scenes.tsx + *Video.tsx。
3. 在 `lessons.tsx` 中注册所有 slug→renderer 映射。
4. 在 `Root.tsx` 中注册所有 Composition。

## 关于物理模板

物理模板 (`video/物理/物理视频模板/`) 使用不同的 CompositionId 共享依赖结构。将此数据驱动范式应用到物理需要单独的迁移工作：
- 物理模板的 CoverPage/ClosingPage 组件签名可能不同；
- 共享 node_modules 路径不同（`../node_modules` vs `../../node_modules`）；
- 需要保留物理特有的 Graphite Blue 配色和字体。

建议：先在数学模板上验证范式稳定后，再迁移到物理模板。
