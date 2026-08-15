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
