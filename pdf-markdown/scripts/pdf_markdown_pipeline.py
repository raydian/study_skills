#!/usr/bin/env python3
"""PDF → Markdown pipeline (MinerU 4.x).

Three dependent stages, per study_skills/pdf-markdown/references/pdf-markdown-contract.md:

    convert : PDF -> MinerU raw markdown + images/ + mineru/ JSON + conversion-manifest.json
    format  : raw markdown -> formatted markdown (page traceability, de-duplicated chrome)
    split   : formatted markdown -> 拆分/章节/ + 拆分/单元/ + README
    validate: check artifacts, page records, image links, split coverage

MinerU 4.x no longer accepts `mineru -p ... -o ... -b pipeline -l ch`.
The classic markdown+images+JSON bundle is produced by `mineru-kit parse --format zip`,
which yields markdown.md, images/ and structured_content.json / middle_json.json / model_output.json.

Only the standard library is required.

Usage:
    python pdf_markdown_pipeline.py run --pdf book.pdf --out-root markdown/参考资料
    python pdf_markdown_pipeline.py convert --pdf book.pdf --out-root markdown/参考资料
    python pdf_markdown_pipeline.py import-mineru --bundle book.zip --pdf book.pdf --out-root markdown/参考资料
    python pdf_markdown_pipeline.py format --dir "markdown/参考资料/book"
    python pdf_markdown_pipeline.py split  --dir "markdown/参考资料/book"
    python pdf_markdown_pipeline.py validate --dir "markdown/参考资料/book"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SCHEMA_VERSION = 2
DEFAULT_MINERU_KIT = os.path.expanduser("~/mineru_env/bin/mineru-kit")
DEFAULT_TIER = "standard"
PAGE_MARK_FMT = "<!-- 来源页：{n} -->"
# MinerU 会把这类区块单独导出成图片文件
VISUAL_BLOCK_TYPES = {"image", "equation", "table", "chart", "algorithm"}

# ---------------------------------------------------------------- utilities


def ensure_dir(path: Path) -> Path:
    """mkdir -p，但已存在时完全不调用 mkdir（沙箱代理对已存在目录会抛 EEXIST）。"""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def find_mineru_kit(explicit: str | None) -> str:
    order = [
        explicit,
        os.environ.get("MINERU_KIT_BIN"),
        DEFAULT_MINERU_KIT,
        shutil.which("mineru-kit"),
        shutil.which("mineru"),
    ]
    for cand in order:
        if cand and Path(cand).exists():
            return str(cand)
    raise SystemExit(
        "MinerU 未找到。请用 --mineru-kit-bin 指定，或设置 MINERU_KIT_BIN，"
        "或安装 mineru 并确保 mineru-kit 在 PATH 中。"
    )


def image_size(path: Path) -> tuple[int | None, int | None]:
    """Minimal JPEG / PNG / WebP header size reader (no third-party deps)."""
    try:
        data = path.read_bytes()[:65536]
    except OSError:
        return (None, None)
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", data[16:24])
        return (w, h)
    if data[:2] == b"\xff\xd8":
        idx = 2
        while idx + 9 < len(data):
            if data[idx] != 0xFF:
                idx += 1
                continue
            marker = data[idx + 1]
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                idx += 2
                continue
            seg_len = struct.unpack(">H", data[idx + 2 : idx + 4])[0]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB):
                h, w = struct.unpack(">HH", data[idx + 5 : idx + 9])
                return (w, h)
            idx += 2 + seg_len
        return (None, None)
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        if data[12:16] == b"VP8X":
            w = int.from_bytes(data[24:27], "little") + 1
            h = int.from_bytes(data[27:30], "little") + 1
            return (w, h)
        return (None, None)
    return (None, None)


def norm_text(value: str) -> str:
    return re.sub(r"\s+", "", value or "")


# ---------------------------------------------------------------- import


def find_payload_dir(root: Path) -> Path:
    """Locate the directory that holds markdown.md / structured JSON / images."""
    if (root / "markdown.md").exists():
        return root
    for child in sorted(root.iterdir()):
        if child.is_dir() and (child / "markdown.md").exists():
            return child
    raise SystemExit(f"未在 {root} 下找到 MinerU 产物（markdown.md）")


def import_payload(payload: Path, pdf: Path, out_dir: Path, engine: str,
                   backend: str, command: list[str], source: str,
                   extra_warnings: list[str]) -> dict:
    out_dir = ensure_dir(out_dir)
    images_dir = ensure_dir(out_dir / "images")
    mineru_dir = ensure_dir(out_dir / "mineru")

    stem = pdf.stem
    raw_md = out_dir / f"{stem}.md"
    shutil.copy2(payload / "markdown.md", raw_md)

    # images
    copied: list[Path] = []
    src_images = payload / "images"
    if src_images.is_dir():
        for item in sorted(src_images.iterdir()):
            if item.is_file():
                target = images_dir / item.name
                shutil.copy2(item, target)
                copied.append(target)

    # structured artifacts
    artifacts: list[str] = []
    for name in ("structured_content.json", "middle_json.json", "model_output.json"):
        src = payload / name
        if src.exists():
            shutil.copy2(src, mineru_dir / name)
            artifacts.append(f"mineru/{name}")
    shutil.copy2(payload / "markdown.md", mineru_dir / f"{stem}.md")
    artifacts.append(f"mineru/{stem}.md")

    structured = mineru_dir / "structured_content.json"
    pages, page_warnings = collect_pages(structured, copied, raw_md)
    extra_warnings.extend(page_warnings)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "engine": engine,
        "backend": backend,
        "command": command,
        "source_pdf": str(pdf.resolve()),
        "source_sha256": sha256_file(pdf),
        "source_kind": "reference",
        "page_count": len(pages),
        "model_source": source,
        "stages": {"raw": raw_md.name, "formatted": f"{stem}-格式化.md", "split": []},
        "mineru": {
            "version": mineru_version(),
            "language": "ch",
            "source_markdown": f"mineru/{stem}.md",
            "artifacts": artifacts,
        },
        "pages": pages,
        "images": collect_images(copied, pages, raw_md),
        "raw_validation": validate_links(raw_md, out_dir),
        "warnings": extra_warnings,
        "formatted_validation": {},
        "split_validation": {},
    }
    (out_dir / "conversion-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest


def mineru_version() -> str:
    try:
        out = subprocess.run(["mineru-kit", "version"], capture_output=True, text=True, timeout=60)
        return out.stdout.strip().splitlines()[0] if out.stdout.strip() else "unknown"
    except Exception:
        return "unknown"


def block_texts(page: dict) -> list[str]:
    out: list[str] = []
    for block in page.get("blocks", []):
        content = block.get("content")
        if isinstance(content, str):
            out.append(content)
        elif isinstance(content, list):
            for child in content:
                if isinstance(child, dict):
                    sub = child.get("content")
                    if isinstance(sub, str) and sub.strip():
                        out.append(sub)
                    elif isinstance(sub, list):
                        for leaf in sub:
                            if isinstance(leaf, dict) and isinstance(leaf.get("content"), str):
                                out.append(leaf["content"])
                            elif isinstance(leaf, str):
                                out.append(leaf)
    return out


def collect_pages(structured: Path, images: list[Path], raw_md: Path) -> tuple[list[dict], list[str]]:
    warnings: list[str] = []
    if not structured.exists():
        warnings.append("MinerU structured_content.json 缺失，页面记录为空，需人工复核。")
        return ([], warnings)
    data = json.loads(structured.read_text(encoding="utf-8"))
    pages: list[dict] = []
    for page in data.get("pages", []):
        blocks = page.get("blocks", [])
        texts = block_texts(page)
        visual = [b for b in blocks if b.get("type") in VISUAL_BLOCK_TYPES]
        pages.append({
            "page": int(page.get("page_idx", 0)) + 1,
            "text_chars": sum(len(t) for t in texts),
            "used_ocr": True,
            "ocr_language": "ch",
            "blocks": len(blocks),
            "visual_blocks": len(visual),
            "warnings": [],
            "image_paths": [],
        })
    return pages, warnings


def collect_images(images: list[Path], pages: list[dict], raw_md: Path) -> list[dict]:
    md = raw_md.read_text(encoding="utf-8")
    records: list[dict] = []
    by_hash: dict[str, str] = {}
    for path in images:
        rel = f"images/{path.name}"
        digest = sha256_file(path)
        width, height = image_size(path)
        duplicate_of = by_hash.get(digest)
        if duplicate_of is None:
            by_hash[digest] = rel
        page_no = None
        # 文件名为 `page_<0 基页码>_<kind>_<区块序号><后缀>.jpg`，页码需 +1 转为 PDF 页
        match = re.match(r"page_(\d+)_([a-z_]+?)_?(\d+)", path.name)
        if match:
            page_no = int(match.group(1)) + 1
            kind = match.group(2).rstrip("_") or "figure"
        else:
            kind = "figure"
        referenced = rel in md
        reason = None
        if duplicate_of:
            reason = f"duplicate_of:{duplicate_of}"
        elif not referenced:
            if kind.startswith("equation"):
                reason = "公式已在原始稿以 LaTeX 表达，此图片为同内容冗余导出"
            elif kind.startswith("table"):
                reason = "表格已在原始稿以 HTML 表格表达，此图片为同内容冗余导出"
            else:
                reason = "未在原始稿中被引用，需人工复核"
        records.append({
            "path": rel,
            "page": page_no,
            "bbox": [],
            "kind": kind,
            "width": width,
            "height": height,
            "sha256": digest,
            "duplicate_of": duplicate_of,
            "referenced": referenced,
            "filtered_reason": reason,
        })
        if page_no and page_no <= len(pages):
            pages[page_no - 1]["image_paths"].append(rel)
    return records


def validate_links(md_path: Path, root: Path) -> dict:
    text = md_path.read_text(encoding="utf-8")
    missing: list[str] = []
    total = 0
    for target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "doc:")):
            continue
        total += 1
        if not (root / target).exists():
            missing.append(target)
    return {"images_referenced": total, "images_missing": missing,
            "ok": not missing}


# ---------------------------------------------------------------- format

# 只在“稳定重复且明确是版面构件”时才删除；孤立数字行不删（可能是答案）。
CHROME_PATTERNS = [
    re.compile(r"^第\s*\d+\s*页$"),
    re.compile(r"^[-—–]\s*\d{1,3}\s*[-—–]$"),
    re.compile(r"^理想树$"),
    re.compile(r"^配套《高中必刷题》"),
]

_CN_DIGITS = "一二三四五六七八九十百"
CHAPTER_HEAD_RE = re.compile(
    rf"^(#{{1,6}})\s*[-—–]?\s*(第\s*[{_CN_DIGITS}]+\s*[章节])\s*(.*)$"
)
NUMBERED_HEAD_RE = re.compile(r"^(#{1,6})\s*(\d+)\s*[.．]\s*(\d+)\s*(.*)$")
# 目录行形如 `- 1.1 集合的概念 … (1)` / `- 3.2 函数的基本性质 …… (41)`
TOC_LINE_RE = re.compile(r"^\s*[-·•]?\s*\d+\s*[.．]\s*\d+.*(?:…|\.{2,}).*$")


def _cn_to_int(text: str) -> int | None:
    text = re.sub(r"\s+", "", text)
    text = text.strip("第章节")
    if not text:
        return None
    if text.isdigit():
        return int(text)
    mapping = {"十": 10}
    for idx, ch in enumerate(_CN_DIGITS[:9], start=1):
        mapping[ch] = idx
    if text == "十":
        return 10
    total = 0
    if "十" in text:
        head, _, tail = text.partition("十")
        total = (mapping.get(head, 1) if head else 1) * 10
        total += mapping.get(tail, 0) if tail else 0
        return total if total else None
    return mapping.get(text)


def _clean_heading_title(raw: str) -> str:
    """`第五章三角函数` -> `第五章 三角函数`；`第一章 集合与常用逻辑用语` 原样保留。"""
    raw = raw.strip()
    m = re.match(rf"^(第\s*[{_CN_DIGITS}]+\s*[章节])\s*(.*)$", raw)
    if not m:
        return raw
    head, tail = m.group(1), m.group(2)
    head = re.sub(r"\s+", "", head)
    if tail and not tail[0].isspace() and "\u4e00" <= tail[0] <= "\u9fff":
        return f"{head} {tail}"
    return f"{head} {tail}".strip()


def _toc_heading_flags(lines: list[str]) -> set[int]:
    """A chapter heading is a TOC entry when a `- N.M … (页)` line follows closely."""
    flags: set[int] = set()
    for idx, line in enumerate(lines):
        if not CHAPTER_HEAD_RE.match(line.strip()):
            continue
        seen = 0
        for nxt in lines[idx + 1 :]:
            if not nxt.strip():
                continue
            seen += 1
            if TOC_LINE_RE.match(nxt):
                flags.add(idx)
                break
            if seen >= 6:
                break
    return flags


def _merge_split_headings(lines: list[str]) -> list[str]:
    """`## 第五章` + `## 三角函数` -> `## 第五章 三角函数`（MinerU 跨行标题）。"""
    out: list[str] = []
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        match = CHAPTER_HEAD_RE.match(line.strip())
        if match and not match.group(3).strip():
            head_level, head_text = match.group(1), match.group(2)
            nxt = idx + 1
            while nxt < len(lines) and not lines[nxt].strip():
                nxt += 1
            if nxt < len(lines):
                follow = lines[nxt].strip()
                follow_match = re.match(r"^#{1,6}\s*(.+)$", follow)
                if follow_match and len(follow_match.group(1).strip()) <= 24:
                    merged = f"{head_level} {_clean_heading_title(head_text)} {follow_match.group(1).strip()}"
                    out.append(merged)
                    idx = nxt + 1
                    continue
        out.append(line)
        idx += 1
    return out


def _normalize_heading_levels(lines: list[str], toc_flags: set[int]) -> list[str]:
    out: list[str] = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        chapter = CHAPTER_HEAD_RE.match(stripped)
        if chapter:
            title = _clean_heading_title(f"{chapter.group(2)} {chapter.group(3)}".strip())
            level = "####" if idx in toc_flags else "##"
            out.append(f"{level} {title}")
            continue
        numbered = NUMBERED_HEAD_RE.match(stripped)
        if numbered:
            suffix = f" {numbered.group(4).strip()}" if numbered.group(4).strip() else ""
            out.append(f"### {numbered.group(2)}.{numbered.group(3)}{suffix}")
            continue
        other = re.match(r"^#{1,6}\s*(.+)$", stripped)
        if other:
            out.append(f"#### {other.group(1).strip()}")
            continue
        out.append(line)
    return out


def stage_format(out_dir: Path) -> dict:
    manifest_path = out_dir / "conversion-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    stem = Path(manifest["stages"]["raw"]).stem
    raw = out_dir / manifest["stages"]["raw"]
    formatted = out_dir / manifest["stages"]["formatted"]
    text = raw.read_text(encoding="utf-8")

    # 1. strip stable chrome lines only
    kept: list[str] = []
    dropped = 0
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and any(p.match(stripped) for p in CHROME_PATTERNS):
            dropped += 1
            continue
        kept.append(line.rstrip())
    text = "\n".join(kept)

    # 2. collapse 3+ blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = text.splitlines()

    # 3. merge MinerU cross-line headings, then unify heading levels
    merged = _merge_split_headings(lines)
    toc_flags = _toc_heading_flags(merged)
    normalized = _normalize_heading_levels(merged, toc_flags)
    text = "\n".join(normalized)

    # 4. insert page markers from MinerU structured_content.json
    text, anchors, missing_pages = insert_page_markers(
        text, out_dir / "mineru" / "structured_content.json"
    )

    header = (
        f"# {stem}\n\n"
        f"> 由 PDF 原始扫描件经 MinerU 转换并格式化而成。\n"
        f"> 原始稿：`{manifest['stages']['raw']}`；本文件只做版面清理、标题层级统一与页码追溯，不重写正文。\n"
        f"> 源文件 SHA-256：`{manifest['source_sha256']}`\n\n---\n\n"
    )
    formatted.write_text(header + text, encoding="utf-8")

    manifest["stages"]["formatted"] = formatted.name
    manifest["format"] = {
        "dropped_chrome_lines": dropped,
        "merged_crossline_headings": len(merged) != len(lines),
        "toc_headings": len(toc_flags),
        "page_markers_inserted": anchors,
        "pages_without_marker": missing_pages,
        "validation": validate_links(formatted, out_dir),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest["format"]


def insert_page_markers(text: str, structured: Path,
                        min_key: int = 8) -> tuple[str, int, list[int]]:
    """Insert `<!-- 来源页：N -->` before the first block of each page.

    A workbook repeats layout labels (`印象笔记`, `狂K重点`, `知识深层理解`) on many
    pages, so "first block order" is a bad anchor — it can land pages ahead.
    Instead, score every candidate block of a page and keep the one whose
    forward search position is *smallest*: that is the earliest surviving text
    of the page. Keys shorter than `min_key` normalized chars are ignored
    because they are not discriminative.
    """
    if not structured.exists():
        return (text, 0, [])
    data = json.loads(structured.read_text(encoding="utf-8"))
    cursor = 0
    inserted = 0
    missing: list[int] = []
    out_parts: list[str] = []
    for page in data.get("pages", []):
        page_no = int(page.get("page_idx", 0)) + 1
        best: tuple[int, str] | None = None
        for candidate in block_texts(page):
            probe = norm_text(candidate)
            if len(probe) < min_key:
                continue
            idx = find_normalized(text, probe[:14], cursor)
            if idx is None:
                continue
            if best is None or idx < best[0]:
                best = (idx, probe)
        if best is None:
            missing.append(page_no)
            continue
        # 必须落在行首：若落在行中间，会把 `#### ` / `- ` 这类行首标记截断，
        # 既不美观也会破坏标题识别。
        line_start = text.rfind("\n", cursor, best[0]) + 1
        if line_start < cursor:
            line_start = cursor
        out_parts.append(text[cursor:line_start])
        out_parts.append(f"{PAGE_MARK_FMT.format(n=page_no)}\n")
        cursor = line_start
        inserted += 1
    out_parts.append(text[cursor:])
    return ("".join(out_parts), inserted, missing)


_WS = re.compile(r"\s+")


def find_normalized(text: str, key: str, start: int) -> int | None:
    """Find `key` in `text` ignoring all whitespace, honouring a raw offset start."""
    i = start
    k = 0
    n = len(key)
    first: int | None = None
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch == key[k]:
            if k == 0:
                first = i
            k += 1
            if k == n:
                return first
            i += 1
            continue
        if ch == key[0]:
            # restart the match at the current character
            first = i
            k = 1
            i += 1
            continue
        k = 0
        first = None
        i += 1
    return None


# ---------------------------------------------------------------- split

def chapter_spans(lines: list[str]) -> tuple[list[dict], list[str]]:
    """Group the body into chapters without inventing content.

    1. `第 X 章` headings give an explicit chapter start; TOC entries are skipped
       (a chapter heading followed by a `- N.M … (页)` line is a目录 entry).
    2. When the body lost a chapter heading, the first `N.M` 课时 heading still
       pins the chapter, because its leading number IS the chapter number.
    3. Chapter titles come from an explicit heading, else from the目录 entry.
       When neither exists the title stays bare (`第X章`) and a warning is kept.
    """
    warnings: list[str] = []
    toc_flags = _toc_heading_flags(lines)

    heading_hits: dict[int, tuple[int, str]] = {}
    toc_titles: dict[int, str] = {}
    for idx, line in enumerate(lines):
        match = CHAPTER_HEAD_RE.match(line.strip())
        if not match:
            continue
        chapter_no = _cn_to_int(match.group(2))
        if chapter_no is None:
            continue
        title = _clean_heading_title(f"{match.group(2)} {match.group(3)}".strip())
        if idx in toc_flags:
            toc_titles.setdefault(chapter_no, title)
        else:
            heading_hits.setdefault(chapter_no, (idx, title))

    section_first: dict[int, int] = {}
    for idx, line in enumerate(lines):
        numbered = NUMBERED_HEAD_RE.match(line.strip())
        if not numbered:
            continue
        chapter_no = int(numbered.group(2))
        if 1 <= chapter_no <= 40:
            section_first.setdefault(chapter_no, idx)

    anchors: list[dict] = []
    for chapter_no in sorted(set(heading_hits) | set(section_first)):
        starts: list[int] = []
        if chapter_no in heading_hits:
            starts.append(heading_hits[chapter_no][0])
        if chapter_no in section_first:
            starts.append(section_first[chapter_no])
        start = min(starts)
        if chapter_no in heading_hits:
            title, source = heading_hits[chapter_no][1], "heading"
        elif chapter_no in toc_titles:
            title, source = toc_titles[chapter_no], "toc"
            warnings.append(f"{title} 正文未检出章标题，起点取自首个课时编号 {chapter_no}.x")
        else:
            title, source = f"第{chapter_no}章", "section-number"
            warnings.append(
                f"第{chapter_no}章 正文与目录均未检出章标题，章名以课时编号推断（{chapter_no}.x）"
            )
        anchors.append({"chapter": chapter_no, "start": start, "title": title, "source": source})

    anchors.sort(key=lambda a: a["start"])
    for order, anchor in enumerate(anchors):
        end = anchors[order + 1]["start"] if order + 1 < len(anchors) else len(lines)
        anchor["end"] = end
        anchor["sections"] = [
            line.strip().lstrip("# ").strip()
            for line in lines[anchor["start"]:end]
            if NUMBERED_HEAD_RE.match(line.strip())
        ]
    return anchors, warnings


def line_page_map(lines: list[str]) -> list[int | None]:
    """`<!-- 来源页：N -->` 之后的行归属第 N 页。"""
    page: int | None = None
    mapping: list[int | None] = []
    marker = re.compile(r"<!--\s*来源页：(\d+)\s*-->")
    for line in lines:
        hit = marker.search(line)
        if hit:
            page = int(hit.group(1))
        mapping.append(page)
    return mapping


def recover_titles_from_headers(lines: list[str], anchors: list[dict],
                               structured: Path) -> list[str]:
    """章标题常被 MinerU 当作页眉从正文删掉，但 structured_content.json 仍保留着。

    只用页码归属范围内的页眉区块回填，不引入任何外部知识。
    """
    notes: list[str] = []
    if not structured.exists():
        return notes
    data = json.loads(structured.read_text(encoding="utf-8"))
    pages = data.get("pages", [])
    mapping = line_page_map(lines)
    for anchor in anchors:
        if anchor["source"] not in ("section-number", "toc"):
            continue
        chapter_no = anchor["chapter"]
        page_span = sorted({p for p in mapping[anchor["start"]: anchor["end"]] if p})
        for page_no in page_span[:3]:
            if not (1 <= page_no <= len(pages)):
                continue
            found = None
            for block in pages[page_no - 1].get("blocks", []):
                if block.get("type") not in ("header", "doc_title"):
                    continue
                text = block.get("content")
                if not isinstance(text, str):
                    continue
                match = CHAPTER_HEAD_RE.match(f"## {text.strip()}")
                if match and _cn_to_int(match.group(2)) == chapter_no:
                    found = _clean_heading_title(f"{match.group(2)} {match.group(3)}".strip())
                    break
            if found:
                if found != anchor["title"]:
                    notes.append(
                        f"「{anchor['title']}」在正文中无章标题，"
                        f"已由第 {page_no} 页页眉区块回填为「{found}」"
                    )
                    anchor["title"] = found
                    anchor["source"] = "page-header"
                break
    return notes


def stage_split(out_dir: Path) -> dict:
    manifest_path = out_dir / "conversion-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    formatted = out_dir / manifest["stages"]["formatted"]
    text = formatted.read_text(encoding="utf-8")
    stem = Path(manifest["stages"]["raw"]).stem
    lines = text.splitlines()

    anchors, warnings = chapter_spans(lines)
    recovery_notes = recover_titles_from_headers(
        lines, anchors, out_dir / "mineru" / "structured_content.json"
    )
    recovered = {a["chapter"] for a in anchors if a["source"] == "page-header"}
    warnings = [
        w for w in warnings
        if not any(w.startswith(f"第{n}章 正文与目录均未检出章标题") for n in recovered)
    ]
    warnings.extend(recovery_notes)
    split_root = out_dir / "拆分"

    written: list[str] = []
    readme = [f"# {stem} · 拆分索引", "",
              "由格式化稿在高置信度结构标题处切分；图片按相对路径引用根目录 `../../images/`。", ""]
    chapter_dir = split_root / "章节"
    entries: list[tuple[str, str, str]] = []  # (name, title, note)

    preamble = lines[: anchors[0]["start"]] if anchors else []
    if sum(1 for l in preamble if l.strip()) >= 10:
        name = "00-前言与目录.md"
        entries.append((name, "前言与目录", "章前内容（封面、寄语、目录等）"))

    used: set[str] = set()
    for order, anchor in enumerate(anchors, start=1):
        safe = re.sub(r"[\\/:*?\"<>|]", "", anchor["title"]).strip() or f"第{anchor['chapter']}章"
        name = f"{order:02d}-{safe}.md"
        while name in used:
            name = f"{order:02d}-{safe}-{anchor['chapter']}.md"
        used.add(name)
        entries.append((name, anchor["title"],
                        f"切分依据：{anchor['source']}；格式化稿第 {anchor['start'] + 1}–{anchor['end']} 行；"
                        f"课时：{'、'.join(anchor['sections']) or '—'}"))

    if entries:
        ensure_dir(chapter_dir)
        # 只逐个删除“本次不再产出”的旧拆分文件，不做递归目录删除
        expected = {f"拆分/{'章节'}/{name}" for name, _, _ in entries}
        expected |= {"拆分/章节/README.md", "拆分/README.md"}
        if split_root.exists():
            for old in sorted(split_root.rglob("*.md")):
                rel = str(old.relative_to(out_dir)).replace(os.sep, "/")
                if rel not in expected:
                    old.unlink()
        for name, title, note in entries:
            if name.startswith("00-"):
                body = "\n".join(preamble)
            else:
                anchor = anchors[int(name[:2]) - 1] if not name.startswith("00-") else None
                body = "\n".join(lines[anchor["start"]: anchor["end"]])
            # 拆分稿位于 拆分/<kind>/ 两层深处，图片目录在输出根，故用 ../../images/
            body = re.sub(r"\]\(images/", "](../../images/", body.rstrip())
            body = re.sub(r'<img src="images/', '<img src="../../images/', body)
            body += "\n"
            head = (
                f"# {title}\n\n"
                f"> 所属：《{stem}》\n"
                f"> 来源：`{manifest['stages']['formatted']}`（PDF 原始扫描件经 MinerU 转换）\n"
                f"> {note}\n"
                f"> 图片相对路径指向根目录 `../../images/`\n\n---\n\n"
            )
            (chapter_dir / name).write_text(head + body, encoding="utf-8")
            written.append(f"拆分/章节/{name}")
        readme.append("## 章节")
        readme.extend(f"- [{title}](章节/{name})" for name, title, _ in entries)
        readme.append("")
        (chapter_dir / "README.md").write_text(
            "\n".join([f"# {stem} · 章节", ""]
                      + [f"- [{title}]({name})　—　{note}" for name, title, note in entries] + [""]),
            encoding="utf-8",
        )
    else:
        ensure_dir(split_root)
        readme.append("未检测到 `第 X 章` / `第 X 单元` 级别的高置信度结构标题，故未生成拆分文档。")
    (split_root / "README.md").write_text("\n".join(readme), encoding="utf-8")

    manifest["stages"]["split"] = written
    manifest["split"] = {
        "count": len(written),
        "anchors": [{k: v for k, v in a.items()} for a in anchors],
        "warnings": warnings,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest["split"]


# ---------------------------------------------------------------- validate

CID_RE = re.compile(r"cid:\d+")
ART_RE = re.compile(r"[\u2500-\u27BF]{6,}")


def stage_validate(out_dir: Path) -> int:
    manifest_path = out_dir / "conversion-manifest.json"
    if not manifest_path.exists():
        print(f"[FAIL] manifest 缺失：{manifest_path}")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    problems: list[str] = []
    notes: list[str] = []

    raw = out_dir / manifest["stages"]["raw"]
    formatted = out_dir / manifest["stages"]["formatted"]
    for path, label in ((raw, "原始稿"), (formatted, "格式化稿")):
        if not path.exists():
            problems.append(f"{label}缺失：{path.name}")

    if problems:
        print("[FAIL] " + "；".join(problems))
        return 1

    # 1. page records
    pages = manifest.get("pages", [])
    if manifest.get("page_count") != len(pages):
        problems.append(f"page_count({manifest.get('page_count')}) != len(pages)({len(pages)})")

    # 2. links
    raw_check = validate_links(raw, out_dir)
    fmt_check = validate_links(formatted, out_dir)
    for label, chk in (("原始稿", raw_check), ("格式化稿", fmt_check)):
        if not chk["ok"]:
            problems.append(f"{label}图片断链 {len(chk['images_missing'])} 处：{chk['images_missing'][:5]}")
    if raw_check["images_referenced"] == 0:
        problems.append("原始稿没有任何图片引用")

    # 3. images in manifest exist
    missing_img = [rec["path"] for rec in manifest.get("images", [])
                   if not (out_dir / rec["path"]).exists()]
    if missing_img:
        problems.append(f"manifest 记录的图片文件缺失 {len(missing_img)} 个：{missing_img[:5]}")

    # 4. split docs indexed
    split_files = manifest["stages"].get("split", [])
    for rel in split_files:
        if not (out_dir / rel).exists():
            problems.append(f"拆分文档缺失：{rel}")
    if split_files:
        readme = out_dir / "拆分" / "README.md"
        if not readme.exists():
            problems.append("拆分/README.md 缺失")
        else:
            body = readme.read_text(encoding="utf-8")
            for rel in split_files:
                if Path(rel).name not in body:
                    problems.append(f"拆分文档未在 README 中索引：{rel}")
    for kind_dir in ("章节", "单元"):
        d = out_dir / "拆分" / kind_dir
        if d.exists():
            names = [p.name for p in d.glob("*.md") if p.name != "README.md"]
            if len(names) != len(set(names)):
                problems.append(f"拆分/{kind_dir} 存在重名文档")

    # 5. residual noise
    body = formatted.read_text(encoding="utf-8")
    cid_hits = len(CID_RE.findall(body))
    if cid_hits:
        notes.append(f"格式化稿仍有 {cid_hits} 处 `cid:` 残片，需人工复核")
    dropped = manifest.get("format", {}).get("dropped_chrome_lines")
    notes.append(f"格式化阶段删除重复页眉/页脚/孤页行 {dropped} 行")
    markers = manifest.get("format", {}).get("page_markers_inserted")
    notes.append(f"格式化稿插入页码追溯注释 {markers} 处 / 共 {len(pages)} 页")
    no_marker = manifest.get("format", {}).get("pages_without_marker") or []
    if no_marker:
        notes.append(f"无页码锚点的页（多为整页图，无正文可锚定）：{no_marker}")

    dupes = [r["path"] for r in manifest.get("images", []) if r.get("duplicate_of")]
    if dupes:
        notes.append(f"重复图片 {len(dupes)} 个（已记录 duplicate_of）")
    stale_images = [r for r in manifest.get("images", []) if r.get("filtered_reason")]
    if stale_images:
        notes.append(f"需复核图片 {len(stale_images)} 张（未被原始稿引用或与其它图重复）")
    for warn in manifest.get("warnings", []):
        notes.append(f"warning: {warn}")
    for warn in manifest.get("split", {}).get("warnings", []):
        notes.append(f"split warning: {warn}")

    print(f"输出目录: {out_dir}")
    print(f"页面记录: {len(pages)} 页；图片: {len(manifest.get('images', []))} 张"
          f"（引用 {sum(1 for r in manifest.get('images', []) if r['referenced'])}）")
    print(f"拆分文档: {len(split_files)}")
    for note in notes:
        print(f"  · {note}")
    if problems:
        print("[FAIL] " + "；".join(problems))
        return 1
    print("[OK] 三阶段产物、页面记录、图片链接与拆分索引全部通过")
    return 0


# ---------------------------------------------------------------- convert


def stage_convert(args) -> Path:
    pdf = Path(args.pdf).expanduser().resolve()
    if not pdf.exists():
        raise SystemExit(f"PDF 不存在：{pdf}")
    out_dir = (Path(args.out_root).expanduser().resolve() / pdf.stem)
    kit = find_mineru_kit(args.mineru_kit_bin)
    tmp = Path(tempfile.mkdtemp(prefix="mineru-"))
    cmd = [kit, "parse", str(pdf), "--pages", args.pages, "--tier", args.tier,
           "--format", "zip", "--output", str(tmp)]
    print("运行:", " ".join(cmd))
    proc = subprocess.run(cmd)
    if proc.returncode != 0:
        raise SystemExit(f"MinerU 转换失败（退出码 {proc.returncode}），未生成任何产物。")
    zips = sorted(tmp.glob("*.zip"))
    if not zips:
        raise SystemExit(f"MinerU 未产出 zip：{tmp}")
    payload = tmp / "payload"
    payload.mkdir()
    with zipfile.ZipFile(zips[0]) as zf:
        zf.extractall(payload)
    manifest = import_payload(payload, pdf, out_dir, "mineru", args.tier,
                              [" ".join(cmd)], args.model_source, [])
    print(f"原始稿已写入 {out_dir}（{manifest['page_count']} 页，"
          f"{len(manifest['images'])} 张图片）")
    return out_dir


def stage_import(args) -> Path:
    pdf = Path(args.pdf).expanduser().resolve()
    bundle = Path(args.bundle).expanduser().resolve()
    out_dir = (Path(args.out_root).expanduser().resolve() / pdf.stem)
    tmp = Path(tempfile.mkdtemp(prefix="mineru-import-"))
    if bundle.is_file() and bundle.suffix.lower() == ".zip":
        with zipfile.ZipFile(bundle) as zf:
            zf.extractall(tmp)
        payload = find_payload_dir(tmp)
    elif bundle.is_dir():
        payload = find_payload_dir(bundle)
    else:
        raise SystemExit(f"无法识别的 MinerU 产物：{bundle}")
    manifest = import_payload(payload, pdf, out_dir, "mineru", args.tier,
                              ["import-mineru", str(bundle)], args.model_source, [])
    print(f"已导入 {out_dir}（{manifest['page_count']} 页，{len(manifest['images'])} 张图片）")
    return out_dir


def stage_run(args) -> int:
    out_dir = stage_convert(args)
    args.dir = str(out_dir)
    stage_format(out_dir)
    stage_split(out_dir)
    return stage_validate(out_dir)


# ---------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PDF → Markdown（MinerU 4.x）三阶段流水线")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p, need_pdf=True):
        if need_pdf:
            p.add_argument("--pdf", required=True, help="PDF 路径")
        p.add_argument("--out-root", default="markdown", help="输出父目录，默认 markdown/")
        p.add_argument("--tier", default=DEFAULT_TIER,
                       help="MinerU 解析档位：flash/basic/standard/advanced")
        p.add_argument("--model-source", default="auto",
                       help="模型来源：auto/huggingface/modelscope")
        p.add_argument("--mineru-kit-bin", default=None, help="mineru-kit 可执行文件路径")

    p_run = sub.add_parser("run", help="convert + format + split + validate")
    add_common(p_run)
    p_run.add_argument("--pages", default="all", help="PDF 页码，如 all 或 1-20")

    p_conv = sub.add_parser("convert", help="仅 MinerU 转换")
    add_common(p_conv)
    p_conv.add_argument("--pages", default="all")

    p_imp = sub.add_parser("import-mineru", help="导入已有 MinerU 产物（zip 或目录）")
    add_common(p_imp)
    p_imp.add_argument("--bundle", required=True,
                       help="MinerU 产出的 zip，或已解压且含 markdown.md/images/ 的目录")

    for name, helper in (("format", "仅格式化"), ("split", "仅拆分"), ("validate", "仅校验")):
        p = sub.add_parser(name, help=helper)
        p.add_argument("--dir", required=True, help="转换输出目录")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        return stage_run(args)
    if args.command == "convert":
        stage_convert(args)
        return 0
    if args.command == "import-mineru":
        stage_import(args)
        return 0
    if args.command == "format":
        info = stage_format(Path(args.dir).expanduser().resolve())
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return 0
    if args.command == "split":
        info = stage_split(Path(args.dir).expanduser().resolve())
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return 0
    if args.command == "validate":
        return stage_validate(Path(args.dir).expanduser().resolve())
    return 1


if __name__ == "__main__":
    sys.exit(main())
