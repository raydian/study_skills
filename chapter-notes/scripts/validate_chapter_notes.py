#!/usr/bin/env python3
"""Validate a chapter-notes output directory.

The validator intentionally supports the two-pass workflow described by the
skill:

* comments: notes must contain source-aware image descriptions; image files
  may not exist yet;
* images: every image description must have an image immediately above it,
  and every referenced file must exist.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_HEADINGS = (
    "本节学习目标",
    "核心知识点讲解",
    "重点梳理",
    "难点突破",
    "例题讲解",
    "易错点整理",
    "考点考证点整理",
    "练习题",
    "练习题答案",
)
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
COMMENT_RE = re.compile(r"<!--\s*图片描述：.*?-->", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[[^\]]+\]\]")


def frontmatter_errors(text: str, path: Path) -> list[str]:
    errors: list[str] = []
    if not text.startswith("---\n"):
        return [f"{path}: missing YAML frontmatter"]
    end = text.find("\n---", 4)
    if end < 0:
        return [f"{path}: unterminated YAML frontmatter"]
    frontmatter = text[4:end]
    for key in ("title", "description", "aliases", "tags", "draft"):
        if not re.search(rf"(?m)^{re.escape(key)}\s*:", frontmatter):
            errors.append(f"{path}: missing frontmatter field {key}")
    if re.search(r"(?m)^draft\s*:\s*['\"]?(true|false)['\"]?\s*$", frontmatter) is None:
        errors.append(f"{path}: draft must be a YAML boolean")
    knowledge_tags = re.findall(r"(?m)^\s*-\s*[\"']?知识点/[^\n\"']+", frontmatter)
    if len(knowledge_tags) < 2:
        errors.append(f"{path}: fewer than two 知识点/ tags")
    return errors


def image_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    return target


def image_errors(path: Path, text: str, stage: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    lines = text.splitlines()
    comments = list(COMMENT_RE.finditer(text))
    image_matches = list(IMAGE_RE.finditer(text))

    if not comments:
        errors.append(f"{path}: no 图片描述 comment")
    if stage == "images" and len(image_matches) != len(comments):
        errors.append(
            f"{path}: image/comment count mismatch ({len(image_matches)} images, {len(comments)} comments)"
        )

    for match in image_matches:
        target = image_target(match.group(1))
        if " " in target:
            errors.append(f"{path}: image path contains spaces: {target}")
        if stage == "images":
            image_path = (path.parent / target).resolve()
            if not image_path.is_file():
                errors.append(f"{path}: missing image file: {target}")
            elif image_path.stat().st_size > 1_000_000:
                warnings.append(f"{path}: image exceeds 1 MB: {target}")

    # A generated image must be directly associated with the following
    # comment. Blank lines are allowed for readable Markdown formatting.
    if stage == "images":
        for index, line in enumerate(lines):
            if not IMAGE_RE.search(line):
                continue
            next_index = index + 1
            while next_index < len(lines) and not lines[next_index].strip():
                next_index += 1
            if next_index >= len(lines) or "<!-- 图片描述：" not in lines[next_index]:
                errors.append(f"{path}: image is not immediately above a 图片描述 comment")

    return errors, warnings


def validate_note(path: Path, stage: str) -> tuple[list[str], list[str]]:
    text = path.read_text(encoding="utf-8")
    errors = frontmatter_errors(text, path)
    warnings: list[str] = []

    if not re.search(r"(?m)^#\s+.+", text):
        errors.append(f"{path}: missing H1 title")
    if "## 知识关系导航" not in text:
        errors.append(f"{path}: missing ## 知识关系导航")
    if not WIKILINK_RE.search(text):
        errors.append(f"{path}: no Wikilink")
    for heading in REQUIRED_HEADINGS:
        if f"## {heading}" not in text:
            errors.append(f"{path}: missing ## {heading}")

    image_error_list, image_warning_list = image_errors(path, text, stage)
    errors.extend(image_error_list)
    warnings.extend(image_warning_list)
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chapter_dir", type=Path, help="chapter-notes output directory")
    parser.add_argument(
        "--stage",
        choices=("comments", "images"),
        default="comments",
        help="comments checks the note-generation pass; images checks inserted files too",
    )
    args = parser.parse_args()
    chapter_dir = args.chapter_dir
    if not chapter_dir.is_dir():
        print(f"ERROR: not a directory: {chapter_dir}", file=sys.stderr)
        return 2

    markdown_files = sorted(chapter_dir.glob("*.md"))
    if not markdown_files:
        print(f"ERROR: no Markdown files in {chapter_dir}", file=sys.stderr)
        return 2
    moc = chapter_dir / "章首 学习导图.md"
    errors: list[str] = []
    warnings: list[str] = []
    if not moc.is_file():
        errors.append(f"{chapter_dir}: missing 章首 学习导图.md")

    for path in markdown_files:
        if path.name == moc.name:
            continue
        note_errors, note_warnings = validate_note(path, args.stage)
        errors.extend(note_errors)
        warnings.extend(note_warnings)

    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1

    print(
        f"PASS: {len(markdown_files) - 1} subchapter note(s) and chapter MOC "
        f"validated in {chapter_dir} [{args.stage}]"
    )
    if warnings:
        print(f"{len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
