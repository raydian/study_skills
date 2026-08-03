# 守卫测试（Guard Tests）

三组测试构成 Remotion 课时视频的**质量守门线**。每次修改工程后运行 `vitest run` 确保全部通过。

## 测试文件清单

| 文件 | 测试数 | 覆盖范围 |
|---|---|---|
| `src/__tests__/timeline.test.ts` | ≥5 | buildLesson 编译器正确性 |
| `src/__tests__/source-guard.test.ts` | 4 | 源码硬性规范 |
| `src/__tests__/script-sync.test.ts` | N+1 (N=cue总数) | 口播稿↔字幕逐条一致 |

---

## 1. source-guard.test.ts — 源码硬性规范

### 测试 A：禁止 CSS animation / transition

```typescript
it('禁止 CSS 拥有的 animation / transition', () => {
  // 递归收集 src 下所有 .ts/.tsx
  for (const f of SRC_FILES) {
    const src = read(f);
    expect(src, `${f} 含 CSS animation`).not.toMatch(/animation\s*:/);
    expect(src, `${f} 含 CSS transition`).not.toMatch(/transition\s*:/);
  }
});
```

**为什么重要**：Remotion 是帧驱动渲染引擎，CSS `animation`/`transition` 在逐帧渲染下结果不确定——同一帧可能渲染出不同状态。所有动画必须用 `interpolate()` / `<Sequence>` 驱动。

### 测试 B：Composition 注册正确性

```typescript
it('Root.tsx 注册的 Composition 正确且无残留', () => {
  const root = read('../Root.tsx');
  for (const id of ['ExpConcept', 'ExpApplication']) { /* 你的 composition IDs */
    expect(root.split(id)).toHaveLength(2); // import + usage
  }
  expect(root).not.toContain('TemplateVideo');   // 无旧模板残留
});
```

### 测试 C：口播稿/分镜文档存在

```typescript
it('口播稿 / 分镜文档存在且非空', () => {
  expect(script.trim().length).toBeGreaterThan(200);
  expect(script).toContain('ExpConcept');
});
```

### 测试 D：KaTeX 公式守卫

```typescript
it('公式必须走 KaTeX 组件', () => {
  const latexToken = /\\(frac|sqrt|sum|int|...|\^\s*\{|_\s*\{/;
  for (const f of tsxFiles) {
    if (latexToken.test(src))
      expect(src).toContain('<MathFormula');  // 必须用组件渲染公式
  }
});
```

---

## 2. script-sync.test.ts — 口播稿 ↔ 字幕逐条一致

```typescript
import { lessonInputs } from '../data/lesson-inputs';
import { buildLesson } from '../timeline';

const script = readFileSync(join(ROOT, '口播稿.md'), 'utf8');

describe('口播稿 ↔ 字幕 cue 逐条一致', () => {
  for (const key of Object.keys(lessonInputs) as (keyof typeof lessonInputs)[]) {
    const spec = buildLesson(lessonInputs[key]);
    describe(`视频 ${key}`, () => {
      for (const cue of spec.cues) {
        it(`cue ${cue.id} 与口播稿一致`, () => {
          expect(script).toContain(`${cue.id}：${cue.text}`);
        });
      }
    });
  }

  it('口播稿条数等于 cue 总条数', () => {
    const total = keys.reduce((n, k) =>
      n + buildLesson(lessonInputs[k]).cues.length, 0);
    const docCount = (script.match(/^[\w-]+：/gm) || []).length;
    expect(docCount).toBe(total);
  });
});
```

**设计意图**：口播稿由 `gen-script.mjs` 从 `lesson-inputs.ts` 自动生成，是单一数据源的"人类可读视图"。此测试确保两者永远同步——如果有人手动编辑了口播稿文本而没更新数据（或反过来），测试立刻报错。

---

## 3. timeline.test.ts — 编译器单元测试

关键测试用例：

- **基本编译**：1 个场景 → from=coverFrames, cues 有正确 start/end。
- **多场景累加**：3 个场景 → 第 2 场景 from = cover + scene1.duration。
- **cue 均分**：场景有 3 条 cue → 每条有合理时长，首尾有 padding。
- **总帧校验通过**：targetFrames = Σduration → 不抛错。
- **总帧校验失败**：targetFrames ≠ Σduration → 抛出 Error。
