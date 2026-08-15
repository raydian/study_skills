"""Small, deterministic primitives shared by the PDF ingestion workflow.

This module deliberately contains no MinerU execution code.  The path, source
identity, and manifest helpers are kept independent so later ingestion stages
can use them without changing how source identity is represented on disk.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Final


_HYPHEN_RE: Final[re.Pattern[str]] = re.compile(r"-+")


@dataclass(frozen=True)
class OutputPaths:
    """Canonical output directories for one source title."""

    markdown_dir: Path
    book_dir: Path
    category: str
    title: str
    slug: str


@dataclass(frozen=True)
class IngestionConfig:
    """Configuration shared by the later MinerU ingestion stages."""

    pdf: Path
    category: str
    title: str
    markdown_root: Path = Path("markdown")
    books_root: Path = Path("books")
    language: str = "ch"
    backend: str = "pipeline"
    mineru_bin: Path | None = None
    work_root: Path | None = None
    timeout: int = 1800

    @property
    def paths(self) -> OutputPaths:
        """Return the validated output locations for this configuration."""

        return build_output_paths(
            markdown_root=self.markdown_root,
            books_root=self.books_root,
            category=self.category,
            title=self.title,
        )

    @property
    def output_paths(self) -> OutputPaths:
        """Alias used by callers that prefer an explicit property name."""

        return self.paths

    @property
    def pdf_path(self) -> Path:
        """Compatibility alias for code that names the source ``pdf_path``."""

        return self.pdf


class IngestionError(RuntimeError):
    """Raised when MinerU cannot be located, run, or produces incomplete output."""


@dataclass(frozen=True)
class MinerUResult:
    """Details from one successful MinerU invocation."""

    binary: Path
    version: str
    command: list[str]
    staging_dir: Path
    auto_dir: Path
    stdout: str
    stderr: str
    returncode: int = 0

    @property
    def output_dir(self) -> Path:
        """Compatibility name for callers referring to the staging output root."""

        return self.staging_dir


@dataclass(frozen=True)
class ConversionResult:
    """Imported MinerU assets and their conversion manifest."""

    raw_path: Path
    manifest_path: Path
    manifest: dict[str, object]


@dataclass(frozen=True)
class ValidationIssue:
    """One conversion validation problem, suitable for a blocking report."""

    code: str
    message: str
    path: Path


@dataclass(frozen=True)
class ValidationReport:
    """The resource-integrity result for a converted Markdown directory."""

    status: str
    issues: tuple[ValidationIssue, ...]
    blocking_count: int


_IMAGE_TARGET_RE: Final[re.Pattern[str]] = re.compile(
    r"(!\[[^\]]*\]\()(?P<target><[^>\n]+>|[^)\s]+)"
)
_REFERENCE_IMAGE_USE_RE: Final[re.Pattern[str]] = re.compile(
    r"!\[(?P<alt>[^\]]*)\]\[(?P<label>[^\]]*)\]"
)
_SHORTCUT_REFERENCE_IMAGE_USE_RE: Final[re.Pattern[str]] = re.compile(
    r"!\[(?P<label>[^\]]+)\](?![\[(])"
)
_REFERENCE_DEFINITION_RE: Final[re.Pattern[str]] = re.compile(
    r"(?m)^(?P<prefix>[ \t]{0,3}\[(?P<label>[^\]]+)\]:[ \t]*)(?P<target><[^>\n]+>|[^\s]+)"
)
_PAGE_FOOTER_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:[Pp]age\s*\d{1,4}|第\s*\d{1,4}\s*页|[·|｜]\s*\d{1,4}|[-—–]?\s*\d{1,4}(?:\s*[-—–])?)\s*$"
)
_PAGE_BOUNDARY_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*(?:\f|<!--\s*(?:page(?:[_ -]?(?:num(?:ber)?)?)?|页)\s*[:=]?\s*\d+.*?-->)\s*$",
    re.IGNORECASE,
)
_CHAPTER_HEADING_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?P<marks>#{1,2})[ \t]+(?P<title>第[一二三四五六七八九十百千零〇0-9]+[章节篇部](?:[ \t:：、.．—-]+.+|$))\s*$"
)
_HEADING_RE: Final[re.Pattern[str]] = re.compile(r"^#{1,6}[ \t]+(?P<title>.+?)\s*$")
_CONVERSION_TEMPLATE: Final[Path] = (
    Path(__file__).resolve().parents[1]
    / "templates"
    / "ingestion"
    / "conversion-manifest.json"
)
_PACKAGE_TEMPLATES: Final[Path] = Path(__file__).resolve().parents[1] / "templates"
_PACKAGE_SOURCE_STATE_RE: Final[re.Pattern[str]] = re.compile(
    r"<!--\s*source-state:\s*[^>]*-->\s*\n?", re.IGNORECASE
)
_LIST_BLOCK_RE: Final[re.Pattern[str]] = re.compile(r"^\s*(?:[-+*]\s+|\d+[.)]\s+)")
_SETEXT_UNDERLINE_RE: Final[re.Pattern[str]] = re.compile(r"^\s*[=-]{2,}\s*$")
_TABLE_DELIMITER_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*\|?\s*:?-+:?\s*(?:\|\s*:?-+:?\s*)+\|?\s*$"
)
_FENCE_OPEN_RE: Final[re.Pattern[str]] = re.compile(r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})")
_HTML_BLOCK_OPEN_RE: Final[re.Pattern[str]] = re.compile(
    r"^[ \t]*<(?P<tag>address|article|aside|blockquote|div|figure|footer|header|"
    r"main|nav|ol|p|pre|script|section|style|table|textarea|ul|xmp)(?:\s|>|$)",
    re.IGNORECASE,
)


def _usable_mineru_binary(candidate: Path) -> Path | None:
    """Return an executable candidate, or ``None`` when it is unavailable."""

    try:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    except OSError:
        pass
    return None


def locate_mineru(explicit: Path | None, project_root: Path) -> Path:
    """Locate MinerU using explicit, environment, PATH, and project-local options."""

    root = Path(project_root)
    candidates: list[Path] = []
    if explicit is not None:
        candidates.append(Path(explicit))

    configured = os.environ.get("MINERU_BIN")
    if configured:
        configured_path = Path(configured)
        candidates.append(
            configured_path if configured_path.is_absolute() else root / configured_path
        )

    path_binary = shutil.which("mineru")
    if path_binary:
        candidates.append(Path(path_binary))

    candidates.extend(
        (
            root / ".venv-mineru" / "bin" / "mineru",
            root / ".venv" / "bin" / "mineru",
        )
    )

    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        usable = _usable_mineru_binary(candidate)
        if usable is not None:
            return usable

    searched = ", ".join(str(path) for path in candidates if str(path)) or "(none)"
    raise IngestionError(f"MinerU executable not found; searched: {searched}")


def mineru_version(binary: Path) -> str:
    """Return the version reported by a MinerU executable."""

    try:
        completed = subprocess.run(
            [str(binary), "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            shell=False,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise IngestionError(f"Unable to query MinerU version: {exc}") from exc
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip() or "no diagnostic output"
        raise IngestionError(f"MinerU version check failed: {detail}")
    return (completed.stdout or completed.stderr).strip() or "unknown"


def build_mineru_command(
    binary: Path,
    pdf: Path,
    output: Path,
    backend: str,
    language: str,
) -> list[str]:
    """Build MinerU's explicit argument list without shell interpolation."""

    return [
        str(binary),
        "-p",
        str(pdf),
        "-o",
        str(output),
        "-b",
        str(backend),
        "-l",
        str(language),
    ]


def find_mineru_auto_dir(output_root: Path) -> Path:
    """Find a complete MinerU ``auto`` directory below an output root."""

    root = Path(output_root)
    if not root.is_dir():
        raise IngestionError(f"MinerU output directory does not exist: {root}")

    candidates: list[Path] = []
    if root.name == "auto":
        candidates.append(root)
    direct_auto = root / "auto"
    if direct_auto.is_dir():
        candidates.append(direct_auto)
    candidates.extend(path for path in sorted(root.glob("*/auto")) if path.is_dir())

    seen: set[Path] = set()
    for auto_dir in candidates:
        if auto_dir in seen:
            continue
        seen.add(auto_dir)
        has_markdown = any(path.is_file() for path in auto_dir.glob("*.md"))
        has_content_list = any(
            path.is_file() for path in auto_dir.glob("*_content_list_v2.json")
        )
        if has_markdown and has_content_list:
            return auto_dir

    raise IngestionError(
        f"MinerU output is incomplete under {root}: expected Markdown and *_content_list_v2.json in auto/"
    )


def run_mineru(config: IngestionConfig, staging_dir: Path) -> MinerUResult:
    """Run MinerU in a caller-provided staging directory and validate its output."""

    pdf = Path(config.pdf)
    if not pdf.is_file():
        raise IngestionError(f"PDF file does not exist: {pdf}")
    if config.timeout <= 0:
        raise IngestionError("MinerU timeout must be positive")

    stage = Path(staging_dir)
    stage.mkdir(parents=True, exist_ok=True)
    project_root = Path(config.work_root) if config.work_root is not None else Path.cwd()
    binary = locate_mineru(config.mineru_bin, project_root=project_root)
    version = mineru_version(binary)
    command = build_mineru_command(
        binary,
        pdf,
        stage,
        config.backend,
        config.language,
    )

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=config.timeout,
            shell=False,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise IngestionError(
            f"MinerU timed out after {config.timeout} seconds; staging retained at {stage}"
        ) from exc
    except (OSError, subprocess.SubprocessError) as exc:
        raise IngestionError(f"MinerU execution failed: {exc}") from exc

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    if completed.returncode != 0:
        detail = (stderr or stdout).strip() or "no diagnostic output"
        raise IngestionError(
            f"MinerU exited with status {completed.returncode}: {detail}"
        )

    auto_dir = find_mineru_auto_dir(stage)
    return MinerUResult(
        binary=binary,
        version=version,
        command=command,
        staging_dir=stage,
        auto_dir=auto_dir,
        stdout=stdout,
        stderr=stderr,
        returncode=completed.returncode,
    )


def safe_segment(value: str) -> str:
    """Validate and return one path segment without normalizing its spelling.

    Roots are supplied by the caller; this guard is for user-controlled
    category and title segments.  Both POSIX and Windows separators are
    rejected so the same validation is safe on either platform.
    """

    if not isinstance(value, str):
        raise TypeError("path segment must be a string")
    if not value or not value.strip():
        raise ValueError("path segment must not be blank")
    if "\x00" in value:
        raise ValueError("path segment must not contain NUL bytes")
    if value in {".", ".."}:
        raise ValueError("path segment must not be a traversal component")
    if "/" in value or "\\" in value:
        raise ValueError("path segment must not contain path separators")
    if PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute():
        raise ValueError("path segment must not be absolute")
    if PureWindowsPath(value).drive:
        raise ValueError("path segment must not contain a drive prefix")
    return value


def slugify_title(title: str) -> str:
    """Create a stable, path-safe slug while retaining Unicode letters.

    Whitespace becomes a single hyphen.  Unicode normalization makes visually
    equivalent full-width forms deterministic; punctuation and symbols are
    discarded.  ``str.isalnum`` intentionally keeps Chinese and other
    non-ASCII letters and digits.
    """

    if not isinstance(title, str):
        raise TypeError("title must be a string")

    normalized = unicodedata.normalize("NFKC", title)
    pieces: list[str] = []
    for char in normalized:
        if char.isspace():
            pieces.append("-")
        elif char.isalnum() or char == "-":
            pieces.append(char)

    slug = _HYPHEN_RE.sub("-", "".join(pieces)).strip("-")
    if not slug:
        raise ValueError("title must contain at least one usable character")
    return slug


def build_output_paths(
    markdown_root: Path,
    books_root: Path,
    category: str,
    title: str,
) -> OutputPaths:
    """Build canonical Markdown and deep-reading package directories."""

    category_segment = safe_segment(category)
    title_segment = safe_segment(title)
    slug = slugify_title(title_segment)
    return OutputPaths(
        markdown_dir=Path(markdown_root) / category_segment / title_segment,
        book_dir=Path(books_root) / slug,
        category=category_segment,
        title=title_segment,
        slug=slug,
    )


def sha256_file(path: Path) -> str:
    """Return the lowercase SHA-256 digest of a file."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_text(path: Path, text: str) -> None:
    """Write UTF-8 text through a sibling temporary file and replace atomically."""

    target = Path(path)
    parent = target.parent
    parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{target.name}.", suffix=".tmp", dir=parent
        )
        temporary = Path(temporary_name)
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as output:
            output.write(text)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, target)
        temporary = None
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def write_json(path: Path, payload: dict[str, object]) -> None:
    """Serialize a JSON object deterministically using an atomic text write."""

    if not isinstance(payload, dict):
        raise TypeError("JSON payload must be a dictionary")
    atomic_write_text(
        path,
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )


def read_json(path: Path) -> dict[str, object]:
    """Read a JSON object and reject non-object top-level values."""

    with Path(path).open("r", encoding="utf-8") as source:
        payload = json.load(source)
    if not isinstance(payload, dict):
        raise ValueError("JSON document must contain an object")
    return payload


def _markdown_target_key(target: str) -> str | None:
    """Return a normalized local ``images/`` target, if ``target`` is one."""

    value = target.strip()
    if value.startswith("<") and value.endswith(">"):
        value = value[1:-1]
    value = value.replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    if not value.startswith("images/"):
        return None
    relative = PurePosixPath(value).relative_to("images")
    if any(part in {"", ".", ".."} for part in relative.parts):
        return None
    return "images/" + relative.as_posix()


def _collision_safe_destination(destination: Path, source: Path) -> Path:
    """Choose a deterministic image destination without overwriting another image."""

    if not destination.exists() or sha256_file(destination) == sha256_file(source):
        return destination
    digest = sha256_file(source)[:12]
    candidate = destination.with_name(
        f"{destination.stem}--{digest}{destination.suffix}"
    )
    if not candidate.exists() or sha256_file(candidate) == sha256_file(source):
        return candidate
    raise IngestionError(f"Unable to make a collision-safe image name for {source}")


def _copy_mineru_images(auto_dir: Path, destination_dir: Path) -> dict[str, str]:
    """Copy MinerU images and return source-reference to output-reference mappings."""

    source_dir = auto_dir / "images"
    if not source_dir.is_dir():
        return {}

    mappings: dict[str, str] = {}
    for source in sorted(path for path in source_dir.rglob("*") if path.is_file()):
        relative = source.relative_to(source_dir)
        target = _collision_safe_destination(destination_dir / relative, source)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)
        mappings["images/" + relative.as_posix()] = (
            "images/" + target.relative_to(destination_dir).as_posix()
        )
    return mappings


def _rewrite_image_paths(raw_text: str, mappings: dict[str, str]) -> str:
    """Rewrite only local MinerU image targets in otherwise untouched Markdown."""

    def replace(match: re.Match[str]) -> str:
        target = match.group("target")
        key = _markdown_target_key(target)
        rewritten = mappings.get(key) if key is not None else None
        if rewritten is None:
            return match.group(0)
        if target.startswith("<") and target.endswith(">"):
            rewritten = f"<{rewritten}>"
        return match.group(1) + rewritten

    return _IMAGE_TARGET_RE.sub(replace, raw_text)


def _rewrite_chapter_image_paths(
    chapter_text: str, chapter_path: Path, output_dir: Path
) -> str:
    """Make output-root image references resolve from a split chapter file."""

    def replace(match: re.Match[str]) -> str:
        target = match.group("target")
        key = _markdown_target_key(target)
        if key is None:
            return match.group(0)
        image_path = Path(output_dir) / Path(PurePosixPath(key))
        relative = os.path.relpath(image_path, start=chapter_path.parent).replace(os.sep, "/")
        if target.startswith("<") and target.endswith(">"):
            relative = f"<{relative}>"
        return match.group(1) + relative

    return _IMAGE_TARGET_RE.sub(replace, chapter_text)


def _find_raw_markdown(auto_dir: Path) -> Path:
    """Find the one primary Markdown document in a complete MinerU auto directory."""

    candidates = sorted(path for path in auto_dir.glob("*.md") if path.is_file())
    if len(candidates) != 1:
        raise IngestionError(
            f"Expected exactly one top-level MinerU Markdown file in {auto_dir}; found {len(candidates)}"
        )
    return candidates[0]


def _copy_mineru_json(auto_dir: Path, destination_dir: Path) -> list[str]:
    """Preserve all MinerU JSON artifacts under the conversion directory."""

    copied: list[str] = []
    has_content_list = False
    for source in sorted(path for path in auto_dir.rglob("*.json") if path.is_file()):
        relative = source.relative_to(auto_dir)
        target = _collision_safe_destination(destination_dir / relative, source)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)
        copied.append(target.relative_to(destination_dir).as_posix())
        has_content_list = has_content_list or source.name.endswith("_content_list_v2.json")
    if not has_content_list:
        raise IngestionError(f"MinerU content-list JSON is missing from {auto_dir}")
    return copied


def import_mineru_output(
    config: IngestionConfig, auto_dir: Path, mineru_version: str
) -> ConversionResult:
    """Import raw MinerU artifacts without applying editorial transformations.

    The sole permitted Markdown alteration is deterministic repair of local
    image targets when an existing output image requires a collision-safe name.
    """

    source_auto = Path(auto_dir)
    if not source_auto.is_dir():
        raise IngestionError(f"MinerU auto directory does not exist: {source_auto}")
    raw_source = _find_raw_markdown(source_auto)
    output_dir = config.paths.markdown_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    image_mappings = _copy_mineru_images(source_auto, output_dir / "images")
    with raw_source.open("r", encoding="utf-8", newline="") as source:
        raw_text = source.read()
    raw_path = output_dir / f"{config.paths.title}.md"
    atomic_write_text(raw_path, _rewrite_image_paths(raw_text, image_mappings))
    mineru_json = _copy_mineru_json(source_auto, output_dir / "mineru")

    manifest = read_json(_CONVERSION_TEMPLATE)
    book = manifest["book"]
    source = manifest["source"]
    engine = manifest["engine"]
    stages = manifest["stages"]
    resources = manifest["resources"]
    if not all(isinstance(value, dict) for value in (book, source, engine, stages, resources)):
        raise IngestionError("Conversion manifest template has an invalid shape")
    book.update({"title": config.paths.title, "category": config.paths.category, "language": config.language})
    source.update(
        {
            "pdf": str(config.pdf),
            "sha256": sha256_file(config.pdf) if Path(config.pdf).is_file() else "",
            "auto_dir": str(source_auto),
        }
    )
    engine.update({"name": "MinerU", "version": mineru_version})
    stages.update({"imported": True})
    resources.update(
        {
            "images": sorted(image_mappings.values()),
            "mineru_json": mineru_json,
        }
    )
    manifest_path = output_dir / "conversion-manifest.json"
    write_json(manifest_path, manifest)
    return ConversionResult(raw_path=raw_path, manifest_path=manifest_path, manifest=manifest)


def _page_edge_line_indexes(lines: list[str]) -> set[int]:
    """Return first/last body lines of pages marked by explicit page boundaries."""

    boundaries = [
        index for index, line in enumerate(lines) if _PAGE_BOUNDARY_RE.fullmatch(line)
    ]
    edges: set[int] = set()
    for position, boundary in enumerate(boundaries):
        next_boundary = boundaries[position + 1] if position + 1 < len(boundaries) else len(lines)
        body_lines = [
            index
            for index in range(boundary + 1, next_boundary)
            if lines[index].strip()
        ]
        if body_lines:
            edges.add(body_lines[0])
            edges.add(body_lines[-1])
    return edges


def _repeated_header_footer_lines(lines: list[str], page_edges: set[int]) -> set[str]:
    """Identify repeated short labels only when page boundaries support the repair."""

    counts: dict[str, int] = {}
    for index in page_edges:
        normalized = lines[index].strip()
        if normalized and len(normalized) <= 80:
            counts[normalized] = counts.get(normalized, 0) + 1

    repeated: set[str] = set()
    for index in page_edges:
        normalized = lines[index].strip()
        is_label = (
            counts.get(normalized, 0) >= 2
            and not normalized.startswith("#")
            and not normalized.startswith("![")
            and not re.search(r"[。！？!?；;：:，,]$", normalized)
        )
        if is_label:
            repeated.add(normalized)
    return repeated


def format_markdown(raw_text: str) -> tuple[str, list[dict[str, str]]]:
    """Apply only auditable structural repairs to raw conversion Markdown."""

    lines = raw_text.splitlines(keepends=True)
    plain_lines = [line.rstrip("\r\n") for line in lines]
    page_edges = _page_edge_line_indexes(plain_lines)
    repeated_labels = _repeated_header_footer_lines(plain_lines, page_edges)
    retained: list[str] = []
    changes: list[dict[str, str]] = []
    for index, (line, plain) in enumerate(zip(lines, plain_lines)):
        stripped = plain.strip()
        if index in page_edges and stripped and _PAGE_FOOTER_RE.fullmatch(stripped):
            changes.append({"type": "removed_page_footer", "text": plain})
            continue
        if index in page_edges and stripped in repeated_labels:
            changes.append({"type": "removed_repeated_header_footer", "text": plain})
            continue
        retained.append(line)

    index = 0
    repaired: list[str] = []
    while index < len(retained):
        line = retained[index]
        if (
            line.endswith(("-\n", "-\r\n"))
            and index + 1 < len(retained)
            and re.search(r"[A-Za-z]-\r?\n$", line)
            and re.match(r"[a-z]", retained[index + 1])
        ):
            repaired.append(re.sub(r"-\r?\n$", "", line) + retained[index + 1])
            changes.append({"type": "repaired_hyphenated_line_wrap", "text": line.rstrip("\r\n")})
            index += 2
            continue
        repaired.append(line)
        index += 1
    return "".join(repaired), changes


def _heading_title(line: str) -> str | None:
    """Return a Markdown heading title, preserving no formatting syntax."""

    match = _HEADING_RE.match(line.rstrip("\r\n"))
    return match.group("title").strip() if match else None


def _chapter_filename(index: int, heading: str) -> str:
    """Create a portable chapter filename from a trusted chapter heading."""

    safe_heading = re.sub(r'[<>:"/\\|?*]', "-", heading).strip(" .")
    return f"{index:02d}-{safe_heading or '章节'}.md"


def split_chapters(formatted_text: str, output_dir: Path, title: str) -> list[Path]:
    """Split only H1/H2 chapter headings outside an explicit contents region."""

    lines = formatted_text.splitlines(keepends=True)
    chapter_starts: list[tuple[int, str]] = []
    in_contents = False
    contents_heading_level: int | None = None
    for index, line in enumerate(lines):
        heading = _heading_title(line)
        if heading is not None:
            compact = heading.casefold().replace(" ", "")
            if compact in {"目录", "contents", "tableofcontents"}:
                in_contents = True
                contents_heading_level = len(line) - len(line.lstrip("#"))
                continue
            if in_contents and compact in {"正文", "前言", "序言", "引言", "开始阅读"}:
                in_contents = False
                contents_heading_level = None
                continue
        match = _CHAPTER_HEADING_RE.match(line.rstrip("\r\n"))
        if match and in_contents:
            chapter_level = len(match.group("marks"))
            if contents_heading_level is None or chapter_level > contents_heading_level:
                continue
            in_contents = False
            contents_heading_level = None
        if match:
            chapter_starts.append((index, match.group("title").strip()))

    split_root = Path(output_dir) / "拆分"
    chapters_dir = split_root / "章节"
    chapters_dir.mkdir(parents=True, exist_ok=True)
    chapter_paths: list[Path] = []
    for number, (start, heading) in enumerate(chapter_starts, start=1):
        end = chapter_starts[number][0] if number < len(chapter_starts) else len(lines)
        chapter_path = chapters_dir / _chapter_filename(number, heading)
        chapter_text = _rewrite_chapter_image_paths(
            "".join(lines[start:end]), chapter_path, Path(output_dir)
        )
        atomic_write_text(chapter_path, chapter_text)
        chapter_paths.append(chapter_path)

    chapter_links = "\n".join(
        f"- [{path.stem}](章节/{path.name})" for path in chapter_paths
    ) or "- 未识别到可高置信拆分的章节。"
    atomic_write_text(split_root / "README.md", f"# {title} 拆分目录\n\n{chapter_links}\n")
    chapter_index = "\n".join(
        f"- [{path.stem}]({path.name})" for path in chapter_paths
    ) or "- 未识别到可高置信拆分的章节。"
    atomic_write_text(chapters_dir / "README.md", f"# {title} 章节\n\n{chapter_index}\n")
    return chapter_paths


def collect_markdown_links(path: Path) -> list[str]:
    """Return local and remote Markdown image targets in source order."""

    with Path(path).open("r", encoding="utf-8", newline="") as source:
        text = source.read()
    return [match.group("target") for match in _IMAGE_TARGET_RE.finditer(text)]


def _local_image_target(target: str) -> str | None:
    """Return a filesystem-relative image target, excluding remote resources."""

    value = target.strip()
    if value.startswith("<") and value.endswith(">"):
        value = value[1:-1]
    if not value or value.startswith("#"):
        return None
    local = value.split("#", 1)[0].split("?", 1)[0]
    if re.match(r"^[A-Za-z]:[\\/]", local) or local.startswith(("\\\\", "//")):
        return local
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", local):
        return None
    return local


def validate_conversion(output_dir: Path) -> ValidationReport:
    """Validate that every local Markdown image reference resolves to a file."""

    root = Path(output_dir)
    issues: list[ValidationIssue] = []
    if not root.is_dir():
        issues.append(
            ValidationIssue(
                code="missing_output_directory",
                message=f"Conversion output directory does not exist: {root}",
                path=root,
            )
        )
    else:
        for markdown in sorted(root.rglob("*.md")):
            for target in collect_markdown_links(markdown):
                local = _local_image_target(target)
                if local is None:
                    continue
                target_path = markdown.parent / Path(PurePosixPath(local.replace("\\", "/")))
                if not target_path.is_file():
                    issues.append(
                        ValidationIssue(
                            code="missing_image",
                            message=f"Missing image '{target}' referenced by {markdown.name}",
                            path=target_path,
                        )
                    )
    blocking_count = len(issues)
    return ValidationReport(
        status="valid" if blocking_count == 0 else "invalid",
        issues=tuple(issues),
        blocking_count=blocking_count,
    )


def add_stable_paragraph_ids(markdown: str, chapter_id: str) -> str:
    """Insert deterministic paragraph locator comments without changing Markdown."""

    if not re.fullmatch(r"ch\d{2,}", chapter_id):
        raise IngestionError(f"Invalid chapter ID: {chapter_id}")
    source = _PACKAGE_SOURCE_STATE_RE.sub("", markdown)
    rendered: list[str] = [f"<!-- source-state: staging -->\n", f"<!-- chapter: {chapter_id} -->\n"]
    paragraph_number = 0
    for value, is_block in _markdown_source_chunks(source):
        if is_block and _is_source_paragraph(value):
            paragraph_number += 1
            rendered.append(f"<!-- locator: {chapter_id}-p{paragraph_number:03d} -->\n")
        rendered.append(value)
    return "".join(rendered)


def _markdown_source_chunks(source: str) -> list[tuple[str, bool]]:
    """Split only safe top-level blocks while preserving every source character."""

    chunks: list[tuple[str, bool]] = []
    current: list[str] = []
    fence: tuple[str, int] | None = None
    html_tag: str | None = None
    literal_close: str | None = None
    for line in source.splitlines(keepends=True):
        if fence is not None:
            current.append(line)
            marker, length = fence
            if re.match(rf"^[ \t]{{0,3}}{re.escape(marker)}{{{length},}}[ \t]*$", line.rstrip("\r\n")):
                fence = None
            continue
        if literal_close is not None:
            current.append(line)
            if literal_close in line:
                literal_close = None
            continue
        if html_tag is not None:
            current.append(line)
            if re.search(rf"</{re.escape(html_tag)}\s*>", line, re.IGNORECASE):
                html_tag = None
            continue
        literal_close = _multiline_literal_close(line)
        if literal_close is not None:
            current.append(line)
            if literal_close in line:
                literal_close = None
            continue
        fence_match = _FENCE_OPEN_RE.match(line)
        if fence_match:
            current.append(line)
            marker = fence_match.group("fence")[0]
            fence = (marker, len(fence_match.group("fence")))
            continue
        html_match = _HTML_BLOCK_OPEN_RE.match(line)
        if html_match:
            current.append(line)
            tag = html_match.group("tag")
            if not re.search(rf"</{re.escape(tag)}\s*>", line, re.IGNORECASE):
                html_tag = tag
            continue
        if not line.strip():
            if current:
                chunks.append(("".join(current), True))
                current = []
            chunks.append((line, False))
            continue
        current.append(line)
    if current:
        chunks.append(("".join(current), True))
    return chunks


def _multiline_literal_close(line: str) -> str | None:
    """Return the required terminator for a multiline non-Markdown literal."""

    stripped = line.lstrip()
    if stripped.startswith("<!--"):
        return "-->"
    if stripped.startswith("<![CDATA["):
        return "]]" + ">"
    if stripped.startswith("<?"):
        return "?>"
    if stripped.startswith("<!"):
        return "]>" if "[" in stripped else ">"
    return None


def _is_source_paragraph(block: str) -> bool:
    """Recognize only unambiguous top-level prose for locator insertion."""

    if not block or block[0] in " \t":
        return False
    value = block.strip()
    if not value or value.startswith(("#", "<!--", "![", "<", "```", "~~~", ">")):
        return False
    lines = value.splitlines()
    if _LIST_BLOCK_RE.match(value) or any(line.startswith(("    ", "\t")) for line in lines):
        return False
    if len(lines) >= 2 and _SETEXT_UNDERLINE_RE.fullmatch(lines[1]):
        return False
    return not any(_TABLE_DELIMITER_RE.fullmatch(line) for line in lines)


def _resolve_chapter_asset(
    target: str, conversion_dir: Path, chapter_source: Path
) -> tuple[Path, Path] | None:
    """Resolve a local image relative to its chapter and constrain it to conversion."""

    local = _local_image_target(target)
    if local is None:
        return None
    normalized = local.replace("\\", "/")
    posix = PurePosixPath(normalized)
    windows = PureWindowsPath(normalized)
    if posix.is_absolute() or windows.is_absolute() or windows.drive:
        raise IngestionError(f"Absolute chapter image path is not allowed: {target}")
    conversion_root = Path(conversion_dir).resolve()
    resolved = (Path(chapter_source).parent / Path(posix)).resolve()
    try:
        relative = resolved.relative_to(conversion_root)
    except ValueError as exc:
        raise IngestionError(f"Chapter image path escapes conversion directory: {target}") from exc
    if not resolved.is_file():
        raise IngestionError(f"Referenced conversion image is missing: {resolved}")
    return resolved, relative


def _reference_image_labels(markdown: str) -> set[str]:
    """Return normalized labels used by reference-style Markdown images."""

    labels: set[str] = set()
    for match in _REFERENCE_IMAGE_USE_RE.finditer(markdown):
        label = match.group("label") or match.group("alt")
        normalized = " ".join(label.split()).casefold()
        if normalized:
            labels.add(normalized)
    for match in _SHORTCUT_REFERENCE_IMAGE_USE_RE.finditer(markdown):
        normalized = " ".join(match.group("label").split()).casefold()
        if normalized:
            labels.add(normalized)
    return labels


def _reference_image_targets(markdown: str) -> list[str]:
    """Return targets from definitions referenced by a Markdown image."""

    labels = _reference_image_labels(markdown)
    return [
        match.group("target")
        for match in _REFERENCE_DEFINITION_RE.finditer(markdown)
        if " ".join(match.group("label").split()).casefold() in labels
    ]


def _chapter_asset_mapping(
    markdown: str, conversion_dir: Path, chapter_source: Path
) -> dict[str, tuple[Path, Path]]:
    """Validate and map every local chapter image reference before writes begin."""

    mapping: dict[str, tuple[Path, Path]] = {}
    targets = [match.group("target") for match in _IMAGE_TARGET_RE.finditer(markdown)]
    targets.extend(_reference_image_targets(markdown))
    for target in targets:
        resolved = _resolve_chapter_asset(target, conversion_dir, chapter_source)
        if resolved is not None:
            mapping[target] = resolved
    return mapping


def copy_chapter_assets(
    markdown: str,
    conversion_dir: Path,
    chapter_dir: Path,
    chapter_source: Path | None = None,
) -> str:
    """Copy only locally referenced conversion images and rewrite their links."""

    source_path = Path(chapter_source) if chapter_source is not None else Path(conversion_dir)
    mapping = _chapter_asset_mapping(markdown, conversion_dir, source_path)
    assets_dir = Path(chapter_dir) / "assets"

    def replace(match: re.Match[str]) -> str:
        target = match.group("target")
        resolved = mapping.get(target)
        if resolved is None:
            return match.group(0)
        return match.group(1) + _asset_rewrite_target(target, resolved, assets_dir)

    def replace_reference_definition(match: re.Match[str]) -> str:
        label = " ".join(match.group("label").split()).casefold()
        if label not in _reference_image_labels(markdown):
            return match.group(0)
        target = match.group("target")
        resolved = mapping.get(target)
        if resolved is None:
            return match.group(0)
        return match.group("prefix") + _asset_rewrite_target(target, resolved, assets_dir)

    rewritten = _IMAGE_TARGET_RE.sub(replace, markdown)
    return _REFERENCE_DEFINITION_RE.sub(replace_reference_definition, rewritten)


def _asset_rewrite_target(
    target: str, resolved: tuple[Path, Path], assets_dir: Path
) -> str:
    """Copy one prevalidated asset and return its chapter-local Markdown target."""

    source, conversion_relative = resolved
    asset_relative = conversion_relative
    if asset_relative.parts and asset_relative.parts[0] == "images":
        asset_relative = Path(*asset_relative.parts[1:])
    destination = _collision_safe_destination(assets_dir / asset_relative, source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        shutil.copy2(source, destination)
    rewritten = "assets/" + destination.relative_to(assets_dir).as_posix()
    if target.startswith("<") and target.endswith(">"):
        rewritten = f"<{rewritten}>"
    return rewritten


def _required_manifest_object(manifest: dict[str, object], name: str) -> dict[str, object]:
    value = manifest.get(name)
    if not isinstance(value, dict):
        raise IngestionError(f"Conversion manifest is missing object: {name}")
    return value


def _require_conversion_gate(conversion_dir: Path) -> tuple[dict[str, object], Path]:
    """Load a conversion manifest only when its recorded validation gate passed."""

    manifest_path = Path(conversion_dir) / "conversion-manifest.json"
    if not manifest_path.is_file():
        raise IngestionError(f"Conversion manifest does not exist: {manifest_path}")
    manifest = read_json(manifest_path)
    validation = _required_manifest_object(manifest, "validation")
    blocking_count = validation.get("blocking_count")
    if (
        validation.get("status") != "passed"
        or not isinstance(blocking_count, int)
        or isinstance(blocking_count, bool)
        or blocking_count != 0
    ):
        raise IngestionError("Conversion validation gate has not passed with zero blocking issues")
    return manifest, manifest_path


def _template_values(
    title: str,
    slug: str,
    language: str,
    pdf_path: str,
    pdf_hash: str,
    imported_at: str,
) -> dict[str, str]:
    return {
        "__BOOK_SLUG__": slug,
        "__TITLE__": title,
        "__AUTHOR__": "Unknown",
        "__EDITION__": "Unknown",
        "__LANGUAGE__": language or "unknown",
        "__ISBN_OR_EMPTY__": "",
        "__YEAR__": "",
        "__FORMAT__": "pdf",
        "__SOURCE_FILE__": pdf_path,
        "__AUTHORIZATION__": "user_provided",
        "__AUTHORIZATION_NOTE__": "Imported from a validated conversion.",
        "__PROFILE__": "deep-reading",
        "__RATIONALE__": "Initialized from a validated PDF conversion.",
        "__STATUS__": "in_progress",
        "__PASS__": "0",
        "__COVERAGE_SUMMARY__": "0 chapters reviewed",
        "__BLOCKING_COUNT__": "0",
        "__SCOPE_AND_AUTHORIZATION_NOTE__": "User-provided PDF; source remains staging.",
        "__ISO_8601__": imported_at,
        "__SOURCE_PDF_SHA256__": pdf_hash,
        "__INGESTION_TYPE__": "MinerU",
        "__INGESTION_PARSER__": "unknown",
        "__CONVERSION_DIR__": "",
        "__CONVERSION_MANIFEST__": "",
        "__GATE_STATUS__": "passed",
    }


def _render_template(text: str, values: dict[str, str]) -> str:
    """Render Markdown templates, using JSON strings for YAML scalar safety."""

    for token, value in values.items():
        text = text.replace(token, value)
    return text


def _render_yaml_template(text: str, values: dict[str, str]) -> str:
    """Render dynamic YAML scalars as JSON strings, valid YAML without injection."""

    for token, value in values.items():
        encoded = json.dumps(value, ensure_ascii=False)
        text = text.replace(f'"{token}"', encoded)
        text = text.replace(f"'{token}'", encoded)
        text = text.replace(token, encoded)
    return text


def _recorded_package_pdf_hash(package: Path) -> str | None:
    manifest = package / "manifest.yaml"
    if not manifest.is_file():
        return None
    try:
        text = manifest.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise IngestionError(f"Unable to read existing package manifest: {manifest}") from exc
    match = re.search(r"^\s*source_pdf_sha256:\s*['\"]?([^\s'\"]+)", text, re.MULTILINE)
    if match:
        return match.group(1)
    match = re.search(r"^\s*source_sha256:\s*['\"]?([^\s'\"]+)", text, re.MULTILINE)
    return match.group(1) if match else None


def _copy_rendered_templates(
    source_dir: Path,
    destination_dir: Path,
    values: dict[str, str],
    literal_values: dict[str, str] | None = None,
) -> None:
    for source in sorted(path for path in source_dir.rglob("*") if path.is_file()):
        target = destination_dir / source.relative_to(source_dir)
        template = source.read_text(encoding="utf-8")
        rendered = (
            _render_yaml_template(template, values)
            if target.suffix == ".yaml"
            else _render_template(template, values)
        )
        if literal_values:
            for token, value in literal_values.items():
                rendered = rendered.replace(token, value)
        atomic_write_text(target, rendered)


def _conversion_chapters(conversion_dir: Path) -> list[Path]:
    chapters_dir = Path(conversion_dir) / "拆分" / "章节"
    chapters = [path for path in sorted(chapters_dir.glob("*.md")) if path.name != "README.md"]
    if chapters:
        return chapters
    raw = sorted(path for path in Path(conversion_dir).glob("*.md") if path.is_file())
    if len(raw) == 1:
        return raw
    raise IngestionError("No conversion chapter Markdown files are available for package initialization")


def initialize_book_package(
    conversion_dir: Path, books_root: Path, templates_root: Path | None = None
) -> Path:
    """Initialize a staging reading package from a conversion that passed its gate."""

    conversion_root = Path(conversion_dir)
    manifest, conversion_manifest = _require_conversion_gate(conversion_root)
    book = _required_manifest_object(manifest, "book")
    source = _required_manifest_object(manifest, "source")
    engine = _required_manifest_object(manifest, "engine")
    title = book.get("title")
    pdf_path = source.get("pdf")
    pdf_hash = source.get("sha256")
    if not isinstance(title, str) or not title.strip():
        raise IngestionError("Conversion manifest has no book title")
    if not isinstance(pdf_path, str) or not pdf_path:
        raise IngestionError("Conversion manifest has no source PDF path")
    if not isinstance(pdf_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", pdf_hash):
        raise IngestionError("Conversion manifest has no valid source PDF SHA-256")
    language = book.get("language") if isinstance(book.get("language"), str) else "unknown"
    templates = Path(templates_root) if templates_root is not None else _PACKAGE_TEMPLATES
    for required in (templates / "book", templates / "chapter", templates / "synthesis"):
        if not required.is_dir():
            raise IngestionError(f"Package template directory does not exist: {required}")
    chapter_plans: list[tuple[str, Path, str]] = []
    for number, chapter_source in enumerate(_conversion_chapters(conversion_root), start=1):
        content = chapter_source.read_text(encoding="utf-8")
        if not content.strip():
            raise IngestionError(f"Conversion chapter is empty: {chapter_source}")
        _chapter_asset_mapping(content, conversion_root, chapter_source)
        chapter_plans.append((f"ch{number:02d}", chapter_source, content))

    slug = slugify_title(title)
    package = Path(books_root) / slug
    if package.exists():
        existing_hash = _recorded_package_pdf_hash(package)
        if existing_hash != pdf_hash:
            raise IngestionError("Existing package records a different or unknown source PDF SHA-256")
        expected_sources = [package / "chapters" / chapter_id / "source.md" for chapter_id, _, _ in chapter_plans]
        if (package / "manifest.yaml").is_file() and all(path.is_file() for path in expected_sources):
            return package
        raise IngestionError("Existing package with matching PDF hash is incomplete; refusing partial overwrite")

    imported_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    values = _template_values(title, slug, language, pdf_path, pdf_hash, imported_at)
    values.update(
        {
            "__INGESTION_PARSER__": f"{engine.get('name', 'unknown')} {engine.get('version', '')}".strip(),
            "__CONVERSION_DIR__": str(conversion_root),
            "__CONVERSION_MANIFEST__": str(conversion_manifest),
        }
    )
    books_root_path = Path(books_root)
    books_root_path.mkdir(parents=True, exist_ok=True)
    staging_root = Path(tempfile.mkdtemp(prefix=f".{slug}.", dir=books_root_path))
    staging_package = staging_root / slug
    try:
        staging_package.mkdir()
        _copy_rendered_templates(templates / "book", staging_package, values)
        _copy_rendered_templates(templates / "synthesis", staging_package / "synthesis", values)
        for chapter_id, chapter_source, content in chapter_plans:
            chapter_dir = staging_package / "chapters" / chapter_id
            chapter_title = _heading_title(content.splitlines()[0]) if content.splitlines() else None
            _copy_rendered_templates(
                templates / "chapter",
                chapter_dir,
                values,
                literal_values={"chNN": chapter_id, "__CHAPTER_TITLE__": chapter_title or chapter_source.stem},
            )
            copied = copy_chapter_assets(content, conversion_root, chapter_dir, chapter_source)
            atomic_write_text(chapter_dir / "source.md", add_stable_paragraph_ids(copied, chapter_id))
        os.replace(staging_package, package)
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)
    return package
