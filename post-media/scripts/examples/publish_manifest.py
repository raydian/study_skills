#!/usr/bin/env python3
"""
post-media · 清单式批量上传

读取一个 JSON 清单，按条目调用 `sau` CLI 把视频 / 图文发布到 抖音 / 小红书 / Bilibili。
视频号(tencent)为实验性，本脚本不尝试自动发布，仅给出提示。

用法
----
    python3 publish_manifest.py manifest.json --dry-run     # 仅打印将要执行的命令
    python3 publish_manifest.py manifest.json --go          # 真正执行

环境变量
--------
    SAU_BIN        覆盖 `sau` 可执行文件（默认 "sau"；也可写 "uv run sau"）

清单格式 (manifest.json)
------------------------
{
  "defaults": { "headless": true },          # 可选，逐条可被覆盖
  "items": [
    {
      "platform": "douyin",                  # douyin | xiaohongshu | bilibili | tencent
      "account": "my_account",
      "type": "video",                       # video | note (douyin/xhs 支持 note；bilibili 仅 video)
      "file": "videos/a.mp4",                # type=video 必填
      "images": ["1.png", "2.png"],          # type=note 必填（douyin/xhs）
      "title": "标题",
      "desc": "视频简介 / B站简介",            # video 用
      "note": "图文正文",                      # note 用（douyin/xhs）
      "tags": ["标签1", "标签2"],
      "schedule": "2026-08-04 10:00",        # 可选，不填立即发布
      "thumbnail": "cover.png",              # 可选（douyin/xhs video）
      "tid": 249,                            # bilibili 必填分区码
      "headless": true                       # 可选，覆盖 defaults
    }
  ]
}

注意
----
- 每个 account 必须已 `sau <platform> login` 且 `check` 为 valid。
- Bilibili 强制 tid；抖音 / 小红书图文最多 35 张图且不支持 GIF。
- 视频号(tencent)不在本脚本自动执行范围内（核心交互未实现），遇到会跳过并提示。
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def build_command(item: dict, defaults: dict) -> list[str] | None:
    """根据条目构造 sau 命令列表；返回 None 表示跳过（如 tencent）。"""
    sau = os.environ.get("SAU_BIN", "sau").split()
    platform = item.get("platform", "")
    account = item.get("account", "")
    itype = item.get("type", "video")
    headless = item.get("headless", defaults.get("headless", False))

    title = item.get("title", "")
    tags = item.get("tags")
    tags_arg = ",".join(tags) if tags else None
    schedule = item.get("schedule")

    def opt(*pairs):
        out = []
        for flag, val in pairs:
            if val:
                out += [flag, str(val)]
        return out

    if platform in ("douyin", "xiaohongshu"):
        base = ["sau", platform] if sau == ["sau"] else sau + [platform]
        if itype == "note":
            images = item.get("images", [])
            if not images:
                raise ValueError(f"[{platform}] note 类型需要 images 字段")
            cmd = base + ["upload-note", "--account", account,
                          "--images", *images, "--title", title]
            cmd += opt(("--note", item.get("note")),
                       ("--tags", tags_arg),
                       ("--schedule", schedule))
            if headless:
                cmd.append("--headless")
            return cmd
        else:
            file = item.get("file", "")
            if not file:
                raise ValueError(f"[{platform}] video 类型需要 file 字段")
            cmd = base + ["upload-video", "--account", account,
                          "--file", file, "--title", title]
            cmd += opt(("--desc", item.get("desc")),
                       ("--tags", tags_arg),
                       ("--schedule", schedule),
                       ("--thumbnail", item.get("thumbnail")))
            if headless:
                cmd.append("--headless")
            return cmd

    elif platform == "bilibili":
        tid = item.get("tid")
        if not tid:
            raise ValueError("[bilibili] 必须提供 tid（分区码）")
        file = item.get("file", "")
        if not file:
            raise ValueError("[bilibili] 需要 file 字段")
        base = ["sau", "bilibili"] if sau == ["sau"] else sau + ["bilibili"]
        cmd = base + ["upload-video", "--account", account, "--file", file,
                      "--title", title, "--desc", item.get("desc", ""),
                      "--tid", str(tid)]
        cmd += opt(("--tags", tags_arg), ("--schedule", schedule))
        return cmd

    elif platform == "tencent":
        # 实验性：核心交互未实现，不自动执行
        return None

    raise ValueError(f"未知 platform: {platform}")


def main() -> int:
    ap = argparse.ArgumentParser(description="post-media 清单式批量上传")
    ap.add_argument("manifest", help="清单 JSON 路径")
    ap.add_argument("--dry-run", action="store_true", help="只打印命令不执行")
    ap.add_argument("--go", dest="go", action="store_true", help="真正执行上传")
    args = ap.parse_args()

    if not args.dry_run and not args.go:
        ap.error("必须指定 --dry-run 或 --go")

    data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    defaults = data.get("defaults", {})
    items = data.get("items", [])

    failures = 0
    for i, item in enumerate(items, 1):
        platform = item.get("platform", "?")
        try:
            cmd = build_command(item, defaults)
        except ValueError as e:
            print(f"[{i}] ✗ {platform}: 参数错误 - {e}")
            failures += 1
            continue

        if cmd is None:
            print(f"[{i}] ⊘ {platform}: 视频号(tencent)为实验性，核心交互未实现，"
                  f"跳过自动发布（见 scripts/examples/tencent_example.py）")
            continue

        print(f"[{i}] → {' '.join(cmd)}")
        if args.dry_run:
            continue

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                print(f"      ✗ 失败 (exit {proc.returncode})")
                print(proc.stdout)
                print(proc.stderr)
                failures += 1
            else:
                print("      ✓ 已提交")
        except FileNotFoundError:
            print("      ✗ 找不到 `sau` 命令，请先安装 social-auto-upload（见 runtime-requirements.md）")
            failures += 1

    print(f"\n完成：{len(items) - failures} 成功，{failures} 失败/跳过")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
