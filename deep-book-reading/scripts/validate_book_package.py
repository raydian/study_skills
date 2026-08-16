#!/usr/bin/env python3
"""Structural validator for deep-book-reading output packages.

This intentionally uses only the Python standard library. It validates observable
contracts; semantic fidelity still requires the audit in workflows/verification.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from pdf_ingestion import (
    IngestionError,
    _local_markdown_image_paths,
    read_json,
    sha256_file,
    validate_conversion,
)


class Issue(NamedTuple):
    severity: str
    code: str
    path: str
    message: str


ROOT_FILES = ("BOOK.md", "manifest.yaml", "reading-ledger.yaml", "evidence-ledger.yaml")
CHAPTER_FILES = ("source.md", "reading.md", "annotated.md", "annotations.yaml", "knowledge.yaml")
SYNTHESIS_FILES = (
    "book-map.md",
    "core-thesis.md",
    "concept-evolution.md",
    "argument-map.md",
    "critical-reading.md",
    "full-book-reading.md",
)
COVERAGE_KINDS = (
    "chapters",
    "sections",
    "pages",
    "paragraphs",
    "figures",
    "tables",
    "equations",
    "code_blocks",
    "footnotes",
    "sidebars",
    "appendices",
)
KNOWLEDGE_TYPES = {
    "Concept",
    "Definition",
    "Claim",
    "Principle",
    "Framework",
    "Method",
    "Pattern",
    "Rule",
    "Evidence",
    "Case",
    "Counterexample",
    "Limitation",
}
ATTRIBUTIONS = {
    "author_claim",
    "source_evidence",
    "quoted_view",
    "case",
    "ai_explanation",
    "ai_inference",
    "ai_synthesis",
    "critical_analysis",
    "editorial_note",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def add(issues: list[Issue], severity: str, code: str, path: Path, message: str) -> None:
    issues.append(Issue(severity, code, str(path), message))


def manifest_scalar(text: str, section: str, key: str) -> str | None:
    """Read one plain scalar from a simple, indented manifest mapping.

    The package validator deliberately does not depend on a YAML library.  The
    manifest contract uses simple top-level mappings for the fields checked
    here, so a small indentation-aware reader is sufficient and keeps this
    script standard-library-only.
    """

    section_pattern = re.compile(rf"^(?P<indent>[ \t]*){re.escape(section)}:\s*(?:#.*)?$")
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


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{64}", value) is not None


def _is_contained(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _project_root_for_package(package: Path) -> Path:
    package_root = package.resolve()
    return (
        package_root.parent.parent
        if package_root.parent.name == "books"
        else package_root.parent
    )


def _resolve_recorded_path(
    manifest: Path,
    value: str | None,
    allowed_root: Path,
    issues: list[Issue],
    label: str,
) -> Path | None:
    if not value:
        add(
            issues,
            "error",
            "INGESTION_MANIFEST_MISSING",
            manifest,
            f"PDF package requires ingestion.{label}",
        )
        return None
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = manifest.parent / candidate
    resolved = candidate.resolve(strict=False)
    if not _is_contained(resolved, allowed_root.resolve()):
        add(
            issues,
            "error",
            "INGESTION_PATH_ESCAPE",
            candidate,
            f"ingestion.{label} escapes its allowed root",
        )
        return None
    return resolved


def validate_pdf_ingestion(manifest: Path, text: str, issues: list[Issue]) -> None:
    """Revalidate a PDF package's conversion, source identity, and provenance."""

    source_format = manifest_scalar(text, "source", "format")
    if source_format is None or source_format.lower() != "pdf":
        return
    package = manifest.parent.resolve()
    project_root = _project_root_for_package(package)
    markdown_root = (project_root / "markdown").resolve()

    gate_status = manifest_scalar(text, "ingestion", "gate_status")
    if gate_status != "passed":
        add(
            issues,
            "error",
            "INGESTION_GATE_NOT_PASSED",
            manifest,
            "PDF package ingestion.gate_status must be passed",
        )

    conversion_dir = _resolve_recorded_path(
        manifest,
        manifest_scalar(text, "ingestion", "conversion_dir"),
        markdown_root,
        issues,
        "conversion_dir",
    )
    conversion_manifest = _resolve_recorded_path(
        manifest,
        manifest_scalar(text, "ingestion", "conversion_manifest"),
        markdown_root,
        issues,
        "conversion_manifest",
    )
    if conversion_dir is None or conversion_manifest is None:
        return
    if not conversion_dir.is_dir():
        add(
            issues,
            "error",
            "INGESTION_CONVERSION_DIR_MISSING",
            conversion_dir,
            "PDF conversion directory does not exist",
        )
        return
    expected_manifest = (conversion_dir / "conversion-manifest.json").resolve()
    if conversion_manifest != expected_manifest:
        add(
            issues,
            "error",
            "INGESTION_MANIFEST_ROOT_MISMATCH",
            conversion_manifest,
            "conversion_manifest must identify conversion_dir/conversion-manifest.json",
        )
        return
    if not conversion_manifest.is_file():
        add(
            issues,
            "error",
            "INGESTION_MANIFEST_MISSING",
            conversion_manifest,
            "PDF conversion manifest does not exist",
        )
        return
    try:
        conversion = read_json(conversion_manifest)
    except json.JSONDecodeError as exc:
        add(
            issues,
            "error",
            "INGESTION_MANIFEST_INVALID",
            conversion_manifest,
            f"PDF conversion manifest is malformed JSON: {exc}",
        )
        return
    except (OSError, UnicodeError, ValueError) as exc:
        add(
            issues,
            "error",
            "INGESTION_MANIFEST_INVALID",
            conversion_manifest,
            f"PDF conversion manifest is invalid: {exc}",
        )
        return

    validation = conversion.get("validation")
    if (
        not isinstance(validation, dict)
        or validation.get("status") != "passed"
        or validation.get("blocking_count") != 0
    ):
        add(
            issues,
            "error",
            "INGESTION_GATE_NOT_PASSED",
            conversion_manifest,
            "PDF conversion manifest must record passed with zero blockers",
        )

    conversion_report = validate_conversion(conversion_dir)
    for conversion_issue in conversion_report.issues:
        add(
            issues,
            "error",
            "INGESTION_CONVERSION_" + conversion_issue.code.upper(),
            conversion_issue.path,
            conversion_issue.message,
        )

    source = conversion.get("source")
    conversion_hash = source.get("sha256") if isinstance(source, dict) else None
    pdf_value = source.get("pdf") if isinstance(source, dict) else None
    package_hash = manifest_scalar(text, "ingestion", "source_pdf_sha256")
    package_source_hash = manifest_scalar(text, "source", "source_sha256")
    if not isinstance(pdf_value, str) or not Path(pdf_value).is_absolute() or not Path(pdf_value).is_file():
        add(
            issues,
            "error",
            "INGESTION_SOURCE_PDF_MISSING",
            Path(pdf_value) if isinstance(pdf_value, str) else conversion_manifest,
            "Conversion source.pdf must identify the existing original PDF",
        )
    else:
        actual_hash = sha256_file(Path(pdf_value))
        if conversion_hash != actual_hash:
            add(
                issues,
                "error",
                "INGESTION_SOURCE_HASH_MISMATCH",
                Path(pdf_value),
                "Original PDF SHA-256 no longer matches conversion source.sha256",
            )
    if (
        not is_sha256(conversion_hash)
        or not is_sha256(package_hash)
        or not is_sha256(package_source_hash)
        or conversion_hash.lower() != package_hash.lower()
        or conversion_hash.lower() != package_source_hash.lower()
    ):
        add(
            issues,
            "error",
            "INGESTION_SOURCE_HASH_MISMATCH",
            conversion_manifest,
            "Conversion, ingestion, and package source PDF hashes must match",
        )

    provenance_value = manifest_scalar(text, "ingestion", "provenance_index")
    provenance_path = _resolve_recorded_path(
        manifest,
        provenance_value,
        package,
        issues,
        "provenance_index",
    )
    if provenance_path is None:
        return
    if provenance_path != (package / "ingestion-provenance.json").resolve():
        add(
            issues,
            "error",
            "INGESTION_PROVENANCE_INVALID",
            provenance_path,
            "PDF package provenance_index must identify ingestion-provenance.json",
        )
        return
    try:
        provenance = read_json(provenance_path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        add(
            issues,
            "error",
            "INGESTION_PROVENANCE_INVALID",
            provenance_path,
            f"PDF package provenance index is invalid: {exc}",
        )
        return
    if (
        provenance.get("schema_version") != 1
        or provenance.get("source_pdf_sha256") != conversion_hash
        or provenance.get("conversion_manifest_sha256")
        != sha256_file(conversion_manifest)
        or not isinstance(provenance.get("source_units"), list)
        or not provenance.get("source_units")
    ):
        add(
            issues,
            "error",
            "INGESTION_PROVENANCE_INVALID",
            provenance_path,
            "PDF package provenance identity does not match the conversion",
        )
        return
    artifacts = conversion.get("artifacts")
    split_record = artifacts.get("split_index") if isinstance(artifacts, dict) else None
    split_value = split_record.get("path") if isinstance(split_record, dict) else None
    try:
        split_index = read_json(
            conversion_dir / split_value
            if isinstance(split_value, str)
            else conversion_dir / "__missing_split_index__"
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        add(
            issues,
            "error",
            "INGESTION_PROVENANCE_INVALID",
            provenance_path,
            f"Conversion split identity cannot be reconciled: {exc}",
        )
        return
    split_units = split_index.get("units")
    expected_conversion_paths = [
        unit.get("path")
        for unit in split_units
        if isinstance(unit, dict) and isinstance(unit.get("path"), str)
    ] if isinstance(split_units, list) else []
    actual_chapter_ids = sorted(
        path.name
        for path in (package / "chapters").glob("ch[0-9][0-9]")
        if path.is_dir()
    )
    expected_chapter_ids = [
        f"ch{number:02d}"
        for number in range(1, len(expected_conversion_paths) + 1)
    ]
    provenance_units = provenance["source_units"]
    provenance_ids = [
        unit.get("chapter_id") if isinstance(unit, dict) else None
        for unit in provenance_units
    ]
    if (
        not expected_conversion_paths
        or actual_chapter_ids != expected_chapter_ids
        or provenance_ids != expected_chapter_ids
        or len(set(provenance_ids)) != len(provenance_ids)
    ):
        add(
            issues,
            "error",
            "INGESTION_PROVENANCE_INVALID",
            provenance_path,
            "PDF package chapters and provenance units must exactly match ordered split units",
        )

    for index, unit in enumerate(provenance_units):
        if not isinstance(unit, dict):
            add(
                issues,
                "error",
                "INGESTION_PROVENANCE_INVALID",
                provenance_path,
                "PDF package source-unit provenance must be an object",
            )
            continue
        conversion_value = unit.get("conversion_path")
        package_value = unit.get("package_source")
        if not isinstance(conversion_value, str) or not isinstance(package_value, str):
            add(
                issues,
                "error",
                "INGESTION_PROVENANCE_INVALID",
                provenance_path,
                "PDF package source-unit paths are missing",
            )
            continue
        chapter_id = unit.get("chapter_id")
        expected_conversion = (
            expected_conversion_paths[index]
            if index < len(expected_conversion_paths)
            else None
        )
        expected_package = (
            f"chapters/{chapter_id}/source.md"
            if isinstance(chapter_id, str)
            else None
        )
        if conversion_value != expected_conversion or package_value != expected_package:
            add(
                issues,
                "error",
                "INGESTION_PROVENANCE_INVALID",
                provenance_path,
                "PDF package source-unit identity differs from the ordered split unit",
            )
        conversion_source = (conversion_dir / conversion_value).resolve(strict=False)
        package_source = (package / package_value).resolve(strict=False)
        if (
            not _is_contained(conversion_source, conversion_dir)
            or not _is_contained(package_source, package)
            or not conversion_source.is_file()
            or not package_source.is_file()
            or unit.get("conversion_sha256") != sha256_file(conversion_source)
            or unit.get("package_source_sha256") != sha256_file(package_source)
        ):
            add(
                issues,
                "error",
                "INGESTION_PROVENANCE_INVALID",
                provenance_path,
                "PDF package source-unit provenance no longer resolves or hashes differ",
            )

        assets = unit.get("assets")
        if not isinstance(assets, list):
            add(
                issues,
                "error",
                "INGESTION_PROVENANCE_INVALID",
                provenance_path,
                "PDF package source-unit asset provenance must be a list",
            )
            continue
        try:
            actual_assets = {
                path.relative_to(package).as_posix()
                for path in _local_markdown_image_paths(package_source, package)
            }
        except IngestionError as exc:
            add(
                issues,
                "error",
                "INGESTION_PACKAGE_IMAGE_INVALID",
                package_source,
                str(exc),
            )
            actual_assets = set()
        recorded_assets: set[str] = set()
        for asset_record in assets:
            value = (
                asset_record.get("package_path")
                if isinstance(asset_record, dict)
                else None
            )
            if not isinstance(value, str):
                add(
                    issues,
                    "error",
                    "INGESTION_PROVENANCE_INVALID",
                    provenance_path,
                    "PDF package asset provenance path is invalid",
                )
                continue
            asset = (package / value).resolve(strict=False)
            if (
                not _is_contained(asset, package)
                or not asset.is_file()
                or asset_record.get("sha256") != sha256_file(asset)
                or asset_record.get("size") != asset.stat().st_size
            ):
                add(
                    issues,
                    "error",
                    "INGESTION_PROVENANCE_INVALID",
                    provenance_path,
                    "PDF package asset provenance no longer resolves or hashes differ",
                )
            recorded_assets.add(value)
        if recorded_assets != actual_assets or len(recorded_assets) != len(assets):
            add(
                issues,
                "error",
                "INGESTION_PROVENANCE_INVALID",
                provenance_path,
                "PDF package asset links and provenance records differ",
            )

    for markdown in sorted(package.rglob("*.md")):
        try:
            _local_markdown_image_paths(markdown, package)
        except IngestionError as exc:
            add(
                issues,
                "error",
                "INGESTION_PACKAGE_IMAGE_INVALID",
                markdown,
                str(exc),
            )


def validate_yaml_contract(path: Path, issues: list[Issue]) -> None:
    text = read(path)
    if "annotations.yaml" == path.name:
        if "source_refs:" not in text:
            add(issues, "error", "ANNOTATION_UNTRACED", path, "annotations require source_refs")
        if not any(f"attribution: {value}" in text for value in ATTRIBUTIONS):
            add(issues, "error", "ATTRIBUTION_MISSING", path, "annotation attribution is missing or invalid")
        if "revision:" not in text:
            add(issues, "error", "ANNOTATION_REVISION_MISSING", path, "annotations require revision metadata")
    elif "knowledge.yaml" == path.name:
        if "source_refs:" not in text:
            add(issues, "error", "KNOWLEDGE_UNTRACED", path, "knowledge units require source_refs")
        found = set(re.findall(r"^\s*type:\s*([A-Za-z]+)\s*$", text, re.MULTILINE))
        invalid = found - KNOWLEDGE_TYPES
        if invalid:
            add(issues, "error", "KNOWLEDGE_TYPE_INVALID", path, f"invalid types: {sorted(invalid)}")


def validate_chapter(chapter: Path, issues: list[Issue]) -> None:
    for name in CHAPTER_FILES:
        path = chapter / name
        if not path.is_file():
            add(issues, "error", "CHAPTER_FILE_MISSING", path, f"required chapter artifact {name} is missing")
    if any(not (chapter / name).is_file() for name in CHAPTER_FILES):
        return

    source = chapter / "source.md"
    source_text = read(source)
    if "source-state: sealed" not in source_text:
        add(issues, "error", "SOURCE_NOT_SEALED", source, "canonical source must be sealed")
    paragraph_ids = re.findall(r'<p\s+id="(ch\d+-p\d{3,})"', source_text)
    if not paragraph_ids:
        add(issues, "error", "SOURCE_LOCATOR_MISSING", source, "no stable paragraph locator found")
    if len(paragraph_ids) != len(set(paragraph_ids)):
        add(issues, "error", "SOURCE_LOCATOR_DUPLICATE", source, "paragraph locators must be unique")
    if "<!-- page:" not in source_text:
        add(issues, "error", "PAGE_LOCATOR_MISSING", source, "printed page locator is missing")

    reading = chapter / "reading.md"
    reading_text = read(reading)
    claim_lines = [line for line in reading_text.splitlines() if re.search(r'id=["\']r-ch\d+-\d{3,}["\']', line)]
    if not claim_lines:
        add(issues, "error", "READING_CLAIM_ID_MISSING", reading, "no reading claim IDs found")
    for line in claim_lines:
        if "[source:" not in line:
            add(issues, "error", "READING_UNTRACED", reading, "a material reading claim lacks inline source refs")

    validate_yaml_contract(chapter / "annotations.yaml", issues)
    validate_yaml_contract(chapter / "knowledge.yaml", issues)


def validate_package(package: Path) -> list[Issue]:
    package = Path(package)
    issues: list[Issue] = []
    if not package.is_dir():
        return [Issue("error", "PACKAGE_NOT_FOUND", str(package), "book package directory does not exist")]

    for name in ROOT_FILES:
        path = package / name
        if not path.is_file():
            add(issues, "error", "ROOT_FILE_MISSING", path, f"required root artifact {name} is missing")

    manifest = package / "manifest.yaml"
    if manifest.is_file():
        text = read(manifest)
        if not re.search(r"source_state:\s*sealed\b", text):
            add(issues, "error", "MANIFEST_SOURCE_NOT_SEALED", manifest, "manifest source_state must be sealed")
        if not re.search(r"source_sha256:\s*[\"']?[0-9a-fA-F]{64}[\"']?", text):
            add(issues, "error", "SOURCE_HASH_MISSING", manifest, "manifest requires a 64-character SHA-256")
        validate_pdf_ingestion(manifest, text, issues)

    ledger = package / "reading-ledger.yaml"
    if ledger.is_file():
        text = read(ledger)
        for number in range(6):
            if not re.search(rf"pass_{number}:\s*(complete|in_progress|pending|blocked)\b", text):
                add(issues, "error", "PASS_STATE_MISSING", ledger, f"PASS {number} state is missing")
        for kind in COVERAGE_KINDS:
            if not re.search(rf"^\s{{2}}{re.escape(kind)}:\s*", text, re.MULTILINE):
                add(issues, "error", "COVERAGE_KIND_MISSING", ledger, f"coverage kind {kind} is missing")

    chapters_root = package / "chapters"
    chapters = sorted(path for path in chapters_root.glob("ch[0-9][0-9]") if path.is_dir()) if chapters_root.is_dir() else []
    if not chapters:
        add(issues, "error", "CHAPTERS_MISSING", chapters_root, "no chapter directories found")
    for chapter in chapters:
        validate_chapter(chapter, issues)

    synthesis = package / "synthesis"
    for name in SYNTHESIS_FILES:
        path = synthesis / name
        if not path.is_file():
            add(issues, "error", "SYNTHESIS_FILE_MISSING", path, f"required synthesis artifact {name} is missing")

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a deep-book-reading book package")
    parser.add_argument("package", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    issues = validate_package(args.package)
    if args.as_json:
        print(json.dumps([issue._asdict() for issue in issues], ensure_ascii=False, indent=2))
    elif issues:
        for issue in issues:
            print(f"{issue.severity.upper()} {issue.code} {issue.path}: {issue.message}")
    else:
        print("OK: book package satisfies structural contracts")
    return 1 if any(issue.severity == "error" for issue in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
