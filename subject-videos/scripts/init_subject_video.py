#!/usr/bin/env python3
"""Create a subject-video project directory with starter planning files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def slugify(text: str) -> str:
    text = text.strip().replace(" ", "-")
    text = re.sub(r"[\\/：:*?\"<>|]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "knowledge-video"


def write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def content_design_template(subject: str, knowledge_name: str, source_line: str) -> str:
    if subject != "物理":
        return f"""# {knowledge_name} 知识点分析与视频设计
{source_line}

## 知识点分析

## 学生难点与误区

## 视频讲解主线

## 场景结构设计

## 动效与组件设计

## 素材使用计划

"""

    return f"""# {knowledge_name} 物理知识点分析与视频设计
{source_line}

> 按 `physics-video-structure.md` 完成首次理解、考点、难点、纠错、母题和变式闭环。

## 视频类型路由

- 主类型：概念规律型 / 实验探究型 / 计算方法型 / 现象机制型
- 副类型：无 / 选择一个支持同一学习目标的类型

## 核心问题与物理模型

## 前置知识与建模条件

## 核心考核重点

## 难点分析

## 易错点与认知误区

## 典型母题

- 来源：教材 / 课后习题 / 考试原型 / 本课设计母题
- 选择理由：
- 完整路径：读题 → 识型 → 画图 → 建模 → 选规律 → 列式 → 求解 → 检查

## 单条件变式

## 场景连续性设计

## 动效与物理组件设计

## 素材使用计划

## 物理准确性检查

"""


def storyboard_template(subject: str, knowledge_name: str, source_line: str) -> str:
    if subject != "物理":
        return f"""# {knowledge_name} Remotion 分镜

- 规格：1920x1080，30fps，2-15 分钟，静音视频。时长应根据实际内容调整，不要为凑时长而硬拉。
- 版本：核心精讲版。
{source_line}

| 时间段 | 画面目标 | 口播对应 | 组件/素材 |
|---|---|---|---|
"""

    return f"""# {knowledge_name} 物理知识点 Remotion 分镜

- 规格：1920x1080，30fps，建议 6-10 分钟，静音视频。实际时长由教学内容决定。
- 主线：现象 → 建模 → 规律 → 考点 → 难点 → 易错纠偏 → 母题 → 变式 → 复盘。
{source_line}

| 时间段 | 场景 ID | 所属阶段/类型 | 教学目的 | 核心问题 | 继承对象/结论 | 本场画面与物理状态 | 考点/难点/易错点 | 口播对应 | 下一场桥接 | 组件/素材 |
|---|---|---|---|---|---|---|---|---|---|---|
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("subject", help="学科，如 数学/物理/化学")
    parser.add_argument("knowledge_name", help="知识点或源文件名")
    parser.add_argument("--root", default="video", help="video root directory")
    parser.add_argument("--source", help="optional source note path")
    args = parser.parse_args()

    project = Path(args.root) / args.subject / slugify(args.knowledge_name)
    (project / "src" / "scenes").mkdir(parents=True, exist_ok=True)
    (project / "src" / "components").mkdir(parents=True, exist_ok=True)
    (project / "src" / "data").mkdir(parents=True, exist_ok=True)
    (project / "public" / "images").mkdir(parents=True, exist_ok=True)
    (project / "renders").mkdir(parents=True, exist_ok=True)

    source_line = f"\n源文件：`{args.source}`\n" if args.source else ""
    write_if_missing(
        project / "content-design.md",
        content_design_template(args.subject, args.knowledge_name, source_line),
    )
    write_if_missing(
        project / "口播稿.md",
        f"# {args.knowledge_name} 核心精讲版口播稿\n{source_line}\n> 先完成 `content-design.md` 和 `storyboard.md`，再写口播稿。不要直接朗读源文件。\n\n## 讲解目标\n\n## 口播稿\n\n（开场停顿 2 秒）\n\n",
    )
    write_if_missing(
        project / "storyboard.md",
        storyboard_template(args.subject, args.knowledge_name, source_line),
    )
    write_if_missing(
        project / "source.md",
        f"# Source\n{source_line}\n在这里记录源知识点文件摘要、图片素材、习题和引用路径。\n",
    )
    print(project)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
