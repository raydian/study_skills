#!/usr/bin/env python3
"""Scan Markdown files for image comments and nearby inserted images."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

COMMENT_RE = re.compile(r"<!--\s*图片描述[:：](.*?)-->", re.S)
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def markdown_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(p for p in path.rglob("*.md") if p.is_file())


def has_image_immediately_above(text: str, start: int) -> bool:
    before = text[:start].rstrip().splitlines()
    if not before:
        return False
    return bool(IMAGE_RE.search(before[-1]))


def scan_file(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    rows = []
    for idx, match in enumerate(COMMENT_RE.finditer(text), start=1):
        line = text.count("\n", 0, match.start()) + 1
        prompt = " ".join(match.group(1).split())
        rows.append(
            {
                "file": str(path),
                "index": idx,
                "line": line,
                "has_image_above": has_image_immediately_above(text, match.start()),
                "prompt": prompt,
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    rows = []
    for md in markdown_files(args.path):
        rows.extend(scan_file(md))

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for row in rows:
            status = "done" if row["has_image_above"] else "todo"
            print(f'{row["file"]}:{row["line"]}: 图{row["index"]:02d} [{status}] {row["prompt"][:100]}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
