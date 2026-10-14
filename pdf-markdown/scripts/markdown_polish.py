#!/usr/bin/env python3
"""Markdown 精修器 —— 把 MinerU 产出的拆分稿整理为可直接渲染/检索的 Markdown。

面向「扫描件 OCR → MinerU → 拆分稿」这条链路的常见病灶：

1. 拆分稿位于两层子目录，图片相对路径却仍按一层写法（`../images/`）→ 全量断链
2. HTML `<table>` 内嵌 `<img src="images/...">`，路径同样失效且不便阅读
3. `$\\begin{cases}...\\end{cases}$` 之类的多行结构被塞进行内公式
4. 表格单元格里的数学符号未用 `$` 包裹，渲染成纯文本
5. `![](x)` 空 alt，无障碍与检索都失效
6. 标题层级跳跃（`#` / `###` / `####`），`(1)` `①` 等教材编号没有列表语义
7. OCR 版面换行把一个完整段落切成多个碎片段落

用法：

```bash
python markdown_polish.py polish --dir <拆分/章节目录> [--images-rel ../../images] [--backup]
python markdown_polish.py check  --dir <拆分/章节目录>
```

`polish` 只做**可逆的结构与格式整理**；不改写任何正文措辞，不修正 OCR 识别错误。
"""

from __future__ import annotations

import argparse
import html as html_mod
import json
import os
import re
import shutil
import sys
from pathlib import Path

CJK = r"\u4e00-\u9fff\u3400-\u4dbf"
CJK_PUNCT = "，。；：、！？）】》」』·…—"
OPEN_PUNCT = "（【《「『"

# ---------------------------------------------------------------- 图片链接

IMG_MD_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
IMG_HTML_RE = re.compile(r'<img\s+src="([^"]+)"[^>]*/?>', re.I)


def _alt_from_path(path: str) -> str:
    """由图片文件名生成可读 alt，如 page_95_image_21.jpg -> 图 p95-21。"""
    name = Path(path).stem
    m = re.match(r"page_(\d+)_image_(\d+)$", name)
    if m:
        return f"图 p{m.group(1)}-{m.group(2)}"
    m = re.match(r"page_(\d+)_table_image_(\d+)_(\d+)$", name)
    if m:
        return f"表 p{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return f"图 {name}"


def fix_image_links(text: str, images_rel: str) -> tuple[str, dict]:
    """统一图片相对路径，并为空 alt 补描述。"""
    stats = {"md_relinked": 0, "html_relinked": 0, "alt_filled": 0}

    def repl_md(m: re.Match) -> str:
        alt, path = m.group(1), m.group(2).strip()
        if path.startswith("http") or path.startswith("data:"):
            return m.group(0)
        rel = path
        if re.match(r"^\.{0,2}/?images/", rel):
            rel = f"{images_rel}/{rel.split('images/', 1)[1]}"
        elif rel.startswith("images/"):
            rel = f"{images_rel}/{rel.split('images/', 1)[1]}"
        if rel != path:
            stats["md_relinked"] += 1
        if not alt.strip():
            alt = _alt_from_path(rel)
            stats["alt_filled"] += 1
        return f"![{alt}]({rel})"

    text = IMG_MD_RE.sub(repl_md, text)

    def repl_html(m: re.Match) -> str:
        path = m.group(1).strip()
        rel = path
        if rel.startswith("images/"):
            rel = f"{images_rel}/{rel.split('images/', 1)[1]}"
        if rel != path:
            stats["html_relinked"] += 1
        return f"![{_alt_from_path(rel)}]({rel})"

    text = IMG_HTML_RE.sub(repl_html, text)
    return text, stats


# ---------------------------------------------------------------- HTML 表格

TABLE_RE = re.compile(r"<table\b[^>]*>(.*?)</table>", re.S | re.I)
TR_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.S | re.I)
TD_RE = re.compile(r"<t([dh])\b([^>]*)>(.*?)</t\1>", re.S | re.I)


def _cell_text(raw: str) -> str:
    raw = IMG_HTML_RE.sub(lambda m: f"![{_alt_from_path(m.group(1))}]({m.group(1)})", raw)
    raw = re.sub(r"<br\s*/?>", " ", raw, flags=re.I)
    raw = re.sub(r"</?(?:p|div|span|b|strong|i|em|sub|sup)\b[^>]*>", "", raw, flags=re.I)
    raw = html_mod.unescape(raw)
    raw = raw.replace("|", "\\|")
    raw = re.sub(r"\s+", " ", raw)
    return raw.strip()


def _html_table_to_md(body: str) -> str:
    rows: list[list[str]] = []
    pending: list[list] = []  # [col, rows_left]
    for tr in TR_RE.findall(body):
        cells = TD_RE.findall(tr)
        row: list[str] = []
        col = 0
        ti = 0
        while ti < len(cells):
            carried = False
            for p in pending:
                if p[0] == col and p[1] > 0:
                    row.append("")
                    p[1] -= 1
                    col += 1
                    carried = True
                    break
            if carried:
                continue
            _tag, attrs, inner = cells[ti]
            ti += 1
            cs = int((re.search(r'colspan="(\d+)"', attrs, re.I) or [0, "1"])[1])
            rs = int((re.search(r'rowspan="(\d+)"', attrs, re.I) or [0, "1"])[1])
            txt = _cell_text(inner)
            row.append(txt)
            for _ in range(cs - 1):
                row.append("")
            col += cs
            if rs > 1:
                pending.append([col - cs, rs - 1])
        rows.append(row)

    width = max((len(r) for r in rows), default=0)
    if width == 0:
        return ""
    rows = [r + [""] * (width - len(r)) for r in rows]

    out = []
    for i, r in enumerate(rows):
        out.append("| " + " | ".join(c if c else " " for c in r) + " |")
        if i == 0:
            out.append("| " + " | ".join(["---"] * width) + " |")
    return "\n".join(out)


def html_tables_to_markdown(text: str) -> tuple[str, int]:
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        md = _html_table_to_md(m.group(1))
        if not md:
            return m.group(0)
        count += 1
        return "\n\n" + md + "\n"

    text = TABLE_RE.sub(repl, text)
    return text, count


# ---------------------------------------------------------------- 空格清理

MATH_SPAN_RE = re.compile(r"\$\$.*?\$\$|\$[^$\n]+\$", re.S)


def clean_spaces_line(line: str) -> str:
    """保守清理空格：只动标点周围与多余空格，不删中文之间的单空格。

    OCR 版面里「提示 集合是……」这类单空格常承担分隔作用，
    一并按「中文间空格」删除会造成词语粘连，因此这里只清理：
    中文/标点相邻处的空格、连续空格、行尾空格、全角空格。
    """
    if re.match(r"^\s*(\||#)", line):  # 表格行与标题保留原样
        return line.rstrip()
    parts: list[str] = []
    last = 0
    for m in MATH_SPAN_RE.finditer(line):
        parts.append(("t", line[last:m.start()]))
        parts.append(("m", m.group(0)))
        last = m.end()
    parts.append(("t", line[last:]))

    out = []
    for kind, seg in parts:
        if kind == "m":
            out.append(seg)
            continue
        s = seg.replace("\u3000", "")
        s = re.sub(rf"([{CJK}])[ \t]+([{CJK_PUNCT}])", r"\1\2", s)
        s = re.sub(rf"([{OPEN_PUNCT}])[ \t]+([{CJK}])", r"\1\2", s)
        s = re.sub(r"[ \t]{2,}", " ", s)
        out.append(s)
    return "".join(out).rstrip()


# ---------------------------------------------------------------- 公式

INLINE_MATH_RE = re.compile(r"(?<!\$)\$(?!\$)([^$\n]+)\$(?!\$)")
BLOCK_ENV_RE = re.compile(r"\\begin\{(cases|aligned|align|array|matrix|pmatrix|split|gathered)\}")


ADJACENT_MATH_RE = re.compile(r"(?<=\S)\$\$(?=\S)")


def split_adjacent_math(lines: list[str]) -> int:
    """`$A$$B$` 这种两个行内公式贴在一起的情况拆开，避免被当成公式块。"""
    fixed = 0
    in_block = False
    for i, line in enumerate(lines):
        if line.strip() == "$$":
            in_block = not in_block
            continue
        if in_block or "$$" not in line:
            continue
        new = ADJACENT_MATH_RE.sub("$ $", line)
        if new != line:
            lines[i] = new
            fixed += 1
    return fixed


def normalize_math(lines: list[str]) -> tuple[list[str], int]:
    """把含多行结构（cases/aligned/\\\\）的行内公式提升为独立公式块。"""
    out: list[str] = []
    promoted = 0
    i = 0
    in_block = False
    while i < len(lines):
        line = lines[i]
        if line.strip() == "$$":
            in_block = not in_block
            out.append(line)
            i += 1
            continue
        if in_block:
            out.append(line)
            i += 1
            continue

        m = INLINE_MATH_RE.search(line)
        if m and (BLOCK_ENV_RE.search(m.group(1)) or "\\\\" in m.group(1)):
            before = line[: m.start()].rstrip()
            after = line[m.end():].lstrip()
            if before:
                out.append(before)
                out.append("")
            out.append("$$")
            out.append(m.group(1).strip())
            out.append("$$")
            if after:
                out.append("")
                out.append(after)
            promoted += 1
            i += 1
            continue
        out.append(line)
        i += 1
    return out, promoted


SEP_ROW_RE = re.compile(r"^\s*\|(\s*:?-{2,}:?\s*\|)+\s*$")
ROW_SPLIT_RE = re.compile(r"(?<!\\)\|")


def _split_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip() for c in ROW_SPLIT_RE.split(s)]


def _merge_fragments(cells: list[str], width: int) -> list[str]:
    """把被单元格内未转义 `|` 切碎的单元格重新拼起来。

    判据：前一段以反斜杠结尾（LaTeX 竖线 `\\|` 被截断）或 `$` 数量为奇数，
    说明它还没说完，应把下一段并回来，并用转义竖线 `\\|` 连接。
    """
    out: list[str] = []
    acc: str | None = None
    for c in cells:
        if acc is None:
            acc = c
        elif acc.endswith("\\") or acc.count("$") % 2 == 1:
            acc = f"{acc} \\| {c}"
        else:
            out.append(acc)
            acc = c
    if acc is not None:
        out.append(acc)
    while len(out) > width:
        tail = out.pop()
        out[-1] = f"{out[-1]} \\| {tail}"
    while len(out) < width:
        out.append("")
    return out


def normalize_markdown_tables(lines: list[str]) -> dict:
    """对齐已存在的 Markdown 表格：以分隔行为准统一列宽，转义单元格内竖线。"""
    stats = {"tables": 0, "rows_fixed": 0}
    i = 0
    while i < len(lines):
        if not lines[i].lstrip().startswith("|"):
            i += 1
            continue
        j = i
        while j < len(lines) and lines[j].lstrip().startswith("|"):
            j += 1
        block = lines[i:j]
        seps = [k for k, l in enumerate(block) if SEP_ROW_RE.match(l)]
        if not seps:
            i = j
            continue
        width = len(_split_row(block[seps[0]]))
        stats["tables"] += 1
        if width == 1:
            # 单列表格多是「竖排条目」的版面产物，还原为列表更易读
            rows = []
            for k, line in enumerate(block):
                if SEP_ROW_RE.match(line):
                    continue
                cell = " \\| ".join(_split_row(line)).strip()
                if cell:
                    rows.append(f"- {cell}")
            if rows:
                lines[i:j] = rows
                stats["rows_fixed"] += len(block)
                i = i + len(rows)
                continue
        for k, line in enumerate(block):
            if SEP_ROW_RE.match(line):
                block[k] = "| " + " | ".join(["---"] * width) + " |"
                continue
            cells = _merge_fragments(_split_row(line), width)
            new = "| " + " | ".join(c if c else " " for c in cells) + " |"
            if new != line:
                stats["rows_fixed"] += 1
            block[k] = new
        lines[i:j] = block
        i = j
    return stats


COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def fix_dangerous_lt(lines: list[str]) -> int:
    """裸 `<` 紧跟字母会被 HTML 渲染器当作未闭合标签吞掉后续内容。

    修复：注释 `<!-- -->` 内的 `<` 保留；其余 `<` 后若是字母，插入一个空格
    （数学模式里空格无意义，文本模式里 `< ` 不构成标签起始）。
    """
    changed = 0
    for i, line in enumerate(lines):
        spans = [m.span() for m in COMMENT_RE.finditer(line)]
        out = []
        last = 0
        for m in re.finditer(r"<(?=[A-Za-z])", line):
            if any(s <= m.start() < e for s, e in spans):
                continue
            out.append(line[last:m.end()])
            out.append(" ")
            last = m.end()
            changed += 1
        out.append(line[last:])
        lines[i] = "".join(out)
    return changed


def mid_pipes_in_math(lines: list[str]) -> int:
    """数学片段里的 `\\|` 渲染成 ∥（平行号），集合分隔符应为 `\\mid`。"""
    changed = 0
    for i, line in enumerate(lines):
        def fix_span(m: re.Match) -> str:
            nonlocal changed
            body = m.group(0)
            if "\\|" in body:
                body = body.replace("\\|", "\\mid ")
                changed += 1
            return body
        lines[i] = MATH_SPAN_RE.sub(fix_span, line)
    return changed


def inline_display_blocks(lines: list[str]) -> int:
    """把 `$$` 独占行的多行块合并为单行 `$$…$$`，块内注释行移到块外。

    KaTeX auto-render 类预览按文本节点配对 `$$`，多行块会跨段落失配导致
    公式原文裸露；单行块在 Obsidian / GitHub / KaTeX 下都能正确渲染。
    """
    changed = 0
    i = 0
    while i < len(lines):
        if lines[i].strip() != "$$":
            i += 1
            continue
        j = i + 1
        while j < len(lines) and lines[j].strip() != "$$":
            j += 1
        if j >= len(lines):
            break  # 未闭合，交给 check 报告
        content = lines[i + 1 : j]
        comments = [l for l in content if l.strip().startswith("<!--")]
        body = [l.strip() for l in content if l.strip() and not l.strip().startswith("<!--")]
        repl = comments + ["$$ " + " ".join(body) + " $$"]
        lines[i : j + 1] = repl
        changed += 1
        i += len(repl)
    return changed


def wrap_math_in_tables(lines: list[str]) -> int:
    """给表格单元格里裸露的数学片段补 `$...$`。"""
    changed = 0
    for i, line in enumerate(lines):
        if not re.match(r"^\s*\|", line):
            continue
        if SEP_ROW_RE.match(line):
            continue
        cells = ROW_SPLIT_RE.split(line.strip().strip("|"))
        new_cells = []
        for c in cells:
            c2 = c.strip()
            if not c2 or "$" in c2:
                new_cells.append(c)
                continue
            if needs_math_wrap(c2):
                new_cells.append(f" ${c2}$ ")
                changed += 1
            else:
                new_cells.append(c)
        lines[i] = "| " + " | ".join(x.strip() for x in new_cells) + " |"
    return changed


MATHY = re.compile(
    r"[αβγδεθλμπρσφωΔΣΩ∈∉⊂⊆⊃⊇∪∩∅≠≤≥±×÷√∞→⇒⇔∀∃]"
    r"|\\[a-zA-Z]+|[\^_]{1}[{a-zA-Z0-9]"
)


def needs_math_wrap(cell: str) -> bool:
    if not MATHY.search(cell):
        return False
    cjk = len(re.findall(rf"[{CJK}]", cell))
    if cjk > 3:  # 以中文叙述为主，不做包裹
        return False
    # 形如 y=sin x、β=-α+2kπ、180°=π rad、x∈[0,+∞)
    if re.fullmatch(r"[^，。；：、]{1,40}", cell) and re.search(r"[=<>∈≤≥≈∪∩→]", cell):
        return True
    if re.fullmatch(r"[\dA-Za-zα-ωΑ-Ω°^_=+\-*/().\[\]{},<>$ \\\u2200-\u22ff]+", cell):
        return True
    return False


# ---------------------------------------------------------------- 标题

HEAD_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def normalize_headings(lines: list[str]) -> tuple[list[str], dict]:
    """把 `#`/`###`/`####` 的跳跃层级压成 `#` → `##` → `###`。"""
    title = None
    for l in lines:
        m = HEAD_RE.match(l)
        if m and len(m.group(1)) == 1:
            title = m.group(2).strip()
            break

    out: list[str] = []
    stats = {"dropped_duplicate": 0, "remapped": 0}
    seen_first_h1 = False
    for line in lines:
        m = HEAD_RE.match(line)
        if not m:
            out.append(line)
            continue
        level, text = len(m.group(1)), m.group(2).strip()
        if level == 1 and not seen_first_h1:
            seen_first_h1 = True
            out.append(f"# {text}")
            continue
        if title and text.replace(" ", "") == title.replace(" ", ""):
            stats["dropped_duplicate"] += 1
            continue  # 与文件标题重复的正文标题
        new = {1: 2, 2: 2, 3: 2, 4: 3, 5: 3, 6: 4}[level]
        if new != level:
            stats["remapped"] += 1
        out.append(f"{'#' * new} {text}")
    return out, {"title": title, **stats}


# ---------------------------------------------------------------- 列表化 / 段落合并

RE_PAREN_NUM = re.compile(r"^\s*[（(]\s*(\d{1,2})\s*[)）]\s*")
RE_CIRCLED = re.compile(r"^\s*([①②③④⑤⑥⑦⑧⑨⑩⑳])\s*")
RE_CJK_NUM = re.compile(r"^\s*[（(]\s*([一二三四五六七八九十]{1,3})\s*[)）]\s*")


def _is_structural(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    return bool(
        s.startswith("#")
        or s.startswith("|")
        or s.startswith("![")
        or s.startswith(">")
        or s.startswith("<!--")
        or s.startswith("$$")
        or s.startswith("- ")
        or re.match(r"^\d+\.\s", s)
        or s.startswith("---")
    )


RE_SHORT_NUM = re.compile(r"^(\d{1,2})\.\s+(\S.{0,26})$")


def promote_short_numbered_headings(lines: list[str]) -> int:
    """把 `2. 集合间的基本关系` 这类短编号行提升为小节标题。

    OCR 常把同级小标题识别成正文行（同级的「1. 集合的含义与表示」却带 `####`），
    导致编号列表与标题混杂。仅对「短、无句末标点、不含公式」的行提升。
    """
    promoted = 0
    in_block = False
    for i, line in enumerate(lines):
        if line.strip() == "$$":
            in_block = not in_block
            continue
        if in_block:
            continue
        s = line.strip()
        m = RE_SHORT_NUM.match(s)
        if not m:
            continue
        body = m.group(2).strip()
        if "$" in body or re.search(r"[。；：！？]$", body) or len(body) > 24:
            continue
        if re.search(rf"[{CJK_PUNCT}]", body):
            continue
        lines[i] = f"### {m.group(1)}. {body}"
        promoted += 1
    return promoted


def listify(lines: list[str]) -> tuple[list[str], int]:
    """教材编号 `(1)` / `①` / `（一）` → 真正的 Markdown 列表。"""
    out: list[str] = []
    changed = 0
    in_block = False
    for line in lines:
        if line.strip() == "$$":
            in_block = not in_block
            out.append(line)
            continue
        if in_block or _is_structural(line):
            out.append(line)
            continue
        m = RE_PAREN_NUM.match(line)
        if m:
            out.append(f"{m.group(1)}. {line[m.end():]}".rstrip())
            changed += 1
            continue
        m = RE_CIRCLED.match(line)
        if m:
            out.append(f"- {line[m.end():]}".rstrip())
            changed += 1
            continue
        m = RE_CJK_NUM.match(line)
        if m:
            out.append(f"- {line[m.end():]}".rstrip())
            changed += 1
            continue
        out.append(line)

    # 紧凑化：相邻列表项之间的空行去掉
    compact: list[str] = []
    for line in out:
        if not line.strip() and compact:
            prev = compact[-1].strip()
            nxt = next((l for l in out[out.index(line):] if l.strip()), "")
            if re.match(r"^(- |\d+\.\s)", prev) and re.match(r"^(- |\d+\.\s)", nxt.strip()):
                continue
        compact.append(line)
    return compact, changed


def merge_broken_paragraphs(lines: list[str]) -> int:
    """合并被版面换行切断的中文段落（上一行不以句末标点收尾时才合并）。"""
    merged = 0
    i = 0
    while i < len(lines) - 2:
        a, blank, b = lines[i], lines[i + 1], lines[i + 2]
        if a.strip() and not blank.strip() and b.strip():
            a_s, b_s = a.strip(), b.strip()
            if (
                not _is_structural(a)
                and not _is_structural(b)
                and len(a_s) >= 10
                and re.search(rf"[{CJK}]$", a_s)
                and a_s[-1] not in CJK_PUNCT
                and re.match(rf"[{CJK}]", b_s)
                and not re.match(r"^[【（(①②③④⑤⑥⑦⑧⑨⑩]", b_s)
                and a_s.count("$") % 2 == 0
            ):
                lines[i] = a_s + b_s
                del lines[i + 1: i + 3]
                merged += 1
                continue
        i += 1
    return merged


def squeeze_blank_lines(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        if not line.strip() and out and not out[-1].strip():
            continue
        out.append(line)
    return out


# ---------------------------------------------------------------- 头部

def strip_legacy_head(lines: list[str]) -> tuple[list[str], list[str]]:
    """去掉旧的 `# 标题` 与 `> 所属/来源/...` 元信息块，保留课时信息。"""
    meta: list[str] = []
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and HEAD_RE.match(lines[i]):
        i += 1  # 旧文件标题，稍后由 frontmatter 重建
    j = i
    while j < len(lines) and j < 16:
        s = lines[j].strip()
        if s.startswith(">"):
            body = s.lstrip("> ").strip()
            if body.startswith(("所属：", "来源：", "图片相对路径")):
                j += 1
                continue
            meta.append(body)
            j += 1
            continue
        if s in ("", "---"):
            j += 1
            continue
        break
    rest = lines[j:]
    while rest and not rest[0].strip():
        rest.pop(0)
    return rest, meta


def clean_meta(meta: list[str]) -> list[str]:
    """去掉流水线内部信息（格式化稿行号）与已在 frontmatter 展示的课时。"""
    out = []
    for m in meta:
        m = re.sub(r"切分依据：(\w+)", lambda x: "切分依据：" + {
            "toc": "目录", "heading": "正文标题", "page-header": "页眉回填",
        }.get(x.group(1), x.group(1)), m)
        m = re.sub(r"格式化稿第\s*[\d–\-]+\s*行；?", "", m)
        m = re.sub(r"；?\s*课时：.*$", "", m)
        m = m.strip().rstrip("；;").strip()
        if m:
            out.append(m)
    return out


def page_range(lines: list[str]) -> tuple[int | None, int | None]:
    nums = [int(m.group(1)) for m in (re.search(r"来源页：(\d+)", l) for l in lines) if m]
    return (min(nums), max(nums)) if nums else (None, None)


def build_frontmatter(title: str, meta: list[str], pages: tuple[int | None, int | None],
                      book: str) -> list[str]:
    sections: list[str] = []
    for m in meta:
        m2 = re.sub(r"^切分依据：\w+；格式化稿第 [\d–]+ 行；", "", m)
        if m2.startswith("课时："):
            sections = [s.strip() for s in m2[3:].split("、") if s.strip()]
    tags = ["高中数学", "必修第一册", "狂K重点", title]
    fm = ["---", f"title: {title}", f"book: {book}", "subject: 数学", "level: 高中",
          "type: 教辅精讲", "source: MinerU 4.0.7 · PDF 扫描件 OCR"]
    if pages[0] and pages[1]:
        fm.append(f"pages: {pages[0]}-{pages[1]}")
    fm.append("tags:")
    for t in tags:
        fm.append(f"  - {t}")
    fm.append("---")
    fm.append("")
    if sections:
        fm.append("> **课时**：" + "　·　".join(sections))
        fm.append("")
    return fm


# ---------------------------------------------------------------- 主流程

def polish_file(path: Path, images_rel: str, book: str, add_frontmatter: bool) -> dict:
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    text, img_stats = fix_image_links("\n".join(lines), images_rel)
    lines = text.splitlines()

    text, tbl_count = html_tables_to_markdown("\n".join(lines))
    lines = text.splitlines()
    tbl_norm = normalize_markdown_tables(lines)

    lines = [clean_spaces_line(l) for l in lines]
    adjacent_fixed = split_adjacent_math(lines)
    lines, promoted = normalize_math(lines)
    display_merged = inline_display_blocks(lines)
    tbl_math = wrap_math_in_tables(lines)
    lt_fixed = fix_dangerous_lt(lines)
    mid_fixed = mid_pipes_in_math(lines)
    lines, head_stats = normalize_headings(lines)
    promoted_headings = promote_short_numbered_headings(lines)
    lines, listed = listify(lines)
    merged = merge_broken_paragraphs(lines)
    lines = squeeze_blank_lines(lines)

    # 去掉孤立装饰符号
    lines = [l for l in lines if not re.fullmatch(r"\s*[◀▶▲△●○※▸◂]\s*", l)]

    body, meta = strip_legacy_head(lines)
    meta = clean_meta(meta)
    pages = page_range(body)
    title = head_stats.get("title") or path.stem
    head: list[str] = []
    if add_frontmatter:
        head = build_frontmatter(title, meta, pages, book)
    head.append(f"# {title}")
    head.append("")
    if meta:
        head.append("\n".join(f"> {m}" for m in meta))
        head.append("")
    head.append("---")
    head.append("")

    body = head + body
    out = "\n".join(body).rstrip() + "\n"
    path.write_text(out, encoding="utf-8")

    return {
        "file": path.name,
        "images": img_stats,
        "html_tables_converted": tbl_count,
        "table_rows_realigned": tbl_norm["rows_fixed"],
        "table_cells_math_wrapped": tbl_math,
        "inline_math_promoted": promoted,
        "display_blocks_merged": display_merged,
        "adjacent_math_split": adjacent_fixed,
        "dangerous_lt_fixed": lt_fixed,
        "mid_pipes_fixed": mid_fixed,
        "headings_remapped": head_stats.get("remapped", 0),
        "short_headings_promoted": promoted_headings,
        "duplicate_headings_dropped": head_stats.get("dropped_duplicate", 0),
        "lines_listified": listed,
        "paragraphs_merged": merged,
        "pages": pages,
        "chars_before": len(raw),
        "chars_after": len(out),
    }


# ---------------------------------------------------------------- 校验

def check_file(path: Path, images_root: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    issues: list[str] = []

    broken = []
    for alt, p in IMG_MD_RE.findall(text):
        if p.startswith("http"):
            continue
        if not (path.parent / p).resolve().exists():
            broken.append(p)
    if broken:
        issues.append(f"图片断链 {len(broken)} 处，例如 {broken[0]}")

    odd: list[int] = []
    lonely_block = sum(1 for l in lines if l.strip() == "$$")
    if lonely_block % 2 == 1:
        issues.append(f"独立成行的 $$ 未成对（共 {lonely_block} 处）")
    # 块内空行 / 块内注释：都会破坏渲染
    open_idx: int | None = None
    for i, l in enumerate(lines):
        if l.strip() != "$$":
            continue
        if open_idx is None:
            open_idx = i
        else:
            inner = lines[open_idx + 1 : i]
            if any(not x.strip() for x in inner):
                issues.append(f"$$ 块内有空行（第 {open_idx + 1}–{i + 1} 行）")
            if any(x.strip().startswith("<!--") for x in inner):
                issues.append(f"$$ 块内有注释（第 {open_idx + 1}–{i + 1} 行）")
            open_idx = None
    for i, l in enumerate(lines):
        if l.strip() == "$$" or SEP_ROW_RE.match(l):
            continue
        if re.sub(r"\$\$[^$]*\$\$", "", l).count("$") % 2 == 1:
            odd.append(i + 1)
    if odd:
        issues.append(f"行内 $ 未闭合，行号 {odd[:5]}")

    # 表格列数一致（以分隔行为准）
    block: list[tuple[int, int]] = []
    for i, l in enumerate(lines):
        if re.match(r"^\s*\|", l):
            n = len(_split_row(l))
            block.append((i + 1, n))
        else:
            if len(block) >= 2:
                widths = {n for _, n in block}
                if len(widths) > 1:
                    issues.append(f"表格列数不一致（第 {block[0][0]} 行起，列宽 {sorted(widths)}）")
            block = []

    # 标题层级不跳级
    prev = 0
    for i, l in enumerate(lines):
        m = HEAD_RE.match(l)
        if not m:
            continue
        lv = len(m.group(1))
        if prev and lv > prev + 1:
            issues.append(f"标题层级跳级：第 {i + 1} 行 `{'#' * lv}` 紧跟 `{'#' * prev}`")
        prev = lv

    if re.search(r"\n{4,}", text):
        issues.append("存在 3 行以上连续空行")

    # 裸 `<` 紧跟字母：HTML 渲染器会当作未闭合标签吞掉后续内容
    bad_lt = [
        i + 1
        for i, l in enumerate(lines)
        if any(
            not any(s <= m.start() < e for s, e in
                    [(cm.start(), cm.end()) for cm in COMMENT_RE.finditer(l)])
            for m in re.finditer(r"<(?=[A-Za-z])", l)
        )
    ]
    if bad_lt:
        issues.append(f"裸 `<` 紧跟字母（会被当成 HTML 标签吞内容），行号 {bad_lt[:5]}")

    return {"file": path.name, "ok": not issues, "issues": issues,
            "images": len(IMG_MD_RE.findall(text)), "lines": len(lines)}


# ---------------------------------------------------------------- CLI

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="MinerU 拆分稿 Markdown 精修器")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("polish", help="精修目录下的 markdown")
    p1.add_argument("--dir", required=True)
    p1.add_argument("--images-rel", default="../../images", help="图片相对路径前缀")
    p1.add_argument("--book", default=None)
    p1.add_argument("--no-frontmatter", action="store_true")
    p1.add_argument("--backup", action="store_true", default=True)
    p1.add_argument("--no-backup", dest="backup", action="store_false")

    p2 = sub.add_parser("check", help="校验目录下的 markdown")
    p2.add_argument("--dir", required=True)
    p2.add_argument("--images-root", default=None)

    args = ap.parse_args(argv)
    d = Path(args.dir).expanduser().resolve()
    files = sorted(f for f in d.glob("*.md") if f.name != "README.md")
    if not files:
        print(f"目录内没有待处理的 markdown：{d}", file=sys.stderr)
        return 1

    if args.cmd == "polish":
        book = args.book or d.parents[1].name
        if args.backup:
            bak = d.parent / "_优化前备份"
            if not bak.exists():
                bak.mkdir(parents=True, exist_ok=True)
            for f in files:
                shutil.copy2(f, bak / f.name)
            print(f"备份 → {bak}", file=sys.stderr)
        report = [polish_file(f, args.images_rel, book, not args.no_frontmatter)
                  for f in files]
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    root = Path(args.images_root) if args.images_root else d.parents[1] / "images"
    results = [check_file(f, root) for f in files]
    bad = [r for r in results if not r["ok"]]
    for r in results:
        flag = "OK " if r["ok"] else "FAIL"
        print(f"[{flag}] {r['file']}  ({r['lines']} 行 / {r['images']} 图)")
        for i in r["issues"]:
            print(f"        - {i}")
    print(f"\n通过 {len(results) - len(bad)}/{len(results)}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
