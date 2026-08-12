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
COMMENT_LINE_RE = re.compile(r"^<!-- 图片描述：(.+) -->$")
BIOLOGY_COMMENT_PREFIX_RE = re.compile(
    r"^<!-- 图片描述：(教材.+(?:源图重绘|源图组重绘)|补充知识图（非教材原图）(?:——|；))"
)
WIKILINK_RE = re.compile(r"\[\[[^\]]+\]\]")
WIKILINK_TARGET_RE = re.compile(r"\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|[^\]]+)?\]\]")
FIGURE_NUMBER_RE = re.compile(r"图\s*(\d+\s*[-－—]\s*\d+)")


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
    if re.search(r"(?m)^draft\s*:\s*(true|false)\s*$", frontmatter) is None:
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


def image_errors(
    path: Path, text: str, stage: str, subject: str | None
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    lines = text.splitlines()
    comments = list(COMMENT_RE.finditer(text))
    image_matches = list(IMAGE_RE.finditer(text))

    raw_comment_starts = text.count("<!-- 图片描述：")
    if raw_comment_starts != len(comments):
        errors.append(
            f"{path}: malformed/unclosed 图片描述 comment "
            f"({raw_comment_starts} start(s), {len(comments)} complete comment(s))"
        )

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

    for index, line in enumerate(lines):
        if "<!-- 图片描述：" not in line:
            continue
        line_number = index + 1
        if not COMMENT_LINE_RE.fullmatch(line):
            errors.append(f"{path}:{line_number}: 图片描述 must be one complete single-line comment")
        if index > 0 and lines[index - 1].strip():
            errors.append(f"{path}:{line_number}: 图片描述 must have a blank line before it")
        if index + 1 < len(lines) and lines[index + 1].strip():
            errors.append(f"{path}:{line_number}: 图片描述 must have a blank line after it")
        if subject == "生物" and not BIOLOGY_COMMENT_PREFIX_RE.match(line):
            errors.append(
                f"{path}:{line_number}: biology 图片描述 must start with "
                "教材…源图重绘/教材…源图组重绘 or 补充知识图（非教材原图）"
            )

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


def heading_errors(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    positions: list[int] = []
    for heading in REQUIRED_HEADINGS:
        match = re.search(rf"(?m)^## {re.escape(heading)}\s*$", text)
        if match is None:
            errors.append(f"{path}: missing ## {heading}")
        else:
            positions.append(match.start())
    if len(positions) == len(REQUIRED_HEADINGS) and positions != sorted(positions):
        errors.append(f"{path}: required headings are out of order")
    return errors


def validate_note(
    path: Path, stage: str, subject: str | None
) -> tuple[list[str], list[str]]:
    text = path.read_text(encoding="utf-8")
    errors = frontmatter_errors(text, path)
    warnings: list[str] = []

    if not re.search(r"(?m)^#\s+.+", text):
        errors.append(f"{path}: missing H1 title")
    if "## 知识关系导航" not in text:
        errors.append(f"{path}: missing ## 知识关系导航")
    if not WIKILINK_RE.search(text):
        errors.append(f"{path}: no Wikilink")
    errors.extend(heading_errors(path, text))

    image_error_list, image_warning_list = image_errors(path, text, stage, subject)
    errors.extend(image_error_list)
    warnings.extend(image_warning_list)
    return errors, warnings


def validate_moc(
    path: Path, stage: str, subject: str | None
) -> tuple[list[str], list[str]]:
    text = path.read_text(encoding="utf-8")
    errors = frontmatter_errors(text, path)
    warnings: list[str] = []
    if not re.search(r"(?m)^#\s+.+", text):
        errors.append(f"{path}: missing H1 title")
    if not WIKILINK_RE.search(text):
        errors.append(f"{path}: no Wikilink")
    image_error_list, image_warning_list = image_errors(path, text, stage, subject)
    errors.extend(image_error_list)
    warnings.extend(image_warning_list)
    return errors, warnings


def wikilink_errors(chapter_dir: Path, markdown_files: list[Path]) -> list[str]:
    errors: list[str] = []
    targets = {path.stem: path for path in markdown_files}
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        for target_name, anchor in WIKILINK_TARGET_RE.findall(text):
            target = targets.get(Path(target_name).name)
            if target is None:
                errors.append(f"{path}: dangling Wikilink target: {target_name}")
                continue
            if anchor:
                target_text = target.read_text(encoding="utf-8")
                if not re.search(rf"(?m)^#{{1,6}} {re.escape(anchor)}\s*$", target_text):
                    errors.append(f"{path}: missing Wikilink anchor: {target_name}#{anchor}")
    return errors


def source_figure_errors(source: Path, markdown_files: list[Path]) -> list[str]:
    errors: list[str] = []
    source_text = source.read_text(encoding="utf-8")
    output_text = "\n".join(path.read_text(encoding="utf-8") for path in markdown_files)
    source_figures = {
        re.sub(r"\s+", "", number) for number in FIGURE_NUMBER_RE.findall(source_text)
    }
    output_figures = {
        re.sub(r"\s+", "", number) for number in FIGURE_NUMBER_RE.findall(output_text)
    }
    for number in sorted(source_figures - output_figures):
        errors.append(f"{source}: source figure 图{number} has no traceable output annotation")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chapter_dir", type=Path, help="chapter-notes output directory")
    parser.add_argument(
        "--stage",
        choices=("comments", "images"),
        default="comments",
        help="comments checks the note-generation pass; images checks inserted files too",
    )
    parser.add_argument(
        "--subject",
        choices=("语文", "数学", "英语", "物理", "化学", "生物", "历史", "地理"),
        help="enable subject-specific validation rules",
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="source chapter Markdown; validates traceable numbered source figures",
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

    if moc.is_file():
        moc_errors, moc_warnings = validate_moc(moc, args.stage, args.subject)
        errors.extend(moc_errors)
        warnings.extend(moc_warnings)

    for path in markdown_files:
        if path.name == moc.name:
            continue
        note_errors, note_warnings = validate_note(path, args.stage, args.subject)
        errors.extend(note_errors)
        warnings.extend(note_warnings)

    errors.extend(wikilink_errors(chapter_dir, markdown_files))
    if args.source:
        if not args.source.is_file():
            errors.append(f"source Markdown does not exist: {args.source}")
        else:
            errors.extend(source_figure_errors(args.source, markdown_files))

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
