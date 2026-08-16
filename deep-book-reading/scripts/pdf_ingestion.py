"""Deterministic MinerU execution, conversion, and publication primitives.

The module owns source fingerprinting, MinerU invocation, staged conversion,
Gate P validation, and safe deep-reading package initialization.
"""

import ctypes
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Final


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
    conflict_policy: str = "reject"

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
class SourceFingerprint:
    """Stable source identity captured immediately around external execution."""

    path: Path
    sha256: str
    size: int
    mtime_ns: int
    captured_at: str


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
    source_fingerprint: SourceFingerprint
    started_at: str
    completed_at: str
    returncode: int = 0

    @property
    def output_dir(self) -> Path:
        """Compatibility name for callers referring to the staging output root."""

        return self.staging_dir


@dataclass(frozen=True)
class ConversionResult:
    """Imported MinerU assets and their conversion manifest."""

    raw_path: Path
    formatted_path: Path
    manifest_path: Path
    manifest: dict[str, object]
    reused: bool = False


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
_HTML_VOID_TAGS: Final[frozenset[str]] = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
)
_HTML_BLOCK_OPEN_RE: Final[re.Pattern[str]] = re.compile(
    r"^[ \t]*<(?P<tag>address|area|article|aside|base|basefont|blockquote|body|br|caption|"
    r"center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|"
    r"figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|img|input|"
    r"legend|li|link|main|menu|menuitem|meta|nav|noframes|ol|optgroup|option|p|"
    r"param|pre|script|search|section|source|style|summary|table|tbody|td|textarea|"
    r"tfoot|th|thead|title|tr|track|ul|wbr|xmp|embed)(?:\s|/?>|$)",
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

    source_fingerprint = fingerprint_source(config.pdf)
    pdf = source_fingerprint.path
    if config.timeout <= 0:
        raise IngestionError("MinerU timeout must be positive")

    stage = Path(staging_dir).expanduser().resolve()
    stage.mkdir(parents=True, exist_ok=True)
    project_root = Path(config.work_root) if config.work_root is not None else Path.cwd()
    binary = locate_mineru(config.mineru_bin, project_root=project_root).expanduser().resolve()
    version = mineru_version(binary)
    command = build_mineru_command(
        binary,
        pdf,
        stage,
        config.backend,
        config.language,
    )
    started_at = _utc_now()

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
    _require_unchanged_source(source_fingerprint, context="MinerU execution")
    completed_at = _utc_now()
    return MinerUResult(
        binary=binary,
        version=version,
        command=command,
        staging_dir=stage,
        auto_dir=auto_dir,
        stdout=stdout,
        stderr=stderr,
        source_fingerprint=source_fingerprint,
        started_at=started_at,
        completed_at=completed_at,
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


def _absolute_path(path: Path) -> Path:
    value = Path(path).expanduser()
    return value if value.is_absolute() else Path.cwd() / value


def _contained(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def prepare_publication_target(configured_root: Path, target: Path) -> Path:
    """Resolve a publication target beneath a non-symlinked configured root.

    Existing destination components are checked before directories are created.
    A symlink at any user-controlled component is rejected even when it resolves
    beneath the root, which keeps publication from following mutable aliases.
    """

    root = _absolute_path(configured_root)
    destination = _absolute_path(target)
    if root.is_symlink():
        raise IngestionError(f"Configured publication root may not be a symlink: {root}")
    try:
        root.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise IngestionError(f"Unable to create publication root {root}: {exc}") from exc
    if not root.is_dir():
        raise IngestionError(f"Configured publication root is not a directory: {root}")
    resolved_root = root.resolve()
    try:
        relative = destination.relative_to(root)
    except ValueError as exc:
        raise IngestionError(
            f"Publication target escapes configured root: {destination}"
        ) from exc
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise IngestionError(
                f"Symlinked publication component is not allowed: {current}"
            )
        if current.exists() and current != destination and not current.is_dir():
            raise IngestionError(
                f"Publication path component is not a directory: {current}"
            )
    resolved_destination = destination.resolve(strict=False)
    if not _contained(resolved_destination, resolved_root):
        raise IngestionError(
            f"Publication target resolves outside configured root: {destination}"
        )
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise IngestionError(
            f"Unable to create publication parent {destination.parent}: {exc}"
        ) from exc
    for parent in (destination.parent, destination):
        if parent.is_symlink():
            raise IngestionError(
                f"Symlinked publication component is not allowed: {parent}"
            )
    return destination


def _validated_directory_exchange_paths(
    staging: Path, target: Path
) -> tuple[Path, Path]:
    """Return existing sibling directories that an OS exchange may safely swap."""

    staged = Path(staging)
    destination = Path(target)
    try:
        if staged.is_symlink() or not staged.is_dir():
            raise IngestionError(f"Publication staging directory is invalid: {staged}")
        if destination.is_symlink() or not destination.is_dir():
            raise IngestionError(f"Publication target directory is invalid: {destination}")
        staged_resolved = staged.resolve(strict=True)
        destination_resolved = destination.resolve(strict=True)
        if staged_resolved == destination_resolved:
            raise IngestionError("Publication staging and target directories must differ")
        if staged_resolved.parent != destination_resolved.parent:
            raise IngestionError(
                "Publication staging directory must be a sibling of its target"
            )
        if staged_resolved.stat().st_dev != destination_resolved.stat().st_dev:
            raise IngestionError(
                "Publication staging and target directories must share a filesystem"
            )
    except IngestionError:
        raise
    except OSError as exc:
        raise IngestionError(
            f"Unable to validate atomic directory exchange paths: {exc}"
        ) from exc
    return staged_resolved, destination_resolved


def _exchange_failure(operation: str, error_number: int) -> IngestionError:
    detail = os.strerror(error_number) if error_number else "unknown operating-system error"
    return IngestionError(
        f"Atomic directory exchange via {operation} is unavailable or failed: "
        f"[errno {error_number}] {detail}"
    )


def _atomic_exchange_directories(staging: Path, target: Path) -> None:
    """Atomically exchange two existing directories or fail without mutation."""

    staged, destination = _validated_directory_exchange_paths(staging, target)
    try:
        libc = ctypes.CDLL(None, use_errno=True)
    except (OSError, TypeError) as exc:
        raise IngestionError(
            f"Atomic directory exchange is unavailable on {sys.platform}: {exc}"
        ) from exc

    staged_bytes = os.fsencode(staged)
    destination_bytes = os.fsencode(destination)
    if sys.platform == "darwin":
        try:
            renamex_np = libc.renamex_np
        except AttributeError as exc:
            raise IngestionError(
                "Atomic directory exchange is unavailable: renamex_np is missing"
            ) from exc
        renamex_np.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        renamex_np.restype = ctypes.c_int
        ctypes.set_errno(0)
        result = renamex_np(staged_bytes, destination_bytes, 0x00000002)
        if result != 0:
            raise _exchange_failure("renamex_np(RENAME_SWAP)", ctypes.get_errno())
        return

    if sys.platform.startswith("linux"):
        try:
            renameat2 = libc.renameat2
        except AttributeError as exc:
            raise IngestionError(
                "Atomic directory exchange is unavailable: renameat2 is missing"
            ) from exc
        renameat2.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        renameat2.restype = ctypes.c_int
        ctypes.set_errno(0)
        result = renameat2(
            -100,
            staged_bytes,
            -100,
            destination_bytes,
            0x00000002,
        )
        if result != 0:
            raise _exchange_failure("renameat2(RENAME_EXCHANGE)", ctypes.get_errno())
        return

    raise IngestionError(
        f"Atomic directory exchange is unsupported on platform: {sys.platform}"
    )


def atomic_publish_directory(staging: Path, target: Path) -> None:
    """Publish a sibling directory without making an existing target disappear."""

    staged = Path(staging)
    destination = Path(target)
    if staged.is_symlink() or not staged.is_dir():
        raise IngestionError(f"Publication staging directory is invalid: {staged}")
    if staged.parent.resolve() != destination.parent.resolve():
        raise IngestionError("Publication staging directory must be a sibling of its target")
    if destination.is_symlink():
        raise IngestionError(f"Publication target may not be a symlink: {destination}")
    if destination.exists() and not destination.is_dir():
        raise IngestionError(f"Publication target is not a directory: {destination}")

    if not destination.exists():
        try:
            os.replace(staged, destination)
        except OSError as exc:
            raise IngestionError(
                f"Unable to publish conversion directory {destination}: {exc}"
            ) from exc
        return

    _atomic_exchange_directories(staged, destination)
    try:
        shutil.rmtree(staged)
    except OSError as exc:
        raise IngestionError(
            f"Directory replacement published atomically at {destination}, but cleanup "
            f"of the previous generation at {staged} failed: {exc}"
        ) from exc


def sha256_file(path: Path) -> str:
    """Return the lowercase SHA-256 digest of a file."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _utc_now() -> str:
    """Return a second-precision UTC timestamp in the manifest vocabulary."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def fingerprint_source(path: Path) -> SourceFingerprint:
    """Resolve and fingerprint a PDF without trusting caller-supplied metadata."""

    source = Path(path).expanduser().resolve()
    if not source.is_file():
        raise IngestionError(f"PDF file does not exist: {source}")
    try:
        stat = source.stat()
        digest = sha256_file(source)
    except OSError as exc:
        raise IngestionError(f"Unable to fingerprint PDF {source}: {exc}") from exc
    return SourceFingerprint(
        path=source,
        sha256=digest,
        size=stat.st_size,
        mtime_ns=stat.st_mtime_ns,
        captured_at=_utc_now(),
    )


def _same_fingerprint(first: SourceFingerprint, second: SourceFingerprint) -> bool:
    return (
        first.path == second.path
        and first.sha256 == second.sha256
        and first.size == second.size
        and first.mtime_ns == second.mtime_ns
    )


def _require_unchanged_source(
    before: SourceFingerprint, *, context: str
) -> SourceFingerprint:
    after = fingerprint_source(before.path)
    if not _same_fingerprint(before, after):
        raise IngestionError(f"PDF changed during {context}: {before.path}")
    return after


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

    labels = _reference_image_labels(raw_text)

    def replace_definition(match: re.Match[str]) -> str:
        label = " ".join(match.group("label").split()).casefold()
        if label not in labels:
            return match.group(0)
        target = match.group("target")
        key = _markdown_target_key(target)
        rewritten = mappings.get(key) if key is not None else None
        if rewritten is None:
            return match.group(0)
        if target.startswith("<") and target.endswith(">"):
            rewritten = f"<{rewritten}>"
        return match.group("prefix") + rewritten

    rewritten = _substitute_outside_protected(
        raw_text, _IMAGE_TARGET_RE, replace
    )
    return _substitute_outside_protected(
        rewritten, _REFERENCE_DEFINITION_RE, replace_definition
    )


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

    labels = _reference_image_labels(chapter_text)

    def replace_definition(match: re.Match[str]) -> str:
        label = " ".join(match.group("label").split()).casefold()
        if label not in labels:
            return match.group(0)
        target = match.group("target")
        key = _markdown_target_key(target)
        if key is None:
            return match.group(0)
        image_path = Path(output_dir) / Path(PurePosixPath(key))
        relative = os.path.relpath(image_path, start=chapter_path.parent).replace(
            os.sep, "/"
        )
        if target.startswith("<") and target.endswith(">"):
            relative = f"<{relative}>"
        return match.group("prefix") + relative

    rewritten = _substitute_outside_protected(
        chapter_text, _IMAGE_TARGET_RE, replace
    )
    return _substitute_outside_protected(
        rewritten, _REFERENCE_DEFINITION_RE, replace_definition
    )


def _find_raw_markdown(auto_dir: Path) -> Path:
    """Find the one primary Markdown document in a complete MinerU auto directory."""

    candidates = sorted(path for path in auto_dir.glob("*.md") if path.is_file())
    if len(candidates) != 1:
        raise IngestionError(
            f"Expected exactly one top-level MinerU Markdown file in {auto_dir}; found {len(candidates)}"
        )
    return candidates[0]


def _file_record(path: Path, root: Path) -> dict[str, object]:
    file_path = Path(path)
    return {
        "path": file_path.relative_to(root).as_posix(),
        "sha256": sha256_file(file_path),
        "size": file_path.stat().st_size,
    }


def _copy_mineru_json(
    auto_dir: Path, destination_dir: Path, conversion_root: Path
) -> list[dict[str, object]]:
    """Preserve MinerU JSON with conversion-relative paths and provenance."""

    copied: list[dict[str, object]] = []
    has_content_list = False
    for source in sorted(path for path in auto_dir.rglob("*.json") if path.is_file()):
        relative = source.relative_to(auto_dir)
        target = _collision_safe_destination(destination_dir / relative, source)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)
        is_content_list = source.name.endswith("_content_list_v2.json")
        copied.append(
            {
                **_file_record(target, conversion_root),
                "source_path": relative.as_posix(),
                "kind": "content_list" if is_content_list else "mineru_json",
            }
        )
        has_content_list = has_content_list or is_content_list
    if not has_content_list:
        raise IngestionError(f"MinerU content-list JSON is missing from {auto_dir}")
    return copied


def _load_json_value(path: Path) -> Any:
    try:
        with Path(path).open("r", encoding="utf-8") as source:
            return json.load(source)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise IngestionError(f"MinerU JSON is unreadable or invalid: {path}: {exc}") from exc


def _page_number(record: object) -> int | None:
    """Return an explicit nonnegative page identity from a structured record."""

    if not isinstance(record, dict):
        return None
    for key in ("page_idx", "page_index", "page_id", "page_no", "page_number"):
        value = record.get(key)
        if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None


def _content_list_page_records(
    records: list[dict[str, object]], root: Path
) -> list[dict[str, int]]:
    counts: dict[int, int] = {}
    for record in records:
        if record.get("kind") != "content_list":
            continue
        path_value = record.get("path")
        if not isinstance(path_value, str):
            continue
        payload = _load_json_value(root / Path(PurePosixPath(path_value)))
        if isinstance(payload, dict) and isinstance(payload.get("pages"), list):
            items = payload["pages"]
            for item in items:
                page = _page_number(item)
                if page is None:
                    raise IngestionError(
                        f"MinerU content-list page entry lacks an explicit page identity: "
                        f"{path_value}"
                    )
                counts[page] = counts.get(page, 0) + 1
        elif isinstance(payload, list):
            for item in payload:
                page = _page_number(item)
                if page is None:
                    raise IngestionError(
                        f"MinerU content-list entry lacks an explicit page identity: "
                        f"{path_value}"
                    )
                counts[page] = counts.get(page, 0) + 1
        else:
            raise IngestionError(
                f"MinerU content-list must be a list or an object with a pages list: "
                f"{path_value}"
            )
    return [
        {"page_index": page, "record_count": counts[page]}
        for page in sorted(counts)
    ]


def _pdf_page_count(path: Path) -> int | None:
    """Return a conservative structural PDF page count when directly observable."""

    try:
        data = Path(path).read_bytes()
    except OSError:
        return None
    count = len(re.findall(rb"/Type\s*/Page\b", data))
    return count or None


def _stage(
    completed_at: str, outputs: list[dict[str, object]]
) -> dict[str, object]:
    return {"status": "complete", "completed_at": completed_at, "outputs": outputs}


def _existing_conversion(
    config: IngestionConfig,
    target: Path,
    fingerprint: SourceFingerprint,
    conflict_policy: str,
) -> ConversionResult | None:
    if not target.exists():
        return None
    manifest_path = target / "conversion-manifest.json"
    existing_hash: str | None = None
    manifest: dict[str, object] | None = None
    try:
        manifest = read_json(manifest_path)
        source = manifest.get("source")
        if isinstance(source, dict) and isinstance(source.get("sha256"), str):
            existing_hash = source["sha256"]
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        manifest = None

    if existing_hash is None:
        if conflict_policy != "replace":
            raise IngestionError(
                "Existing conversion has no trustworthy source identity; "
                "use conflict_policy='replace' only after verifying the target"
            )
        return None
    if existing_hash != fingerprint.sha256:
        if conflict_policy != "replace":
            raise IngestionError(
                "Existing conversion records a different PDF SHA-256; "
                "use an explicit safe replacement policy or a new title"
            )
        return None

    report = validate_conversion(target)
    if report.blocking_count:
        return None
    assert manifest is not None
    artifacts = manifest.get("artifacts")
    formatted_value = (
        artifacts.get("formatted_markdown") if isinstance(artifacts, dict) else None
    )
    formatted_path_value = (
        formatted_value.get("path") if isinstance(formatted_value, dict) else None
    )
    if not isinstance(formatted_path_value, str):
        return None
    book = manifest.get("book")
    title = book.get("title") if isinstance(book, dict) else None
    raw_value = artifacts.get("raw_markdown") if isinstance(artifacts, dict) else None
    raw_path_value = raw_value.get("path") if isinstance(raw_value, dict) else None
    if not isinstance(title, str) or not isinstance(raw_path_value, str):
        return None
    return ConversionResult(
        raw_path=target / Path(PurePosixPath(raw_path_value)),
        formatted_path=target / Path(PurePosixPath(formatted_path_value)),
        manifest_path=manifest_path,
        manifest=manifest,
        reused=True,
    )


def reuse_existing_conversion(
    config: IngestionConfig, *, conflict_policy: str | None = None
) -> ConversionResult | None:
    """Return only a matching conversion that currently passes authoritative Gate P."""

    policy = conflict_policy or config.conflict_policy
    if policy not in {"reject", "replace"}:
        raise IngestionError("conflict_policy must be 'reject' or 'replace'")
    try:
        paths = config.paths
    except (TypeError, ValueError) as exc:
        raise IngestionError(f"Invalid category or title: {exc}") from exc
    fingerprint = fingerprint_source(config.pdf)
    target = prepare_publication_target(config.markdown_root, paths.markdown_dir)
    return _existing_conversion(config, target, fingerprint, policy)


def ensure_package_target_compatible(config: IngestionConfig) -> None:
    """Reject a same-slug package bound to a different PDF before conversion work."""

    try:
        paths = config.paths
    except (TypeError, ValueError) as exc:
        raise IngestionError(f"Invalid category or title: {exc}") from exc
    source = fingerprint_source(config.pdf)
    package = prepare_publication_target(config.books_root, paths.book_dir)
    if package.exists():
        recorded = _recorded_package_pdf_hash(package)
        if recorded != source.sha256:
            raise IngestionError(
                "Existing package records a different or unknown source PDF SHA-256; "
                "use a new title/slug"
            )


def import_mineru_output(
    config: IngestionConfig,
    auto_dir: Path,
    mineru_version: str,
    *,
    mineru_binary: Path | None = None,
    command: list[str] | None = None,
    started_at: str | None = None,
    completed_at: str | None = None,
    source_fingerprint: SourceFingerprint | None = None,
    conflict_policy: str | None = None,
) -> ConversionResult:
    """Build a complete conversion generation and publish it as one directory."""

    policy = conflict_policy or config.conflict_policy
    if policy not in {"reject", "replace"}:
        raise IngestionError("conflict_policy must be 'reject' or 'replace'")
    try:
        paths = config.paths
    except (TypeError, ValueError) as exc:
        raise IngestionError(f"Invalid category or title: {exc}") from exc
    source_auto = Path(auto_dir).expanduser().resolve()
    if not source_auto.is_dir():
        raise IngestionError(f"MinerU auto directory does not exist: {source_auto}")
    raw_source = _find_raw_markdown(source_auto)
    before = source_fingerprint or fingerprint_source(config.pdf)
    current = fingerprint_source(config.pdf)
    if not _same_fingerprint(before, current):
        raise IngestionError(f"PDF changed before conversion import: {before.path}")

    output_dir = prepare_publication_target(config.markdown_root, paths.markdown_dir)
    reusable = _existing_conversion(config, output_dir, before, policy)
    if reusable is not None:
        return reusable

    staging_dir = Path(
        tempfile.mkdtemp(prefix=f".{paths.title}.conversion-", dir=output_dir.parent)
    )
    try:
        image_mappings = _copy_mineru_images(source_auto, staging_dir / "images")
        with raw_source.open("r", encoding="utf-8", newline="") as source_file:
            raw_text = source_file.read()
        imported_text = _rewrite_image_paths(raw_text, image_mappings)
        raw_path = staging_dir / f"{paths.title}.md"
        atomic_write_text(raw_path, imported_text)
        mineru_json = _copy_mineru_json(
            source_auto, staging_dir / "mineru", staging_dir
        )
        imported_at = _utc_now()

        formatted_text, normalization_changes = format_markdown(imported_text)
        formatted_path = staging_dir / f"{paths.title}-格式化.md"
        atomic_write_text(formatted_path, formatted_text)
        normalization_path = staging_dir / "normalization-log.json"
        atomic_write_text(
            normalization_path,
            json.dumps(normalization_changes, ensure_ascii=False, indent=2) + "\n",
        )
        formatted_at = _utc_now()

        chapters = split_chapters(formatted_text, staging_dir, paths.title)
        split_at = _utc_now()
        split_index_path = staging_dir / "拆分" / "split-index.json"

        image_resources: list[dict[str, object]] = []
        for source_path, output_path in sorted(image_mappings.items()):
            destination = staging_dir / Path(PurePosixPath(output_path))
            image_resources.append(
                {
                    **_file_record(destination, staging_dir),
                    "source_path": source_path,
                    "source_page": None,
                    "provenance": "mineru_auto",
                }
            )
        page_records = _content_list_page_records(mineru_json, staging_dir)
        source_count = _pdf_page_count(before.path)
        mineru_count = len(page_records)
        if source_count is None:
            reconciliation = "source_count_unavailable"
            warnings: list[dict[str, object]] = [
                {
                    "code": "source_page_count_unavailable",
                    "classification": "accepted",
                    "message": "A structural PDF page count was not directly observable; MinerU records remain authoritative staging evidence.",
                }
            ]
        elif source_count == mineru_count:
            reconciliation = "matched"
            warnings = []
        else:
            reconciliation = "mismatch"
            warnings = [
                {
                    "code": "page_count_mismatch",
                    "classification": "blocking",
                    "message": f"PDF page count {source_count} differs from MinerU page record count {mineru_count}.",
                }
            ]

        raw_record = _file_record(raw_path, staging_dir)
        formatted_record = _file_record(formatted_path, staging_dir)
        normalization_record = _file_record(normalization_path, staging_dir)
        split_index_record = _file_record(split_index_path, staging_dir)
        split_outputs = [split_index_record]
        split_outputs.extend(_file_record(path, staging_dir) for path in chapters)

        after = _require_unchanged_source(before, context="conversion import")
        manifest = read_json(_CONVERSION_TEMPLATE)
        manifest["book"] = {
            "title": paths.title,
            "category": paths.category,
            "slug": paths.slug,
            "language": config.language,
        }
        manifest["source"] = {
            "pdf": str(after.path),
            "sha256": after.sha256,
            "size": after.size,
            "mtime_ns": after.mtime_ns,
            "fingerprinted_at": before.captured_at,
        }
        manifest["engine"] = {
            "name": "MinerU",
            "version": mineru_version,
            "backend": config.backend,
            "language": config.language,
            "executable": str(mineru_binary.resolve()) if mineru_binary else "unknown",
            "command": list(command or []),
            "mode": "run" if command else "import-existing-output",
        }
        manifest["timestamps"] = {
            "started_at": started_at or before.captured_at,
            "mineru_completed_at": completed_at or imported_at,
            "conversion_completed_at": split_at,
        }
        manifest["pages"] = {
            "source_count": source_count,
            "mineru_count": mineru_count,
            "reconciliation": reconciliation,
            "records": page_records,
        }
        manifest["artifacts"] = {
            "raw_markdown": raw_record,
            "formatted_markdown": formatted_record,
            "normalization_log": normalization_record,
            "split_index": split_index_record,
        }
        manifest["stages"] = {
            "imported": _stage(imported_at, [raw_record, *mineru_json, *image_resources]),
            "formatted": _stage(
                formatted_at, [formatted_record, normalization_record]
            ),
            "split": _stage(split_at, split_outputs),
        }
        manifest["resources"] = {
            "images": image_resources,
            "mineru_json": mineru_json,
        }
        manifest["warnings"] = warnings
        manifest["validation"] = {
            "status": "pending",
            "blocking_count": 0,
            "issues": [],
            "validated_at": "",
        }
        manifest_path = staging_dir / "conversion-manifest.json"
        write_json(manifest_path, manifest)

        report = validate_conversion(
            staging_dir, require_recorded_gate=False, allow_staging_root=True
        )
        manifest["validation"] = {
            "status": "passed" if report.blocking_count == 0 else "failed",
            "blocking_count": report.blocking_count,
            "issues": [
                {
                    "code": issue.code,
                    "message": issue.message,
                    "path": str(issue.path),
                }
                for issue in report.issues
            ],
            "validated_at": _utc_now(),
        }
        write_json(manifest_path, manifest)
        if report.blocking_count:
            codes = ", ".join(issue.code for issue in report.issues)
            raise IngestionError(
                f"Conversion validation failed with {report.blocking_count} blocking issue(s): {codes}"
            )
        sealed_report = validate_conversion(staging_dir, allow_staging_root=True)
        if sealed_report.blocking_count:
            raise IngestionError(
                f"Persisted conversion gate failed with {sealed_report.blocking_count} blocking issue(s)"
            )
        atomic_publish_directory(staging_dir, output_dir)
        published_report = validate_conversion(output_dir)
        if published_report.blocking_count:
            raise IngestionError(
                f"Published conversion failed authoritative validation with "
                f"{published_report.blocking_count} blocking issue(s)"
            )
        published_manifest = read_json(output_dir / "conversion-manifest.json")
        return ConversionResult(
            raw_path=output_dir / raw_path.name,
            formatted_path=output_dir / formatted_path.name,
            manifest_path=output_dir / "conversion-manifest.json",
            manifest=published_manifest,
            reused=False,
        )
    except IngestionError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, TypeError) as exc:
        raise IngestionError(f"Unable to build conversion generation: {exc}") from exc
    finally:
        if staging_dir.exists():
            shutil.rmtree(staging_dir, ignore_errors=True)


def _protected_markdown_line_indexes(lines: list[str]) -> set[int]:
    """Identify Markdown lines whose literal contents must not drive normalization.

    The state machine covers leading YAML front matter, fenced/indented code,
    comments and declarations, and multiline raw HTML blocks.  It intentionally
    errs toward preserving source text.
    """

    protected: set[int] = set()
    start = 0
    if lines and lines[0].lstrip("\ufeff").strip() == "---":
        protected.add(0)
        for index in range(1, len(lines)):
            protected.add(index)
            if lines[index].strip() in {"---", "..."}:
                start = index + 1
                break
        else:
            return protected

    fence: tuple[str, int] | None = None
    literal_close: str | None = None
    html_tag: str | None = None
    for index in range(start, len(lines)):
        line = lines[index]
        plain = line.rstrip("\r\n")
        if fence is not None:
            protected.add(index)
            marker, length = fence
            if re.match(
                rf"^[ \t]{{0,3}}{re.escape(marker)}{{{length},}}[ \t]*$", plain
            ):
                fence = None
            continue
        if literal_close is not None:
            protected.add(index)
            if literal_close in line:
                literal_close = None
            continue
        if html_tag is not None:
            protected.add(index)
            if re.search(rf"</{re.escape(html_tag)}\s*>", line, re.IGNORECASE):
                html_tag = None
            continue

        if _PAGE_BOUNDARY_RE.fullmatch(plain):
            continue
        close = _multiline_literal_close(line)
        if close is not None:
            protected.add(index)
            if close not in line[line.find(line.lstrip()) + 1 :]:
                literal_close = close
            continue
        fence_match = _FENCE_OPEN_RE.match(line)
        if fence_match:
            protected.add(index)
            marker = fence_match.group("fence")[0]
            fence = (marker, len(fence_match.group("fence")))
            continue
        html_match = _HTML_BLOCK_OPEN_RE.match(line)
        if html_match:
            protected.add(index)
            tag = html_match.group("tag").casefold()
            if tag not in _HTML_VOID_TAGS and not re.search(
                rf"</{re.escape(tag)}\s*>", line, re.IGNORECASE
            ):
                html_tag = tag
            continue
        if line.startswith(("    ", "\t")):
            protected.add(index)
    return protected


def _page_edge_line_indexes(
    lines: list[str], protected: set[int] | None = None
) -> set[int]:
    """Return first/last body lines of pages marked by explicit page boundaries."""

    protected_indexes = protected or set()
    boundaries = [
        index
        for index, line in enumerate(lines)
        if index not in protected_indexes and _PAGE_BOUNDARY_RE.fullmatch(line)
    ]
    edges: set[int] = set()
    for position, boundary in enumerate(boundaries):
        next_boundary = boundaries[position + 1] if position + 1 < len(boundaries) else len(lines)
        body_lines = [
            index
            for index in range(boundary + 1, next_boundary)
            if index not in protected_indexes and lines[index].strip()
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
    protected = _protected_markdown_line_indexes(lines)
    page_edges = _page_edge_line_indexes(plain_lines, protected)
    repeated_labels = _repeated_header_footer_lines(plain_lines, page_edges)
    retained: list[str] = []
    changes: list[dict[str, str]] = []
    for index, (line, plain) in enumerate(zip(lines, plain_lines)):
        stripped = plain.strip()
        if (
            index not in protected
            and index in page_edges
            and stripped
            and _PAGE_FOOTER_RE.fullmatch(stripped)
        ):
            changes.append({"type": "removed_page_footer", "text": plain})
            continue
        if index not in protected and index in page_edges and stripped in repeated_labels:
            changes.append({"type": "removed_repeated_header_footer", "text": plain})
            continue
        retained.append(line)

    return "".join(retained), changes


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
    protected = _protected_markdown_line_indexes(lines)
    chapter_starts: list[tuple[int, str]] = []
    in_contents = False
    contents_heading_level: int | None = None
    for index, line in enumerate(lines):
        if index in protected:
            continue
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
    split_units: list[dict[str, object]] = []
    for number, (start, heading) in enumerate(chapter_starts, start=1):
        source_start = 0 if number == 1 else start
        end = chapter_starts[number][0] if number < len(chapter_starts) else len(lines)
        chapter_path = chapters_dir / _chapter_filename(number, heading)
        source_text = "".join(lines[source_start:end])
        chapter_text = _rewrite_chapter_image_paths(
            source_text, chapter_path, Path(output_dir)
        )
        atomic_write_text(chapter_path, chapter_text)
        chapter_paths.append(chapter_path)
        split_units.append(
            {
                "kind": "chapter",
                "path": chapter_path.relative_to(output_dir).as_posix(),
                "start": sum(len(value) for value in lines[:source_start]),
                "end": sum(len(value) for value in lines[:end]),
                "source_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
                "sha256": sha256_file(chapter_path),
                "size": chapter_path.stat().st_size,
            }
        )

    chapter_links = "\n".join(
        f"- [{path.stem}](章节/{path.name})" for path in chapter_paths
    ) or "- 未识别到可高置信拆分的章节。"
    atomic_write_text(split_root / "README.md", f"# {title} 拆分目录\n\n{chapter_links}\n")
    chapter_index = "\n".join(
        f"- [{path.stem}]({path.name})" for path in chapter_paths
    ) or "- 未识别到可高置信拆分的章节。"
    atomic_write_text(chapters_dir / "README.md", f"# {title} 章节\n\n{chapter_index}\n")
    if not split_units:
        split_units.append(
            {
                "kind": "formatted_fallback",
                "path": f"{title}-格式化.md",
                "start": 0,
                "end": len(formatted_text),
                "source_sha256": hashlib.sha256(
                    formatted_text.encode("utf-8")
                ).hexdigest(),
                "sha256": hashlib.sha256(formatted_text.encode("utf-8")).hexdigest(),
                "size": len(formatted_text.encode("utf-8")),
            }
        )
    split_index = {
        "schema_version": 1,
        "source_path": f"{title}-格式化.md",
        "source_sha256": hashlib.sha256(formatted_text.encode("utf-8")).hexdigest(),
        "source_char_count": len(formatted_text),
        "mode": "chapters" if chapter_paths else "formatted_fallback",
        "units": split_units,
        "exclusions": [],
    }
    write_json(split_root / "split-index.json", split_index)
    return chapter_paths


def collect_markdown_links(path: Path) -> list[str]:
    """Return direct and reference-style Markdown image targets in source order."""

    with Path(path).open("r", encoding="utf-8", newline="") as source:
        text = source.read()
    visible = _markdown_without_protected_blocks(text)
    targets = [match.group("target") for match in _IMAGE_TARGET_RE.finditer(visible)]
    reference_targets, _ = _reference_image_analysis(visible)
    targets.extend(reference_targets)
    return targets


def _markdown_without_protected_blocks(markdown: str) -> str:
    """Mask protected block contents while retaining line boundaries."""

    lines = markdown.splitlines(keepends=True)
    protected = _protected_markdown_line_indexes(lines)
    return "".join(
        ("\n" if line.endswith("\n") else "") if index in protected else line
        for index, line in enumerate(lines)
    )


def _substitute_outside_protected(
    markdown: str,
    pattern: re.Pattern[str],
    replacement,
) -> str:
    """Apply one Markdown rewrite only on top-level, nonliteral lines."""

    lines = markdown.splitlines(keepends=True)
    protected = _protected_markdown_line_indexes(lines)
    return "".join(
        line if index in protected else pattern.sub(replacement, line)
        for index, line in enumerate(lines)
    )


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


def _add_validation_issue(
    issues: list[ValidationIssue], code: str, message: str, path: Path
) -> None:
    issues.append(ValidationIssue(code=code, message=message, path=Path(path)))


def _manifest_relative_path(
    root: Path,
    value: object,
    *,
    issues: list[ValidationIssue],
    code: str,
    label: str,
) -> Path | None:
    if not isinstance(value, str) or not value:
        _add_validation_issue(issues, code, f"{label} path is missing", root)
        return None
    posix = PurePosixPath(value.replace("\\", "/"))
    windows = PureWindowsPath(value)
    if posix.is_absolute() or windows.is_absolute() or windows.drive:
        _add_validation_issue(
            issues, code, f"{label} path must be conversion-relative: {value}", root
        )
        return None
    if any(part in {"", ".", ".."} for part in posix.parts):
        _add_validation_issue(
            issues, code, f"{label} path escapes or is ambiguous: {value}", root
        )
        return None
    candidate = root / Path(posix)
    resolved = candidate.resolve(strict=False)
    if not _contained(resolved, root.resolve()):
        _add_validation_issue(
            issues, code, f"{label} path resolves outside conversion root: {value}", candidate
        )
        return None
    current = root
    for part in posix.parts:
        current = current / part
        if current.is_symlink():
            _add_validation_issue(
                issues, code, f"{label} path traverses a symlink: {value}", current
            )
            return None
    return candidate


def _validate_file_record(
    record: object,
    root: Path,
    issues: list[ValidationIssue],
    *,
    label: str,
    missing_code: str = "missing_declared_file",
    escape_code: str = "resource_path_escape",
) -> tuple[Path | None, str | None]:
    if not isinstance(record, dict):
        _add_validation_issue(
            issues, "manifest_schema_invalid", f"{label} must be an object", root
        )
        return None, None
    value = record.get("path")
    path = _manifest_relative_path(
        root,
        value,
        issues=issues,
        code=escape_code,
        label=label,
    )
    path_value = value if isinstance(value, str) else None
    if path is None:
        return None, path_value
    if not path.is_file():
        _add_validation_issue(
            issues, missing_code, f"Declared {label} does not exist", path
        )
        return path, path_value
    expected_hash = record.get("sha256")
    if not isinstance(expected_hash, str) or not re.fullmatch(
        r"[0-9a-f]{64}", expected_hash
    ):
        _add_validation_issue(
            issues,
            "manifest_schema_invalid",
            f"Declared {label} has no valid SHA-256",
            path,
        )
    else:
        try:
            actual_hash = sha256_file(path)
        except OSError as exc:
            _add_validation_issue(
                issues, "declared_file_unreadable", f"Unable to hash {label}: {exc}", path
            )
        else:
            if actual_hash != expected_hash:
                _add_validation_issue(
                    issues,
                    "artifact_hash_mismatch",
                    f"Declared {label} SHA-256 no longer matches",
                    path,
                )
    size = record.get("size")
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        _add_validation_issue(
            issues,
            "manifest_schema_invalid",
            f"Declared {label} has no valid byte size",
            path,
        )
    elif path.stat().st_size != size:
        _add_validation_issue(
            issues,
            "artifact_size_mismatch",
            f"Declared {label} byte size no longer matches",
            path,
        )
    return path, path_value


def _validate_split_coverage(
    split_path: Path,
    formatted_path: Path,
    root: Path,
    issues: list[ValidationIssue],
) -> set[str]:
    declared_paths: set[str] = set()
    try:
        split = read_json(split_path)
        formatted_text = formatted_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        _add_validation_issue(
            issues, "split_index_invalid", f"Split index is unreadable: {exc}", split_path
        )
        return declared_paths
    if split.get("schema_version") != 1:
        _add_validation_issue(
            issues, "split_index_invalid", "Split index schema_version must be 1", split_path
        )
    expected_source_path = formatted_path.relative_to(root).as_posix()
    if split.get("source_path") != expected_source_path:
        _add_validation_issue(
            issues,
            "split_source_mismatch",
            "Split index source_path does not identify formatted Markdown",
            split_path,
        )
    source_hash = hashlib.sha256(formatted_text.encode("utf-8")).hexdigest()
    if split.get("source_sha256") != source_hash:
        _add_validation_issue(
            issues,
            "split_source_mismatch",
            "Split index source hash does not match formatted Markdown",
            split_path,
        )
    if split.get("source_char_count") != len(formatted_text):
        _add_validation_issue(
            issues,
            "split_source_mismatch",
            "Split index character count does not match formatted Markdown",
            split_path,
        )

    units = split.get("units")
    exclusions = split.get("exclusions")
    if not isinstance(units, list) or not units:
        _add_validation_issue(
            issues, "split_coverage_gap", "Split index requires ordered source units", split_path
        )
        return declared_paths
    if not isinstance(exclusions, list):
        _add_validation_issue(
            issues, "split_index_invalid", "Split exclusions must be a list", split_path
        )
        exclusions = []
    exclusion_segments: list[tuple[object, object, str, object]] = []
    unit_segments: list[tuple[object, object, str, object]] = []
    for exclusion in exclusions:
        if not isinstance(exclusion, dict):
            _add_validation_issue(
                issues, "split_exclusion_unclassified", "Split exclusion must be an object", split_path
            )
            continue
        classification = exclusion.get("classification")
        reason = exclusion.get("reason")
        if classification not in {"accepted", "not_applicable"} or not isinstance(
            reason, str
        ) or not reason:
            _add_validation_issue(
                issues,
                "split_exclusion_unclassified",
                "Every split exclusion requires an accepted classification and reason",
                split_path,
            )
        exclusion_segments.append(
            (exclusion.get("start", -1), exclusion.get("end", -1), "exclusion", exclusion)
        )

    for unit in units:
        if not isinstance(unit, dict):
            _add_validation_issue(
                issues, "split_index_invalid", "Split unit must be an object", split_path
            )
            continue
        start = unit.get("start")
        end = unit.get("end")
        unit_segments.append((start, end, "unit", unit))
        unit_path, unit_value = _validate_file_record(
            unit,
            root,
            issues,
            label="split unit",
            missing_code="missing_split_output",
        )
        if unit_value:
            declared_paths.add(unit_value)
        if (
            unit_path is not None
            and isinstance(start, int)
            and not isinstance(start, bool)
            and isinstance(end, int)
            and not isinstance(end, bool)
            and 0 <= start <= end <= len(formatted_text)
        ):
            slice_hash = hashlib.sha256(
                formatted_text[start:end].encode("utf-8")
            ).hexdigest()
            if unit.get("source_sha256") != slice_hash:
                _add_validation_issue(
                    issues,
                    "split_source_mismatch",
                    "Split unit source span hash does not match formatted Markdown",
                    unit_path,
                )
            source_slice = formatted_text[start:end]
            expected_output = (
                _rewrite_chapter_image_paths(source_slice, unit_path, root)
                if unit.get("kind") == "chapter"
                else source_slice
            )
            try:
                current_output = unit_path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                _add_validation_issue(
                    issues,
                    "split_output_mismatch",
                    f"Split output cannot be compared to its source span: {exc}",
                    unit_path,
                )
            else:
                if current_output != expected_output:
                    _add_validation_issue(
                        issues,
                        "split_output_mismatch",
                        "Split output is not the deterministic rendering of its formatted source span",
                        unit_path,
                    )

    normalized_units: list[tuple[int, int, str, object]] = []
    normalized_exclusions: list[tuple[int, int, str, object]] = []
    malformed_segment = False
    for recorded, normalized in (
        (unit_segments, normalized_units),
        (exclusion_segments, normalized_exclusions),
    ):
        for start, end, kind, payload in recorded:
            if (
                not isinstance(start, int)
                or isinstance(start, bool)
                or not isinstance(end, int)
                or isinstance(end, bool)
                or start < 0
                or end < start
                or end > len(formatted_text)
            ):
                _add_validation_issue(
                    issues,
                    "split_coverage_gap",
                    "Split spans require valid integer bounds within formatted Markdown",
                    split_path,
                )
                malformed_segment = True
                continue
            normalized.append((start, end, kind, payload))

    cursor = 0
    unit_index = 0
    exclusion_index = 0
    while (
        unit_index < len(normalized_units)
        or exclusion_index < len(normalized_exclusions)
    ):
        next_unit = (
            normalized_units[unit_index]
            if unit_index < len(normalized_units)
            else None
        )
        next_exclusion = (
            normalized_exclusions[exclusion_index]
            if exclusion_index < len(normalized_exclusions)
            else None
        )
        unit_ready = next_unit is not None and next_unit[0] == cursor
        exclusion_ready = (
            next_exclusion is not None and next_exclusion[0] == cursor
        )
        if unit_ready == exclusion_ready:
            _add_validation_issue(
                issues,
                "split_coverage_gap",
                "Recorded split spans are reordered, overlapping, or leave a gap",
                split_path,
            )
            malformed_segment = True
            break
        if unit_ready:
            assert next_unit is not None
            cursor = next_unit[1]
            unit_index += 1
        else:
            assert next_exclusion is not None
            cursor = next_exclusion[1]
            exclusion_index += 1
    if malformed_segment or cursor != len(formatted_text):
        _add_validation_issue(
            issues,
            "split_coverage_gap",
            "Split spans do not reach the end of formatted Markdown",
            split_path,
        )
    mode = split.get("mode")
    if mode not in {"chapters", "formatted_fallback"}:
        _add_validation_issue(
            issues, "split_index_invalid", "Split mode is invalid", split_path
        )
    if mode == "chapters":
        chapter_values = [
            unit.get("path")
            for unit in units
            if isinstance(unit, dict) and isinstance(unit.get("path"), str)
        ]
        if (
            len(chapter_values) != len(units)
            or len(set(chapter_values)) != len(chapter_values)
            or any(
                not isinstance(unit, dict)
                or unit.get("kind") != "chapter"
                or not isinstance(unit.get("path"), str)
                or not unit["path"].startswith("拆分/章节/")
                or Path(PurePosixPath(unit["path"])).name == "README.md"
                for unit in units
            )
        ):
            _add_validation_issue(
                issues,
                "split_index_invalid",
                "Chapter mode requires distinct ordered chapter units below 拆分/章节/",
                split_path,
            )
    if mode == "formatted_fallback" and (
        len(units) != 1
        or not isinstance(units[0], dict)
        or units[0].get("path") != expected_source_path
    ):
        _add_validation_issue(
            issues,
            "split_source_mismatch",
            "Formatted fallback must identify the formatted artifact as its sole unit",
            split_path,
        )
    return declared_paths


def validate_conversion(
    output_dir: Path,
    *,
    require_recorded_gate: bool = True,
    allow_staging_root: bool = False,
) -> ValidationReport:
    """Authoritatively validate a complete, self-contained conversion generation."""

    root = Path(output_dir)
    issues: list[ValidationIssue] = []
    if root.is_symlink():
        _add_validation_issue(
            issues,
            "output_path_escape",
            "Conversion root may not be a symlink",
            root,
        )
    if not root.is_dir():
        _add_validation_issue(
            issues,
            "missing_output_directory",
            f"Conversion output directory does not exist: {root}",
            root,
        )
        return ValidationReport("failed", tuple(issues), len(issues))
    root = root.resolve()
    manifest_path = root / "conversion-manifest.json"
    if not manifest_path.is_file():
        _add_validation_issue(
            issues, "manifest_missing", "Conversion manifest is missing", manifest_path
        )
        return ValidationReport("failed", tuple(issues), len(issues))
    try:
        manifest = read_json(manifest_path)
    except json.JSONDecodeError as exc:
        _add_validation_issue(
            issues,
            "manifest_invalid_json",
            f"Conversion manifest is malformed JSON: {exc}",
            manifest_path,
        )
        return ValidationReport("failed", tuple(issues), len(issues))
    except (OSError, UnicodeError, ValueError) as exc:
        _add_validation_issue(
            issues,
            "manifest_schema_invalid",
            f"Conversion manifest is invalid: {exc}",
            manifest_path,
        )
        return ValidationReport("failed", tuple(issues), len(issues))

    if manifest.get("schema_version") != 2:
        _add_validation_issue(
            issues,
            "manifest_schema_invalid",
            "Conversion manifest schema_version must be 2",
            manifest_path,
        )
    required_objects: dict[str, dict[str, object]] = {}
    for name in (
        "book",
        "source",
        "engine",
        "timestamps",
        "pages",
        "artifacts",
        "stages",
        "resources",
        "validation",
    ):
        value = manifest.get(name)
        if not isinstance(value, dict):
            _add_validation_issue(
                issues,
                "manifest_schema_invalid",
                f"Conversion manifest requires object: {name}",
                manifest_path,
            )
            value = {}
        required_objects[name] = value

    book = required_objects["book"]
    try:
        title = safe_segment(book.get("title"))
        category = safe_segment(book.get("category"))
        slug = slugify_title(title)
    except (TypeError, ValueError) as exc:
        _add_validation_issue(
            issues,
            "manifest_identity_invalid",
            f"Conversion book identity is invalid: {exc}",
            manifest_path,
        )
        title = category = slug = ""
    if title and not allow_staging_root and (
        root.name != title or root.parent.name != category
    ):
        _add_validation_issue(
            issues,
            "manifest_root_mismatch",
            "Conversion manifest title/category do not match the publication root",
            manifest_path,
        )
    if book.get("slug") != slug or not isinstance(book.get("language"), str):
        _add_validation_issue(
            issues,
            "manifest_identity_invalid",
            "Conversion book slug/language identity is invalid",
            manifest_path,
        )

    source = required_objects["source"]
    pdf_value = source.get("pdf")
    pdf = Path(pdf_value) if isinstance(pdf_value, str) else Path()
    current_pdf_page_count: int | None = None
    if not isinstance(pdf_value, str) or not pdf.is_absolute() or not pdf.is_file():
        _add_validation_issue(
            issues,
            "source_pdf_missing",
            "Conversion source.pdf must be an existing absolute file",
            pdf if pdf_value else manifest_path,
        )
    else:
        try:
            current_pdf = pdf.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            _add_validation_issue(
                issues, "source_pdf_unreadable", f"Unable to read source PDF: {exc}", pdf
            )
        else:
            current_pdf_page_count = _pdf_page_count(current_pdf)
            try:
                actual_hash = sha256_file(current_pdf)
                actual_size = current_pdf.stat().st_size
            except OSError as exc:
                _add_validation_issue(
                    issues,
                    "source_pdf_unreadable",
                    f"Unable to read source PDF: {exc}",
                    current_pdf,
                )
            else:
                if source.get("sha256") != actual_hash:
                    _add_validation_issue(
                        issues,
                        "source_pdf_hash_mismatch",
                        "Source PDF SHA-256 no longer matches the manifest",
                        current_pdf,
                    )
                if source.get("size") != actual_size:
                    _add_validation_issue(
                        issues,
                        "source_pdf_size_mismatch",
                        "Source PDF size no longer matches the manifest",
                        current_pdf,
                    )
    if not isinstance(source.get("mtime_ns"), int) or not isinstance(
        source.get("fingerprinted_at"), str
    ):
        _add_validation_issue(
            issues,
            "manifest_schema_invalid",
            "Source fingerprint metadata is incomplete",
            manifest_path,
        )

    engine = required_objects["engine"]
    engine_mode = engine.get("mode")
    engine_command = engine.get("command")
    required_engine_strings = (
        engine.get("version"),
        engine.get("backend"),
        engine.get("language"),
        engine.get("executable"),
    )
    if (
        engine.get("name") != "MinerU"
        or any(not isinstance(value, str) or not value.strip() for value in required_engine_strings)
        or not isinstance(engine_command, list)
        or any(not isinstance(value, str) for value in engine_command or [])
        or engine_mode not in {"run", "import-existing-output"}
    ):
        _add_validation_issue(
            issues,
            "engine_provenance_invalid",
            "MinerU backend, executable, exact command, language, version, and mode are required",
            manifest_path,
        )
    elif engine_mode == "run":
        executable = engine["executable"]
        backend = engine["backend"]
        language = engine["language"]
        command_matches = (
            len(engine_command) == 9
            and Path(executable).is_absolute()
            and engine_command[0] == executable
            and engine_command[1] == "-p"
            and engine_command[2] == pdf_value
            and engine_command[3] == "-o"
            and bool(engine_command[4])
            and Path(engine_command[4]).is_absolute()
            and engine_command[5] == "-b"
            and engine_command[6] == backend
            and engine_command[7] == "-l"
            and engine_command[8] == language
        )
        if not command_matches:
            _add_validation_issue(
                issues,
                "engine_command_mismatch",
                "MinerU run command must exactly bind executable, PDF, output, backend, and language",
                manifest_path,
            )
    elif engine_command != []:
        _add_validation_issue(
            issues,
            "engine_command_mismatch",
            "Imported MinerU output must record an empty execution command",
            manifest_path,
        )
    timestamps = required_objects["timestamps"]
    for key in ("started_at", "mineru_completed_at", "conversion_completed_at"):
        if not isinstance(timestamps.get(key), str) or not timestamps.get(key):
            _add_validation_issue(
                issues,
                "timestamp_missing",
                f"Conversion timestamp is missing: {key}",
                manifest_path,
            )

    artifacts = required_objects["artifacts"]
    artifact_paths: dict[str, Path] = {}
    artifact_values: dict[str, str] = {}
    artifact_missing_codes = {
        "raw_markdown": "missing_raw_markdown",
        "formatted_markdown": "missing_formatted_markdown",
        "normalization_log": "missing_normalization_log",
        "split_index": "missing_split_index",
    }
    for name, missing_code in artifact_missing_codes.items():
        path, value = _validate_file_record(
            artifacts.get(name),
            root,
            issues,
            label=name.replace("_", " "),
            missing_code=missing_code,
        )
        if path is not None:
            artifact_paths[name] = path
        if value is not None:
            artifact_values[name] = value
    if title:
        canonical_artifacts = {
            "raw_markdown": f"{title}.md",
            "formatted_markdown": f"{title}-格式化.md",
            "normalization_log": "normalization-log.json",
            "split_index": "拆分/split-index.json",
        }
        for artifact_name, expected_path in canonical_artifacts.items():
            if artifact_values.get(artifact_name) != expected_path:
                _add_validation_issue(
                    issues,
                    "artifact_identity_invalid",
                    f"{artifact_name} must identify canonical path {expected_path}",
                    manifest_path,
                )
        declared_artifact_paths = [
            artifact_values.get(name) for name in canonical_artifacts
        ]
        present_artifact_paths = [
            value for value in declared_artifact_paths if isinstance(value, str)
        ]
        if len(present_artifact_paths) != len(set(present_artifact_paths)):
            _add_validation_issue(
                issues,
                "artifact_identity_invalid",
                "Raw, formatted, normalization, and split artifacts must be distinct",
                manifest_path,
            )
    normalization_path = artifact_paths.get("normalization_log")
    normalization_payload: object = None
    if normalization_path is not None:
        try:
            normalization_payload = _load_json_value(normalization_path)
        except IngestionError as exc:
            _add_validation_issue(
                issues,
                "normalization_log_invalid",
                str(exc),
                normalization_path,
            )
        else:
            if not isinstance(normalization_payload, list):
                _add_validation_issue(
                    issues,
                    "normalization_log_invalid",
                    "Normalization log must be a JSON list",
                    normalization_path,
                )
    raw_artifact = artifact_paths.get("raw_markdown")
    formatted_artifact = artifact_paths.get("formatted_markdown")
    if raw_artifact is not None and formatted_artifact is not None:
        try:
            with raw_artifact.open("r", encoding="utf-8", newline="") as source_file:
                raw_artifact_text = source_file.read()
            with formatted_artifact.open(
                "r", encoding="utf-8", newline=""
            ) as formatted_file:
                formatted_artifact_text = formatted_file.read()
        except (OSError, UnicodeError) as exc:
            _add_validation_issue(
                issues,
                "formatted_derivation_mismatch",
                f"Raw/formatted derivation cannot be recomputed: {exc}",
                formatted_artifact,
            )
        else:
            expected_formatted, expected_normalization = format_markdown(
                raw_artifact_text
            )
            if formatted_artifact_text != expected_formatted:
                _add_validation_issue(
                    issues,
                    "formatted_derivation_mismatch",
                    "Formatted Markdown is not the deterministic normalization of raw Markdown",
                    formatted_artifact,
                )
            if isinstance(normalization_payload, list) and (
                normalization_payload != expected_normalization
            ):
                _add_validation_issue(
                    issues,
                    "normalization_audit_mismatch",
                    "Normalization audit does not match the deterministic raw-to-formatted changes",
                    normalization_path or manifest_path,
                )

    resources = required_objects["resources"]
    resource_paths: set[str] = set()
    content_records: list[dict[str, object]] = []
    for kind in ("images", "mineru_json"):
        values = resources.get(kind)
        if not isinstance(values, list):
            _add_validation_issue(
                issues,
                "manifest_schema_invalid",
                f"resources.{kind} must be a list",
                manifest_path,
            )
            continue
        for index, record in enumerate(values):
            path, value = _validate_file_record(
                record,
                root,
                issues,
                label=f"{kind} resource {index}",
                missing_code="missing_resource",
            )
            if value:
                expected_prefix = "images/" if kind == "images" else "mineru/"
                if not value.startswith(expected_prefix):
                    _add_validation_issue(
                        issues,
                        "resource_path_escape",
                        f"{kind} resource must be stored below {expected_prefix}",
                        path or manifest_path,
                    )
                if value in resource_paths:
                    _add_validation_issue(
                        issues,
                        "resource_duplicate",
                        f"Resource path is declared more than once: {value}",
                        path or manifest_path,
                    )
                resource_paths.add(value)
            if isinstance(record, dict):
                if not isinstance(record.get("source_path"), str):
                    _add_validation_issue(
                        issues,
                        "resource_provenance_missing",
                        f"{kind} resource lacks source_path provenance",
                        path or manifest_path,
                    )
                if kind == "images" and "source_page" not in record:
                    _add_validation_issue(
                        issues,
                        "resource_provenance_missing",
                        "Image resource lacks source_page provenance",
                        path or manifest_path,
                    )
                if kind == "mineru_json" and record.get("kind") == "content_list":
                    if path is not None and path.is_file():
                        content_records.append(record)

    for directory_name, prefix in (("images", "images/"), ("mineru", "mineru/")):
        directory = root / directory_name
        if not directory.exists():
            continue
        actual_files = {
            path.relative_to(root).as_posix()
            for path in directory.rglob("*")
            if path.is_file() or path.is_symlink()
        }
        undeclared = sorted(
            actual_files
            - {value for value in resource_paths if value.startswith(prefix)}
        )
        for value in undeclared:
            _add_validation_issue(
                issues,
                "undeclared_resource",
                f"Conversion resource is not declared in the manifest: {value}",
                root / Path(PurePosixPath(value)),
            )

    if not content_records:
        _add_validation_issue(
            issues,
            "content_list_missing",
            "At least one MinerU content-list JSON resource is required",
            manifest_path,
        )
        actual_page_records: list[dict[str, int]] = []
    else:
        try:
            actual_page_records = _content_list_page_records(content_records, root)
        except IngestionError as exc:
            _add_validation_issue(
                issues, "content_list_invalid", str(exc), manifest_path
            )
            actual_page_records = []
    pages = required_objects["pages"]
    declared_page_records = pages.get("records")
    if not actual_page_records or not isinstance(declared_page_records, list) or not declared_page_records:
        _add_validation_issue(
            issues,
            "page_records_empty",
            "MinerU content-list must yield nonempty page records",
            manifest_path,
        )
    elif declared_page_records != actual_page_records:
        _add_validation_issue(
            issues,
            "page_records_mismatch",
            "Manifest page records do not match current content-list JSON",
            manifest_path,
        )
    mineru_count = len(actual_page_records)
    if pages.get("mineru_count") != mineru_count:
        _add_validation_issue(
            issues,
            "page_count_mismatch",
            "Manifest mineru_count does not match current page records",
            manifest_path,
        )
    source_count = pages.get("source_count")
    if current_pdf_page_count is None:
        if source_count is not None:
            _add_validation_issue(
                issues,
                "page_count_mismatch",
                "Current PDF page count is unavailable but pages.source_count does not explicitly record unavailable",
                manifest_path,
            )
    elif (
        not isinstance(source_count, int)
        or isinstance(source_count, bool)
        or source_count != current_pdf_page_count
    ):
        _add_validation_issue(
            issues,
            "page_count_mismatch",
            "Manifest source_count does not match the current source PDF page count",
            manifest_path,
        )
    expected_reconciliation = (
        "source_count_unavailable"
        if source_count is None
        else "matched"
        if isinstance(source_count, int)
        and not isinstance(source_count, bool)
        and source_count == mineru_count
        else "mismatch"
    )
    if pages.get("reconciliation") != expected_reconciliation:
        _add_validation_issue(
            issues,
            "page_reconciliation_invalid",
            "Page count reconciliation is inconsistent",
            manifest_path,
        )
    if expected_reconciliation == "mismatch":
        _add_validation_issue(
            issues,
            "page_count_mismatch",
            "PDF and MinerU page counts differ",
            manifest_path,
        )

    stages = required_objects["stages"]
    stage_output_paths: dict[str, set[str]] = {}
    for stage_name in ("imported", "formatted", "split"):
        stage = stages.get(stage_name)
        if not isinstance(stage, dict):
            _add_validation_issue(
                issues,
                "stage_incomplete",
                f"Stage {stage_name} is missing",
                manifest_path,
            )
            continue
        if stage.get("status") != "complete" or not isinstance(
            stage.get("completed_at"), str
        ) or not stage.get("completed_at"):
            _add_validation_issue(
                issues,
                "stage_incomplete",
                f"Stage {stage_name} is not complete",
                manifest_path,
            )
        outputs = stage.get("outputs")
        output_values: set[str] = set()
        if not isinstance(outputs, list):
            _add_validation_issue(
                issues,
                "stage_output_missing",
                f"Stage {stage_name} outputs must be a list",
                manifest_path,
            )
        else:
            for index, record in enumerate(outputs):
                _, value = _validate_file_record(
                    record,
                    root,
                    issues,
                    label=f"{stage_name} output {index}",
                    missing_code="stage_output_missing",
                )
                if value:
                    output_values.add(value)
        stage_output_paths[stage_name] = output_values

    required_stage_paths = {
        "imported": {
            artifact_values.get("raw_markdown"),
            *resource_paths,
        },
        "formatted": {
            artifact_values.get("formatted_markdown"),
            artifact_values.get("normalization_log"),
        },
        "split": {artifact_values.get("split_index")},
    }
    split_units: set[str] = set()
    if "split_index" in artifact_paths and "formatted_markdown" in artifact_paths:
        split_units = _validate_split_coverage(
            artifact_paths["split_index"],
            artifact_paths["formatted_markdown"],
            root,
            issues,
        )
        try:
            split_payload = read_json(artifact_paths["split_index"])
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            split_payload = {}
        if split_payload.get("mode") == "chapters":
            required_stage_paths["split"].update(split_units)
    for stage_name, expected in required_stage_paths.items():
        expected_paths = {value for value in expected if value}
        actual_paths = stage_output_paths.get(stage_name, set())
        missing = expected_paths - actual_paths
        if missing:
            _add_validation_issue(
                issues,
                "stage_output_missing",
                f"Stage {stage_name} does not declare outputs: {sorted(missing)}",
                manifest_path,
            )
        unexpected = actual_paths - expected_paths
        if unexpected:
            _add_validation_issue(
                issues,
                "stage_output_unexpected",
                f"Stage {stage_name} declares outputs owned by another stage: {sorted(unexpected)}",
                manifest_path,
            )

    chapter_output_root = root / "拆分" / "章节"
    actual_split_markdown = {
        path.relative_to(root).as_posix()
        for path in chapter_output_root.rglob("*.md")
        if path.name != "README.md" and path.is_file()
    } if chapter_output_root.is_dir() else set()
    for value in sorted(actual_split_markdown - split_units):
        _add_validation_issue(
            issues,
            "undeclared_split_output",
            f"Chapter Markdown is not declared by split-index.json: {value}",
            root / Path(PurePosixPath(value)),
        )

    warnings = manifest.get("warnings")
    if not isinstance(warnings, list):
        _add_validation_issue(
            issues,
            "manifest_schema_invalid",
            "Conversion warnings must be a list",
            manifest_path,
        )
    else:
        for warning in warnings:
            if (
                not isinstance(warning, dict)
                or not isinstance(warning.get("code"), str)
                or not isinstance(warning.get("message"), str)
                or warning.get("classification")
                not in {"accepted", "blocking", "not_applicable"}
            ):
                _add_validation_issue(
                    issues,
                    "warning_unclassified",
                    "Every warning requires code, message, and classification",
                    manifest_path,
                )
            elif warning.get("classification") == "blocking":
                _add_validation_issue(
                    issues,
                    "blocking_warning",
                    f"Blocking conversion warning: {warning.get('code')}",
                    manifest_path,
                )
    warning_items = warnings if isinstance(warnings, list) else []
    if source_count is None and not any(
        isinstance(warning, dict)
        and warning.get("code") == "source_page_count_unavailable"
        and warning.get("classification") == "accepted"
        for warning in warning_items
    ):
        _add_validation_issue(
            issues,
            "warning_unclassified",
            "Unavailable PDF page count requires an accepted classified warning",
            manifest_path,
        )

    declared_images = {
        record.get("path")
        for record in resources.get("images", [])
        if isinstance(record, dict) and isinstance(record.get("path"), str)
    }
    for markdown in sorted(root.rglob("*.md")):
        try:
            markdown_text = markdown.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            _add_validation_issue(
                issues,
                "markdown_unreadable",
                f"Markdown cannot be inspected for image references: {exc}",
                markdown,
            )
            continue
        _, unresolved_labels = _reference_image_analysis(markdown_text)
        for label in unresolved_labels:
            _add_validation_issue(
                issues,
                "unresolved_image_reference",
                f"Markdown image reference has no definition: {label}",
                markdown,
            )
        for target in collect_markdown_links(markdown):
            local = _local_image_target(target)
            if local is None:
                continue
            normalized = local.replace("\\", "/")
            posix = PurePosixPath(normalized)
            windows = PureWindowsPath(normalized)
            if posix.is_absolute() or windows.is_absolute() or windows.drive:
                _add_validation_issue(
                    issues,
                    "image_path_escape",
                    f"Absolute Markdown image path is not allowed: {target}",
                    markdown,
                )
                continue
            image = markdown.parent / Path(posix)
            resolved = image.resolve(strict=False)
            if not _contained(resolved, root):
                _add_validation_issue(
                    issues,
                    "image_path_escape",
                    f"Markdown image path escapes conversion root: {target}",
                    image,
                )
                continue
            if not image.is_file():
                _add_validation_issue(
                    issues,
                    "missing_image",
                    f"Missing image '{target}' referenced by {markdown.name}",
                    image,
                )
                continue
            relative_image = resolved.relative_to(root).as_posix()
            if relative_image not in declared_images:
                _add_validation_issue(
                    issues,
                    "image_not_manifested",
                    f"Markdown image is not declared in resources.images: {target}",
                    image,
                )

    validation = required_objects["validation"]
    if require_recorded_gate:
        blocking_count = validation.get("blocking_count")
        if (
            validation.get("status") != "passed"
            or not isinstance(blocking_count, int)
            or isinstance(blocking_count, bool)
            or blocking_count != 0
            or validation.get("issues") != []
            or not isinstance(validation.get("validated_at"), str)
            or not validation.get("validated_at")
        ):
            _add_validation_issue(
                issues,
                "validation_not_passed",
                "Persisted Gate P state must be passed with zero blockers and no issues",
                manifest_path,
            )

    blocking_count = len(issues)
    return ValidationReport(
        status="passed" if blocking_count == 0 else "failed",
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
            tag = html_match.group("tag").casefold()
            if tag not in _HTML_VOID_TAGS and not re.search(
                rf"</{re.escape(tag)}\s*>", line, re.IGNORECASE
            ):
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

    visible = _markdown_without_protected_blocks(markdown)
    labels: set[str] = set()
    for match in _REFERENCE_IMAGE_USE_RE.finditer(visible):
        label = match.group("label") or match.group("alt")
        normalized = " ".join(label.split()).casefold()
        if normalized:
            labels.add(normalized)
    for match in _SHORTCUT_REFERENCE_IMAGE_USE_RE.finditer(visible):
        normalized = " ".join(match.group("label").split()).casefold()
        if normalized:
            labels.add(normalized)
    return labels


def _reference_image_analysis(markdown: str) -> tuple[list[str], list[str]]:
    """Resolve reference-image uses and return targets plus unresolved labels.

    Full, collapsed, and shortcut references are all image syntax even when a
    matching definition is absent.  Keeping unresolved labels explicit prevents
    a broken reference from disappearing from Gate P merely because there is no
    target string to inspect.
    """

    visible = _markdown_without_protected_blocks(markdown)
    uses: list[tuple[str, str]] = []
    for match in _REFERENCE_IMAGE_USE_RE.finditer(visible):
        display = match.group("label") or match.group("alt")
        normalized = " ".join(display.split()).casefold()
        if normalized:
            uses.append((display, normalized))
    for match in _SHORTCUT_REFERENCE_IMAGE_USE_RE.finditer(visible):
        display = match.group("label")
        normalized = " ".join(display.split()).casefold()
        if normalized:
            uses.append((display, normalized))

    definitions: dict[str, str] = {}
    definition_order: list[str] = []
    for match in _REFERENCE_DEFINITION_RE.finditer(visible):
        normalized = " ".join(match.group("label").split()).casefold()
        if normalized and normalized not in definitions:
            definitions[normalized] = match.group("target")
            definition_order.append(normalized)

    used_labels = {normalized for _, normalized in uses}
    targets = [
        definitions[label] for label in definition_order if label in used_labels
    ]
    unresolved: list[str] = []
    seen: set[str] = set()
    for display, normalized in uses:
        if normalized not in definitions and normalized not in seen:
            unresolved.append(display)
            seen.add(normalized)
    return targets, unresolved


def _reference_image_targets(markdown: str) -> list[str]:
    """Return targets from definitions referenced by a Markdown image."""

    targets, _ = _reference_image_analysis(markdown)
    return targets


def _chapter_asset_mapping(
    markdown: str, conversion_dir: Path, chapter_source: Path
) -> dict[str, tuple[Path, Path]]:
    """Validate and map every local chapter image reference before writes begin."""

    mapping: dict[str, tuple[Path, Path]] = {}
    visible = _markdown_without_protected_blocks(markdown)
    targets = [match.group("target") for match in _IMAGE_TARGET_RE.finditer(visible)]
    reference_targets, unresolved = _reference_image_analysis(visible)
    if unresolved:
        raise IngestionError(
            "Unresolved chapter image reference(s): " + ", ".join(unresolved)
        )
    targets.extend(reference_targets)
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

    rewritten = _substitute_outside_protected(markdown, _IMAGE_TARGET_RE, replace)
    return _substitute_outside_protected(
        rewritten, _REFERENCE_DEFINITION_RE, replace_reference_definition
    )


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


def _local_markdown_image_paths(markdown_path: Path, allowed_root: Path) -> list[Path]:
    """Resolve every package-local Markdown image beneath one trusted root."""

    source_path = Path(markdown_path)
    root = Path(allowed_root).resolve()
    try:
        text = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise IngestionError(f"Unable to inspect package Markdown {source_path}: {exc}") from exc
    _, unresolved = _reference_image_analysis(text)
    if unresolved:
        raise IngestionError(
            f"Unresolved package image reference(s) in {source_path}: "
            + ", ".join(unresolved)
        )

    resolved_images: list[Path] = []
    seen: set[Path] = set()
    for target in collect_markdown_links(source_path):
        local = _local_image_target(target)
        if local is None:
            continue
        normalized = local.replace("\\", "/")
        posix = PurePosixPath(normalized)
        windows = PureWindowsPath(normalized)
        if posix.is_absolute() or windows.is_absolute() or windows.drive:
            raise IngestionError(
                f"Absolute package image path is not allowed in {source_path}: {target}"
            )
        lexical = Path(os.path.abspath(source_path.parent.resolve() / Path(posix)))
        if not _contained(lexical, root):
            raise IngestionError(
                f"Package image path escapes package root in {source_path}: {target}"
            )
        current = root
        for part in lexical.relative_to(root).parts:
            current = current / part
            if current.is_symlink():
                raise IngestionError(
                    f"Package image path traverses a symlink in {source_path}: {target}"
                )
        resolved = lexical.resolve(strict=False)
        if not _contained(resolved, root) or not resolved.is_file():
            raise IngestionError(
                f"Referenced package image is missing or escapes in {source_path}: {target}"
            )
        if resolved not in seen:
            resolved_images.append(resolved)
            seen.add(resolved)
    return resolved_images


def _package_asset_records(package_source: Path, package_root: Path) -> list[dict[str, object]]:
    """Record the exact package-local images referenced by one source unit."""

    root = Path(package_root).resolve()
    return [
        {
            "package_path": path.relative_to(root).as_posix(),
            "sha256": sha256_file(path),
            "size": path.stat().st_size,
        }
        for path in _local_markdown_image_paths(package_source, root)
    ]


def _validate_package_markdown_images(package: Path) -> None:
    """Recheck all current Markdown image links before reusing a package."""

    root = Path(package).resolve()
    for markdown in sorted(root.rglob("*.md")):
        _local_markdown_image_paths(markdown, root)


def _required_manifest_object(manifest: dict[str, object], name: str) -> dict[str, object]:
    value = manifest.get(name)
    if not isinstance(value, dict):
        raise IngestionError(f"Conversion manifest is missing object: {name}")
    return value


def _require_conversion_gate(conversion_dir: Path) -> tuple[dict[str, object], Path]:
    """Re-run authoritative Gate P validation before loading its manifest."""

    manifest_path = Path(conversion_dir) / "conversion-manifest.json"
    if not manifest_path.is_file():
        raise IngestionError(f"Conversion manifest does not exist: {manifest_path}")
    report = validate_conversion(conversion_dir)
    if report.blocking_count:
        codes = ", ".join(issue.code for issue in report.issues)
        raise IngestionError(
            f"Conversion validation gate failed with {report.blocking_count} "
            f"blocking issue(s): {codes}"
        )
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
        "__INGESTION_PROVENANCE_INDEX__": "ingestion-provenance.json",
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


def _package_manifest_scalar(text: str, section: str, key: str) -> str | None:
    section_pattern = re.compile(rf"^(?P<indent>[ \t]*){re.escape(section)}:\s*$")
    key_pattern = re.compile(rf"^[ \t]+{re.escape(key)}:\s*(?P<value>.*?)(?:\s+#.*)?$")
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = section_pattern.match(line)
        if match is None:
            continue
        section_indent = len(match.group("indent"))
        for child in lines[index + 1 :]:
            if not child.strip() or child.lstrip().startswith("#"):
                continue
            child_indent = len(child) - len(child.lstrip(" \t"))
            if child_indent <= section_indent:
                break
            value_match = key_pattern.match(child)
            if value_match is None:
                continue
            value = value_match.group("value").strip()
            if value.startswith('"'):
                try:
                    decoded = json.loads(value)
                except json.JSONDecodeError:
                    return None
                return decoded if isinstance(decoded, str) else str(decoded)
            if len(value) >= 2 and value[0] == value[-1] == "'":
                return value[1:-1]
            return value
    return None


_REUSE_ROOT_FILES: Final[tuple[str, ...]] = (
    "BOOK.md",
    "manifest.yaml",
    "reading-ledger.yaml",
    "evidence-ledger.yaml",
    "ingestion-provenance.json",
)
_REUSE_CHAPTER_FILES: Final[tuple[str, ...]] = (
    "source.md",
    "reading.md",
    "annotated.md",
    "annotations.yaml",
    "knowledge.yaml",
)
_REUSE_SYNTHESIS_FILES: Final[tuple[str, ...]] = (
    "book-map.md",
    "core-thesis.md",
    "concept-evolution.md",
    "argument-map.md",
    "critical-reading.md",
    "full-book-reading.md",
)


def _validate_recorded_package_assets(
    package: Path,
    package_source: Path,
    chapter_id: str,
    unit: dict[str, object],
) -> None:
    """Match one provenance unit's asset records to its current Markdown links."""

    root = Path(package).resolve()
    assets = unit.get("assets")
    if not isinstance(assets, list):
        raise IngestionError(
            f"Existing package provenance lacks asset records for {chapter_id}"
        )
    actual_paths = {
        path.relative_to(root).as_posix()
        for path in _local_markdown_image_paths(package_source, root)
    }
    recorded_paths: set[str] = set()
    for record in assets:
        if not isinstance(record, dict):
            raise IngestionError(
                f"Existing package asset provenance is invalid for {chapter_id}"
            )
        value = record.get("package_path")
        if not isinstance(value, str):
            raise IngestionError(
                f"Existing package asset provenance has no path for {chapter_id}"
            )
        posix = PurePosixPath(value.replace("\\", "/"))
        windows = PureWindowsPath(value)
        if (
            posix.is_absolute()
            or windows.is_absolute()
            or windows.drive
            or any(part in {"", ".", ".."} for part in posix.parts)
        ):
            raise IngestionError(
                f"Existing package asset provenance escapes for {chapter_id}: {value}"
            )
        asset = root / Path(posix)
        resolved = asset.resolve(strict=False)
        if (
            not value.startswith(f"chapters/{chapter_id}/assets/")
            or not _contained(resolved, root)
            or asset.is_symlink()
            or not asset.is_file()
            or record.get("sha256") != sha256_file(asset)
            or record.get("size") != asset.stat().st_size
        ):
            raise IngestionError(
                f"Existing package asset identity differs for {chapter_id}: {value}"
            )
        recorded_paths.add(value)
    if recorded_paths != actual_paths or len(recorded_paths) != len(assets):
        raise IngestionError(
            f"Existing package asset links differ from provenance for {chapter_id}"
        )


def _validate_existing_package_reuse(
    package: Path,
    conversion_root: Path,
    conversion_manifest: Path,
    pdf_hash: str,
    chapter_plans: list[tuple[str, Path, str]],
) -> None:
    """Require package artifacts, conversion identities, and source-unit provenance."""

    for name in _REUSE_ROOT_FILES:
        if not (package / name).is_file():
            raise IngestionError(f"Existing package is missing required artifact: {name}")
    for name in _REUSE_SYNTHESIS_FILES:
        if not (package / "synthesis" / name).is_file():
            raise IngestionError(
                f"Existing package is missing synthesis artifact: {name}"
            )
    manifest_path = package / "manifest.yaml"
    try:
        manifest_text = manifest_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise IngestionError(f"Unable to read existing package manifest: {exc}") from exc
    recorded_hash = _package_manifest_scalar(
        manifest_text, "ingestion", "source_pdf_sha256"
    )
    gate_status = _package_manifest_scalar(manifest_text, "ingestion", "gate_status")
    conversion_dir_value = _package_manifest_scalar(
        manifest_text, "ingestion", "conversion_dir"
    )
    conversion_manifest_value = _package_manifest_scalar(
        manifest_text, "ingestion", "conversion_manifest"
    )
    provenance_value = _package_manifest_scalar(
        manifest_text, "ingestion", "provenance_index"
    )
    if recorded_hash != pdf_hash or gate_status != "passed":
        raise IngestionError("Existing package ingestion identity or gate status differs")
    if not conversion_dir_value or not conversion_manifest_value:
        raise IngestionError("Existing package lacks conversion provenance paths")
    recorded_dir = Path(conversion_dir_value)
    if not recorded_dir.is_absolute():
        recorded_dir = package / recorded_dir
    recorded_manifest = Path(conversion_manifest_value)
    if not recorded_manifest.is_absolute():
        recorded_manifest = package / recorded_manifest
    if (
        recorded_dir.resolve() != conversion_root.resolve()
        or recorded_manifest.resolve() != conversion_manifest.resolve()
    ):
        raise IngestionError("Existing package points to a different conversion generation")

    provenance_path = package / (provenance_value or "ingestion-provenance.json")
    if provenance_path.resolve() != (package / "ingestion-provenance.json").resolve():
        raise IngestionError("Existing package provenance index path is invalid")
    try:
        provenance = read_json(provenance_path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise IngestionError(f"Existing package provenance index is invalid: {exc}") from exc
    if (
        provenance.get("schema_version") != 1
        or provenance.get("source_pdf_sha256") != pdf_hash
        or provenance.get("conversion_manifest_sha256")
        != sha256_file(conversion_manifest)
    ):
        raise IngestionError("Existing package provenance identity does not match")

    units = provenance.get("source_units")
    if not isinstance(units, list):
        raise IngestionError("Existing package provenance has no source-unit list")
    expected_ids = [chapter_id for chapter_id, _, _ in chapter_plans]
    actual_chapters_root = package / "chapters"
    actual_ids = sorted(
        path.name
        for path in actual_chapters_root.glob("ch[0-9][0-9]")
        if path.is_dir()
    )
    if actual_ids != expected_ids or len(units) != len(chapter_plans):
        raise IngestionError("Existing package chapter identities differ from conversion")
    by_id = {
        unit.get("chapter_id"): unit for unit in units if isinstance(unit, dict)
    }
    for chapter_id, conversion_source, _ in chapter_plans:
        chapter_dir = package / "chapters" / chapter_id
        for name in _REUSE_CHAPTER_FILES:
            if not (chapter_dir / name).is_file():
                raise IngestionError(
                    f"Existing package chapter {chapter_id} is missing {name}"
                )
        unit = by_id.get(chapter_id)
        if not isinstance(unit, dict):
            raise IngestionError(
                f"Existing package provenance lacks source unit {chapter_id}"
            )
        try:
            expected_relative = conversion_source.resolve().relative_to(
                conversion_root.resolve()
            ).as_posix()
        except ValueError as exc:
            raise IngestionError("Conversion source unit escapes conversion root") from exc
        package_source = chapter_dir / "source.md"
        if (
            unit.get("conversion_path") != expected_relative
            or unit.get("conversion_sha256") != sha256_file(conversion_source)
            or unit.get("package_source")
            != package_source.relative_to(package).as_posix()
            or unit.get("package_source_sha256") != sha256_file(package_source)
        ):
            raise IngestionError(
                f"Existing package source identity differs for {chapter_id}"
            )
        _validate_recorded_package_assets(
            package, package_source, chapter_id, unit
        )
    _validate_package_markdown_images(package)


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
    """Return source units exclusively in the order sealed by split-index.json."""

    root = Path(conversion_dir).resolve()
    manifest = read_json(root / "conversion-manifest.json")
    artifacts = _required_manifest_object(manifest, "artifacts")
    split_record = artifacts.get("split_index")
    split_value = split_record.get("path") if isinstance(split_record, dict) else None
    if not isinstance(split_value, str):
        raise IngestionError("Conversion manifest has no split index identity")
    split_path = root / Path(PurePosixPath(split_value))
    try:
        split = read_json(split_path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise IngestionError(f"Conversion split index is invalid: {exc}") from exc
    mode = split.get("mode")
    units = split.get("units")
    if mode not in {"chapters", "formatted_fallback"} or not isinstance(units, list):
        raise IngestionError("Conversion split index has no ordered source units")
    sources: list[Path] = []
    for unit in units:
        if not isinstance(unit, dict) or not isinstance(unit.get("path"), str):
            raise IngestionError("Conversion split unit identity is invalid")
        value = unit["path"]
        candidate = (root / Path(PurePosixPath(value))).resolve(strict=False)
        if not _contained(candidate, root) or not candidate.is_file():
            raise IngestionError(f"Conversion split unit is missing or escapes: {value}")
        if mode == "chapters" and (
            unit.get("kind") != "chapter"
            or not value.startswith("拆分/章节/")
            or candidate.name == "README.md"
        ):
            raise IngestionError(f"Conversion chapter unit identity is invalid: {value}")
        if mode == "formatted_fallback" and unit.get("kind") != "formatted_fallback":
            raise IngestionError("Conversion fallback unit identity is invalid")
        sources.append(candidate)
    if not sources or (mode == "formatted_fallback" and len(sources) != 1):
        raise IngestionError(
            "No conversion source units are available for package initialization"
        )
    return sources


def initialize_book_package(
    conversion_dir: Path, books_root: Path, templates_root: Path | None = None
) -> Path:
    """Initialize a staging reading package from a conversion that passed its gate."""

    conversion_root = Path(conversion_dir).resolve()
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
    package = prepare_publication_target(Path(books_root), Path(books_root) / slug)
    if package.exists():
        existing_hash = _recorded_package_pdf_hash(package)
        if existing_hash != pdf_hash:
            raise IngestionError("Existing package records a different or unknown source PDF SHA-256")
        _validate_existing_package_reuse(
            package,
            conversion_root,
            conversion_manifest,
            pdf_hash,
            chapter_plans,
        )
        return package

    imported_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    values = _template_values(title, slug, language, pdf_path, pdf_hash, imported_at)
    values.update(
        {
            "__INGESTION_PARSER__": f"{engine.get('name', 'unknown')} {engine.get('version', '')}".strip(),
            "__CONVERSION_DIR__": str(conversion_root.resolve()),
            "__CONVERSION_MANIFEST__": str(conversion_manifest.resolve()),
            "__INGESTION_PROVENANCE_INDEX__": "ingestion-provenance.json",
        }
    )
    staging_package = Path(
        tempfile.mkdtemp(prefix=f".{slug}.package-", dir=package.parent)
    )
    try:
        _copy_rendered_templates(templates / "book", staging_package, values)
        _copy_rendered_templates(templates / "synthesis", staging_package / "synthesis", values)
        source_units: list[dict[str, object]] = []
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
            package_source = chapter_dir / "source.md"
            atomic_write_text(
                package_source, add_stable_paragraph_ids(copied, chapter_id)
            )
            source_units.append(
                {
                    "chapter_id": chapter_id,
                    "conversion_path": chapter_source.resolve()
                    .relative_to(conversion_root)
                    .as_posix(),
                    "conversion_sha256": sha256_file(chapter_source),
                    "package_source": package_source.relative_to(
                        staging_package
                    ).as_posix(),
                    "package_source_sha256": sha256_file(package_source),
                    "assets": _package_asset_records(
                        package_source, staging_package
                    ),
                }
            )
        provenance = {
            "schema_version": 1,
            "source_pdf_sha256": pdf_hash,
            "conversion_dir": str(conversion_root),
            "conversion_manifest": str(conversion_manifest.resolve()),
            "conversion_manifest_sha256": sha256_file(conversion_manifest),
            "created_at": imported_at,
            "source_units": source_units,
        }
        write_json(staging_package / "ingestion-provenance.json", provenance)
        atomic_publish_directory(staging_package, package)
    finally:
        if staging_package.exists():
            shutil.rmtree(staging_package, ignore_errors=True)
    return package
