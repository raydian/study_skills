# Content Design

Do not directly turn the source file into narration. Treat the source as material for instructional design.

## Required Before Writing Script

Create a knowledge analysis section in `content-design.md` before `口播稿.md` is finalized:

```markdown
## 知识点分析

## 学生难点与误区

## 视频讲解主线

## 场景结构设计

## 动效与组件设计

## 素材使用计划
```

## Analysis Checklist

For each knowledge point, identify:

- core concept: what must be understood;
- prerequisite knowledge: what students need before this video;
- key definitions, formulas, models, events, mechanisms, maps, or evidence;
- conceptual obstacles: what students usually misunderstand;
- method path: how to judge, calculate, prove, analyze, or answer;
- example path: which example best reveals the method;
- exercise use: which exercise should appear, and whether to solve fully or only prompt;
- visual logic: what must be shown as a structure, process, relationship, proof, experiment, map, timeline, microscopic view, or real-world mechanism.

## Physics Analysis Extension

For `学科=物理`, use `physics-video-structure.md` and record all of the following before finalizing the storyboard:

- primary route and optional secondary route;
- one core question and one core model/law;
- prerequisite knowledge and model assumptions;
- at most two core assessment points, including question signals and scoring actions;
- one primary conceptual difficulty and why the incorrect intuition feels plausible;
- related error points, misconceptions, conflict evidence, and correction cues;
- mother-problem source, selection reason, complete model path, and result checks;
- one single-condition variation and whether the original model remains valid;
- scene-to-scene object, conclusion, and visual-continuity plan.

## Video Structure Design

Design the video as a teaching journey, not a source-file order replay. A typical structure is usually 2-15 minutes, but the duration should be determined by the actual content rather than a fixed range. Design the scene lengths so that each scene has corresponding narration and visual explanation; avoid long停留空白 where nothing is being taught.

The following list is a menu of common teaching stages, not ten required scenes, ten pages, or a one-stage-one-component template. Split, merge, reorder, or omit stages according to subject, source, learning goal, evidence load, and narration. For `学科=语文`, use `chinese-video-structure.md`: its seven modules are also teaching stages and must be decomposed into concrete article-specific scenes.

1. 封面开场：用短暂的未开始/即将开始状态建立主题和课程感，不直接在第一帧进入讲解。
2. 问题引入：用一个真实问题、题目、现象或冲突引出学习目标。
3. 总览结构：重建本知识点的视频化结构图，让学生知道接下来学什么。
4. 概念建立：从直观例子到正式定义。
5. 方法拆解：把判断、计算、证明或分析过程拆成步骤。
6. 典型例题：完整展示审题、转化、解答和检查。
7. 易错对比：展示一个常见错误和正确修正。
8. 练习停顿：给学生 3-8 秒思考，再点拨。
9. 复盘总结：回到结构图，串起本节结论。
10. 结束收尾：用独立结束页总结整条学习路径和最后的可迁移方法。

## Scene Design

For each scene, decide:

- teaching purpose;
- what appears on screen;
- what changes over time;
- what the student should think about;
- which component or diagram type expresses it best;
- what pause is needed before the teacher continues.

Do not leave long停留空白 without narration or visual animation. The pace should be determined by what is being taught, not by a pre-set duration.

Do not show long paragraphs of source text on screen. Convert paragraphs into diagrams, boards, timelines, maps, formulas, tables, or guided examples.

If the source includes an information structure image, do not paste it into the video as the default solution. Extract its structure and rebuild it as animated, editable video elements. Direct image placement is reserved for real visual evidence, scene illustrations, artworks, maps, experiment images, or other visuals that students should inspect directly.

## Visual Effect Design

Effects must teach:

- reveal hierarchy step by step;
- highlight current object or condition;
- animate arrows to show process or causality;
- move from real-world phenomenon to abstract model;
- zoom from macro view to micro view when useful;
- show wrong path versus correct path;
- synchronize board writing with teacher explanation.

Avoid effects that only decorate, spin, bounce, or distract.

## Source Material Use

Use source text, images, and exercises selectively:

- source text provides knowledge accuracy;
- images become visual evidence or diagram material;
- exercises become thinking checkpoints or worked examples;
- examples can be reordered if it improves teaching.

If a source section is long, reorganize it around student understanding rather than original order.
