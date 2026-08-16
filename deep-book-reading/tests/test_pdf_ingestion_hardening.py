import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
INGESTION_PATH = ROOT / "scripts" / "pdf_ingestion.py"


def load_ingestion():
    spec = importlib.util.spec_from_file_location("pdf_ingestion_hardening", INGESTION_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("pdf ingestion module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_record(path: Path, root: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size": path.stat().st_size,
    }


def make_valid_conversion(
    root: Path,
    *,
    formatted_text: str = "# 第一章 系统\n\n正文。\n",
    warnings: list[dict[str, object]] | None = None,
) -> tuple[Path, dict[str, object]]:
    """Create the schema exercised by Gate P without invoking MinerU."""

    root.mkdir(parents=True)
    pdf = root.parent.parent.parent / "系统思考.pdf"
    pdf.write_bytes(b"%PDF-1.7\n1 0 obj <</Type /Page>>\nendobj\n%%EOF\n")

    raw = root / "系统思考.md"
    formatted = root / "系统思考-格式化.md"
    normalization = root / "normalization-log.json"
    content_list = root / "mineru" / "book_content_list_v2.json"
    chapter = root / "拆分" / "章节" / "01-第一章 系统.md"
    split_index = root / "拆分" / "split-index.json"
    content_list.parent.mkdir(parents=True)
    chapter.parent.mkdir(parents=True)

    raw.write_text(formatted_text, encoding="utf-8")
    formatted.write_text(formatted_text, encoding="utf-8")
    normalization.write_text("[]\n", encoding="utf-8")
    content_list.write_text(
        json.dumps({"pages": [{"page_idx": 0, "type": "text"}]}) + "\n",
        encoding="utf-8",
    )
    chapter.write_text(formatted_text, encoding="utf-8")
    split_payload = {
        "schema_version": 1,
        "source_path": formatted.relative_to(root).as_posix(),
        "source_sha256": hashlib.sha256(formatted.read_bytes()).hexdigest(),
        "source_char_count": len(formatted_text),
        "mode": "chapters",
        "units": [
            {
                "kind": "chapter",
                "path": chapter.relative_to(root).as_posix(),
                "start": 0,
                "end": len(formatted_text),
                "source_sha256": text_sha256(formatted_text),
                "sha256": hashlib.sha256(chapter.read_bytes()).hexdigest(),
                "size": chapter.stat().st_size,
            }
        ],
        "exclusions": [],
    }
    split_index.write_text(
        json.dumps(split_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    raw_record = file_record(raw, root)
    formatted_record = file_record(formatted, root)
    normalization_record = file_record(normalization, root)
    content_record = {
        **file_record(content_list, root),
        "source_path": "book_content_list_v2.json",
        "kind": "content_list",
    }
    split_index_record = file_record(split_index, root)
    chapter_record = file_record(chapter, root)
    timestamp = "2026-08-15T00:00:00Z"
    manifest: dict[str, object] = {
        "schema_version": 2,
        "book": {
            "title": "系统思考",
            "category": "商业管理",
            "slug": "系统思考",
            "language": "ch",
        },
        "source": {
            "pdf": str(pdf.resolve()),
            "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
            "size": pdf.stat().st_size,
            "mtime_ns": pdf.stat().st_mtime_ns,
            "fingerprinted_at": timestamp,
        },
        "engine": {
            "name": "MinerU",
            "version": "1.3.0",
            "backend": "pipeline",
            "language": "ch",
            "executable": "/usr/local/bin/mineru",
            "command": [
                "/usr/local/bin/mineru",
                "-p",
                str(pdf.resolve()),
                "-o",
                str((root.parent / "mineru-stage").resolve()),
                "-b",
                "pipeline",
                "-l",
                "ch",
            ],
            "mode": "run",
        },
        "timestamps": {
            "started_at": timestamp,
            "mineru_completed_at": timestamp,
            "conversion_completed_at": timestamp,
        },
        "pages": {
            "source_count": 1,
            "mineru_count": 1,
            "reconciliation": "matched",
            "records": [{"page_index": 0, "record_count": 1}],
        },
        "artifacts": {
            "raw_markdown": raw_record,
            "formatted_markdown": formatted_record,
            "normalization_log": normalization_record,
            "split_index": split_index_record,
        },
        "stages": {
            "imported": {
                "status": "complete",
                "completed_at": timestamp,
                "outputs": [raw_record, content_record],
            },
            "formatted": {
                "status": "complete",
                "completed_at": timestamp,
                "outputs": [formatted_record, normalization_record],
            },
            "split": {
                "status": "complete",
                "completed_at": timestamp,
                "outputs": [split_index_record, chapter_record],
            },
        },
        "resources": {"images": [], "mineru_json": [content_record]},
        "warnings": warnings or [],
        "validation": {
            "status": "passed",
            "blocking_count": 0,
            "issues": [],
            "validated_at": timestamp,
        },
    }
    (root / "conversion-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return pdf, manifest


class AuthoritativeGatePTests(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        self.base = Path(self._tempdir.name)
        self.root = self.base / "markdown" / "商业管理" / "系统思考"
        self.module = load_ingestion()
        self.pdf, self.manifest = make_valid_conversion(self.root)

    def tearDown(self):
        self._tempdir.cleanup()

    def codes(self) -> set[str]:
        return {issue.code for issue in self.module.validate_conversion(self.root).issues}

    def rewrite_manifest(self) -> None:
        (self.root / "conversion-manifest.json").write_text(
            json.dumps(self.manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def replace_source_pdf_with_page_count(self, page_count: int) -> None:
        payload = (
            b"%PDF-1.7\n"
            + b"\n".join(
                f"{index} 0 obj <</Type /Page>> endobj".encode("ascii")
                for index in range(1, page_count + 1)
            )
            + b"\n%%EOF\n"
        )
        self.pdf.write_bytes(payload)
        self.manifest["source"].update(
            {
                "sha256": hashlib.sha256(payload).hexdigest(),
                "size": len(payload),
                "mtime_ns": self.pdf.stat().st_mtime_ns,
            }
        )

    def forge_reordered_two_unit_split(self) -> None:
        first = "# 第一章 系统\n\n第一章正文。\n\n"
        second = "# 第二章 反馈\n\n第二章正文。\n"
        formatted_text = first + second
        raw = self.root / "系统思考.md"
        formatted = self.root / "系统思考-格式化.md"
        raw.write_text(formatted_text, encoding="utf-8")
        formatted.write_text(formatted_text, encoding="utf-8")
        raw_record = file_record(raw, self.root)
        formatted_record = file_record(formatted, self.root)
        self.manifest["artifacts"]["raw_markdown"] = raw_record
        self.manifest["artifacts"]["formatted_markdown"] = formatted_record
        self.manifest["stages"]["imported"]["outputs"][0] = raw_record
        self.manifest["stages"]["formatted"]["outputs"][0] = formatted_record

        chapter_root = self.root / "拆分" / "章节"
        chapter_one = chapter_root / "01-第一章 系统.md"
        chapter_two = chapter_root / "02-第二章 反馈.md"
        chapter_one.write_text(first, encoding="utf-8")
        chapter_two.write_text(second, encoding="utf-8")
        first_unit = {
            "kind": "chapter",
            **file_record(chapter_one, self.root),
            "start": 0,
            "end": len(first),
            "source_sha256": text_sha256(first),
        }
        second_unit = {
            "kind": "chapter",
            **file_record(chapter_two, self.root),
            "start": len(first),
            "end": len(formatted_text),
            "source_sha256": text_sha256(second),
        }
        split_index = self.root / "拆分" / "split-index.json"
        split_payload = {
            "schema_version": 1,
            "source_path": formatted.relative_to(self.root).as_posix(),
            "source_sha256": text_sha256(formatted_text),
            "source_char_count": len(formatted_text),
            "mode": "chapters",
            "units": [second_unit, first_unit],
            "exclusions": [],
        }
        split_index.write_text(
            json.dumps(split_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        split_record = file_record(split_index, self.root)
        self.manifest["artifacts"]["split_index"] = split_record
        self.manifest["stages"]["split"]["outputs"] = [
            split_record,
            file_record(chapter_two, self.root),
            file_record(chapter_one, self.root),
        ]
        self.rewrite_manifest()

    def test_valid_complete_conversion_passes_authoritative_gate(self):
        report = self.module.validate_conversion(self.root)
        self.assertEqual("passed", report.status)
        self.assertEqual(0, report.blocking_count, report.issues)

    def test_gate_rejects_malformed_manifest_and_missing_declared_artifacts(self):
        (self.root / "conversion-manifest.json").write_text("{not-json", encoding="utf-8")
        self.assertIn("manifest_invalid_json", self.codes())

        make_valid_conversion(self.base / "other" / "商业管理" / "系统思考")
        self.root = self.base / "other" / "商业管理" / "系统思考"
        (self.root / "系统思考-格式化.md").unlink()
        self.assertIn("missing_formatted_markdown", self.codes())

    def test_gate_requires_content_list_and_nonempty_page_records(self):
        content_path = self.root / "mineru" / "book_content_list_v2.json"
        content_path.write_text('{"pages": []}\n', encoding="utf-8")
        content_record = file_record(content_path, self.root)
        content_record.update(
            {"source_path": "book_content_list_v2.json", "kind": "content_list"}
        )
        self.manifest["resources"]["mineru_json"] = [content_record]
        self.manifest["stages"]["imported"]["outputs"][1] = content_record
        self.manifest["pages"]["records"] = []
        self.manifest["pages"]["mineru_count"] = 0
        self.rewrite_manifest()
        self.assertIn("page_records_empty", self.codes())

    def test_gate_rejects_forged_stored_count_against_current_two_page_pdf(self):
        self.replace_source_pdf_with_page_count(2)
        self.rewrite_manifest()

        report = self.module.validate_conversion(self.root)

        self.assertIn(
            "page_count_mismatch",
            {issue.code for issue in report.issues},
            report.issues,
        )

    def test_gate_accepts_stored_count_matching_current_two_page_pdf(self):
        self.replace_source_pdf_with_page_count(2)
        content_path = self.root / "mineru" / "book_content_list_v2.json"
        content_path.write_text(
            json.dumps(
                {
                    "pages": [
                        {"page_idx": 0, "type": "text"},
                        {"page_idx": 1, "type": "text"},
                    ]
                }
            )
            + "\n",
            encoding="utf-8",
        )
        content_record = {
            **file_record(content_path, self.root),
            "source_path": "book_content_list_v2.json",
            "kind": "content_list",
        }
        self.manifest["resources"]["mineru_json"] = [content_record]
        self.manifest["stages"]["imported"]["outputs"][1] = content_record
        self.manifest["pages"] = {
            "source_count": 2,
            "mineru_count": 2,
            "reconciliation": "matched",
            "records": [
                {"page_index": 0, "record_count": 1},
                {"page_index": 1, "record_count": 1},
            ],
        }
        self.rewrite_manifest()

        report = self.module.validate_conversion(self.root)

        self.assertEqual(0, report.blocking_count, report.issues)

    def test_gate_requires_explicit_unavailable_state_when_current_count_unavailable(self):
        with mock.patch.object(
            self.module, "_pdf_page_count", return_value=None
        ) as page_count:
            report = self.module.validate_conversion(self.root)

        page_count.assert_called_once_with(self.pdf.resolve())
        self.assertIn(
            "page_count_mismatch",
            {issue.code for issue in report.issues},
            report.issues,
        )

    def test_gate_accepts_explicit_unavailable_state_when_current_count_unavailable(self):
        self.manifest["pages"]["source_count"] = None
        self.manifest["pages"]["reconciliation"] = "source_count_unavailable"
        self.manifest["warnings"] = [
            {
                "code": "source_page_count_unavailable",
                "classification": "accepted",
                "message": "Structural page count is unavailable.",
            }
        ]
        self.rewrite_manifest()

        with mock.patch.object(
            self.module, "_pdf_page_count", return_value=None
        ) as page_count:
            report = self.module.validate_conversion(self.root)

        page_count.assert_called_once_with(self.pdf.resolve())
        self.assertEqual(0, report.blocking_count, report.issues)

    def test_gate_requires_complete_stage_outputs_and_current_hashes(self):
        self.manifest["stages"]["formatted"]["outputs"] = []
        self.rewrite_manifest()
        self.assertIn("stage_output_missing", self.codes())

        self.manifest = json.loads(
            (self.root / "conversion-manifest.json").read_text(encoding="utf-8")
        )
        self.manifest["stages"]["formatted"]["outputs"] = [
            self.manifest["artifacts"]["formatted_markdown"],
            self.manifest["artifacts"]["normalization_log"],
        ]
        (self.root / "系统思考-格式化.md").write_text("tampered\n", encoding="utf-8")
        self.rewrite_manifest()
        self.assertIn("artifact_hash_mismatch", self.codes())

    def test_gate_requires_canonical_distinct_artifact_and_stage_identities(self):
        raw = self.root / "系统思考.md"
        formatted = self.root / "系统思考-格式化.md"
        raw.unlink()
        formatted_record = file_record(formatted, self.root)
        self.manifest["artifacts"]["raw_markdown"] = formatted_record
        self.manifest["stages"]["imported"]["outputs"][0] = formatted_record
        self.rewrite_manifest()
        self.assertIn("artifact_identity_invalid", self.codes())

    def test_gate_recomputes_formatted_artifact_and_normalization_audit(self):
        formatted = self.root / "系统思考-格式化.md"
        formatted.write_text("# 改写内容\n", encoding="utf-8")
        formatted_record = file_record(formatted, self.root)
        self.manifest["artifacts"]["formatted_markdown"] = formatted_record
        self.manifest["stages"]["formatted"]["outputs"][0] = formatted_record
        self.rewrite_manifest()
        self.assertIn("formatted_derivation_mismatch", self.codes())

        _, self.manifest = make_valid_conversion(
            self.base / "normalization-case" / "商业管理" / "系统思考"
        )
        self.root = self.base / "normalization-case" / "商业管理" / "系统思考"
        normalization = self.root / "normalization-log.json"
        normalization.write_text('[{"type": "invented"}]\n', encoding="utf-8")
        normalization_record = file_record(normalization, self.root)
        self.manifest["artifacts"]["normalization_log"] = normalization_record
        self.manifest["stages"]["formatted"]["outputs"][1] = normalization_record
        self.rewrite_manifest()
        self.assertIn("normalization_audit_mismatch", self.codes())

    def test_gate_rejects_undeclared_split_and_resource_files(self):
        injected_chapter = self.root / "拆分" / "章节" / "99-注入.md"
        injected_chapter.write_text("# 第九十九章 注入\n", encoding="utf-8")
        injected_resource = self.root / "images" / "stale.png"
        injected_resource.parent.mkdir()
        injected_resource.write_bytes(b"stale")
        codes = self.codes()
        self.assertIn("undeclared_split_output", codes)
        self.assertIn("undeclared_resource", codes)

    def test_gate_rejects_unresolved_reference_style_images(self):
        other = self.base / "unresolved-case" / "商业管理" / "系统思考"
        make_valid_conversion(
            other,
            formatted_text=(
                "# 第一章 系统\n\n"
                "![完整][missing-full]\n"
                "![折叠][]\n"
                "![快捷]\n"
            ),
        )
        report = self.module.validate_conversion(other)
        unresolved = [
            issue for issue in report.issues
            if issue.code == "unresolved_image_reference"
        ]
        self.assertGreaterEqual(len(unresolved), 3, report.issues)
        self.assertEqual(
            {"missing-full", "折叠", "快捷"},
            {issue.message.rsplit(": ", 1)[-1] for issue in unresolved},
        )

    def test_gate_rejects_malformed_content_list_page_entries(self):
        content_path = self.root / "mineru" / "book_content_list_v2.json"
        content_path.write_text('{"pages": [null]}\n', encoding="utf-8")
        content_record = file_record(content_path, self.root)
        content_record.update(
            {"source_path": "book_content_list_v2.json", "kind": "content_list"}
        )
        self.manifest["resources"]["mineru_json"] = [content_record]
        self.manifest["stages"]["imported"]["outputs"][1] = content_record
        self.manifest["pages"]["records"] = [
            {"page_index": 0, "record_count": 1}
        ]
        self.rewrite_manifest()
        self.assertIn("content_list_invalid", self.codes())

    def test_gate_requires_nonempty_exact_engine_run_provenance(self):
        self.manifest["engine"].update(
            {
                "version": "",
                "backend": "",
                "language": "",
                "executable": "",
                "command": [],
            }
        )
        self.rewrite_manifest()
        self.assertIn("engine_provenance_invalid", self.codes())

        self.root = self.base / "command-case" / "商业管理" / "系统思考"
        _, self.manifest = make_valid_conversion(self.root)
        self.manifest["engine"]["command"][2] = str(
            (self.base / "wrong.pdf").resolve()
        )
        self.rewrite_manifest()
        self.assertIn("engine_command_mismatch", self.codes())

    def test_gate_checks_all_markdown_image_reference_forms(self):
        text = (
            "# 第一章 系统\n\n"
            "![inline](images/missing-inline.png)\n"
            "![full][full-ref]\n"
            "![collapsed][]\n"
            "![shortcut]\n\n"
            "[full-ref]: images/missing-full.png\n"
            "[collapsed]: images/missing-collapsed.png\n"
            "[shortcut]: images/missing-shortcut.png\n"
        )
        other = self.base / "images-case" / "商业管理" / "系统思考"
        make_valid_conversion(other, formatted_text=text)
        report = self.module.validate_conversion(other)
        missing = [issue for issue in report.issues if issue.code == "missing_image"]
        self.assertEqual(
            {
                "missing-inline.png",
                "missing-full.png",
                "missing-collapsed.png",
                "missing-shortcut.png",
            },
            {issue.path.name for issue in missing},
            report.issues,
        )

    def test_void_html_tag_does_not_hide_later_missing_markdown_image(self):
        other = self.base / "void-image-case" / "商业管理" / "系统思考"
        make_valid_conversion(
            other,
            formatted_text=(
                "<hr>\n\n"
                "![missing](images/missing-after-hr.png)\n"
            ),
        )

        report = self.module.validate_conversion(other)

        missing = [issue for issue in report.issues if issue.code == "missing_image"]
        self.assertEqual(
            {"missing-after-hr.png"},
            {issue.path.name for issue in missing},
            report.issues,
        )

    def test_gate_rejects_resource_escape_and_symlink_escape(self):
        outside = self.base / "outside.json"
        outside.write_text("{}\n", encoding="utf-8")
        escaping = {
            "path": "../../../outside.json",
            "sha256": hashlib.sha256(outside.read_bytes()).hexdigest(),
            "size": outside.stat().st_size,
            "source_path": "outside.json",
            "kind": "mineru_json",
        }
        self.manifest["resources"]["mineru_json"].append(escaping)
        self.rewrite_manifest()
        self.assertIn("resource_path_escape", self.codes())

        self.manifest["resources"]["mineru_json"].pop()
        link = self.root / "mineru" / "escaped.json"
        link.symlink_to(outside)
        symlinked = {
            "path": "mineru/escaped.json",
            "sha256": hashlib.sha256(outside.read_bytes()).hexdigest(),
            "size": outside.stat().st_size,
            "source_path": "escaped.json",
            "kind": "mineru_json",
        }
        self.manifest["resources"]["mineru_json"].append(symlinked)
        self.rewrite_manifest()
        self.assertIn("resource_path_escape", self.codes())

    def test_gate_proves_split_span_coverage(self):
        split_index = self.root / "拆分" / "split-index.json"
        payload = json.loads(split_index.read_text(encoding="utf-8"))
        payload["units"][0]["start"] = 1
        split_index.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")
        split_record = file_record(split_index, self.root)
        self.manifest["artifacts"]["split_index"] = split_record
        self.manifest["stages"]["split"]["outputs"][0] = split_record
        self.rewrite_manifest()
        self.assertIn("split_coverage_gap", self.codes())

    def test_gate_rejects_complete_split_units_reordered_in_manifest(self):
        self.forge_reordered_two_unit_split()

        report = self.module.validate_conversion(self.root)

        self.assertIn(
            "split_coverage_gap",
            {issue.code for issue in report.issues},
            report.issues,
        )

    def test_package_initialization_refuses_reordered_split_units(self):
        self.forge_reordered_two_unit_split()
        books_root = self.base / "books"

        with self.assertRaises(self.module.IngestionError):
            self.module.initialize_book_package(self.root, books_root)

        self.assertFalse((books_root / "系统思考").exists())

    def test_gate_binds_each_split_file_to_its_formatted_source_span(self):
        chapter = self.root / "拆分" / "章节" / "01-第一章 系统.md"
        chapter.write_text("# 注入内容\n", encoding="utf-8")
        split_index = self.root / "拆分" / "split-index.json"
        payload = json.loads(split_index.read_text(encoding="utf-8"))
        payload["units"][0].update(file_record(chapter, self.root))
        split_index.write_text(
            json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        split_record = file_record(split_index, self.root)
        chapter_record = file_record(chapter, self.root)
        self.manifest["artifacts"]["split_index"] = split_record
        self.manifest["stages"]["split"]["outputs"] = [
            split_record,
            chapter_record,
        ]
        self.rewrite_manifest()
        self.assertIn("split_output_mismatch", self.codes())

    def test_gate_reports_malformed_split_span_types_without_crashing(self):
        split_index = self.root / "拆分" / "split-index.json"
        payload = json.loads(split_index.read_text(encoding="utf-8"))
        payload["units"][0]["start"] = None
        payload["exclusions"] = [
            {
                "start": 0,
                "end": 0,
                "classification": "accepted",
                "reason": "empty classified prefix",
            }
        ]
        split_index.write_text(
            json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        split_record = file_record(split_index, self.root)
        self.manifest["artifacts"]["split_index"] = split_record
        self.manifest["stages"]["split"]["outputs"][0] = split_record
        self.rewrite_manifest()
        self.assertIn("split_coverage_gap", self.codes())

    def test_gate_requires_classified_nonblocking_warnings_and_recorded_pass(self):
        self.manifest["warnings"] = [{"code": "ocr_review", "message": "review"}]
        self.rewrite_manifest()
        self.assertIn("warning_unclassified", self.codes())

        self.manifest["warnings"] = []
        self.manifest["validation"]["status"] = "pending"
        self.rewrite_manifest()
        self.assertIn("validation_not_passed", self.codes())
        structural = self.module.validate_conversion(
            self.root, require_recorded_gate=False
        )
        self.assertEqual(0, structural.blocking_count, structural.issues)


class MarkdownStateAndFormattingTests(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tempdir.name)
        self.module = load_ingestion()

    def tearDown(self):
        self._tempdir.cleanup()

    def test_split_preserves_prefix_and_ignores_headings_in_protected_blocks(self):
        formatted = (
            "---\n"
            "title: 第九章 元数据不是章节\n"
            "---\n"
            "# 前言\n\n前置正文。\n\n"
            "```markdown\n# 第八章 代码示例\n```\n\n"
            "<!--\n# 第七章 注释示例\n-->\n\n"
            "<div>\n# 第六章 HTML 示例\n</div>\n\n"
            "# 第一章 真正章节\n\n第一章正文。\n\n"
            "# 第二章 后续章节\n\n第二章正文。\n"
        )
        paths = self.module.split_chapters(formatted, self.root, "系统思考")
        self.assertEqual(2, len(paths))
        first = paths[0].read_text(encoding="utf-8")
        self.assertTrue(first.startswith("---\ntitle:"), first)
        self.assertIn("前置正文。", first)
        self.assertIn("# 第八章 代码示例", first)
        self.assertIn("# 第七章 注释示例", first)
        self.assertIn("# 第六章 HTML 示例", first)
        self.assertIn("# 第一章 真正章节", first)
        split_index = json.loads(
            (self.root / "拆分" / "split-index.json").read_text(encoding="utf-8")
        )
        self.assertEqual(0, split_index["units"][0]["start"])
        self.assertEqual(len(formatted), split_index["units"][-1]["end"])

    def test_split_ignores_chapter_headings_inside_details_html_block(self):
        formatted = (
            "<details>\n"
            "<summary>示例</summary>\n"
            "# 第九章 HTML 示例\n"
            "</details>\n\n"
            "# 第一章 真正章节\n\n第一章正文。\n\n"
            "# 第二章 后续章节\n\n第二章正文。\n"
        )
        paths = self.module.split_chapters(formatted, self.root, "系统思考")
        self.assertEqual(2, len(paths))
        self.assertIn("# 第九章 HTML 示例", paths[0].read_text(encoding="utf-8"))

    def test_void_html_tag_does_not_hide_later_chapter_headings(self):
        formatted = (
            "<hr>\n\n"
            "# 第一章 真正章节\n\n第一章正文。\n\n"
            "# 第二章 后续章节\n\n第二章正文。\n"
        )

        paths = self.module.split_chapters(formatted, self.root, "系统思考")

        self.assertEqual(2, len(paths))
        self.assertIn("第一章正文。", paths[0].read_text(encoding="utf-8"))
        self.assertIn("第二章正文。", paths[1].read_text(encoding="utf-8"))

    def test_void_html_tag_does_not_hide_later_paragraph_locator(self):
        markdown = "<hr>\n\n后续正文。\n"

        rendered = self.module.add_stable_paragraph_ids(markdown, "ch01")

        self.assertIn("<!-- locator: ch01-p001 -->\n后续正文。", rendered)

    def test_formatting_preserves_ambiguous_hyphens_and_protected_blocks(self):
        raw = (
            "---\nfooter: Page 1\n---\n"
            "<!-- page: 1 -->\n"
            "hyphen-\nated remains ambiguous.\n\n"
            "```text\n<!-- page: 2 -->\nPage 2\nword-\nwrap\n```\n\n"
            "Page 1\n"
        )
        formatted, changes = self.module.format_markdown(raw)
        self.assertIn("hyphen-\nated", formatted)
        self.assertIn("footer: Page 1", formatted)
        self.assertIn("<!-- page: 2 -->\nPage 2\nword-\nwrap", formatted)
        self.assertNotIn("\nPage 1\n", formatted.split("```", 2)[-1])
        self.assertTrue(changes)

    def test_image_rewrites_preserve_front_matter_code_and_html_literals(self):
        markdown = (
            "---\ncover: ![meta](images/figure.png)\n---\n"
            "```markdown\n![code](images/figure.png)\n```\n"
            "<details>\n![html](images/figure.png)\n</details>\n\n"
            "![body](images/figure.png)\n"
            "![body-ref][figure-ref]\n"
            "[figure-ref]: images/figure.png\n"
        )
        rewritten = self.module._rewrite_image_paths(
            markdown, {"images/figure.png": "images/renamed.png"}
        )
        self.assertIn("cover: ![meta](images/figure.png)", rewritten)
        self.assertIn("![code](images/figure.png)", rewritten)
        self.assertIn("![html](images/figure.png)", rewritten)
        self.assertIn("![body](images/renamed.png)", rewritten)
        self.assertIn("[figure-ref]: images/renamed.png", rewritten)

        image = self.root / "images" / "figure.png"
        image.parent.mkdir()
        image.write_bytes(b"figure")
        chapter_source = self.root / "source.md"
        package_chapter = self.root / "package" / "chapters" / "ch01"
        copied = self.module.copy_chapter_assets(
            markdown, self.root, package_chapter, chapter_source
        )
        self.assertIn("![code](images/figure.png)", copied)
        self.assertIn("![html](images/figure.png)", copied)
        self.assertIn("![body](assets/figure.png)", copied)


class AtomicPublicationAndReuseTests(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        self.base = Path(self._tempdir.name)
        self.module = load_ingestion()
        self.auto = self.base / "auto"
        (self.auto / "images").mkdir(parents=True)
        (self.auto / "book.md").write_text(
            "# 第一章 系统\n\n正文。\n", encoding="utf-8"
        )
        (self.auto / "book_content_list_v2.json").write_text(
            json.dumps({"pages": [{"page_idx": 0, "type": "text"}]}) + "\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self._tempdir.cleanup()

    def config(self, payload: bytes, *, title: str = "系统思考"):
        pdf = self.base / (hashlib.sha256(payload).hexdigest()[:8] + ".pdf")
        pdf.write_bytes(payload)
        return self.module.IngestionConfig(
            pdf=pdf,
            category="商业管理",
            title=title,
            markdown_root=self.base / "markdown",
            books_root=self.base / "books",
            work_root=self.base,
        )

    def test_different_pdf_requires_explicit_replace_and_replacement_has_no_stale_files(self):
        first = self.config(b"%PDF first /Type /Page")
        result = self.module.import_mineru_output(first, self.auto, "1.0")
        stale = result.manifest_path.parent / "images" / "stale.png"
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.write_bytes(b"stale")

        second = self.config(b"%PDF second /Type /Page")
        with self.assertRaises(self.module.IngestionError):
            self.module.import_mineru_output(second, self.auto, "1.0")
        self.assertTrue(stale.is_file())

        replaced = self.module.import_mineru_output(
            second, self.auto, "1.0", conflict_policy="replace"
        )
        self.assertFalse((replaced.manifest_path.parent / "images" / "stale.png").exists())
        self.assertEqual(
            self.module.sha256_file(second.pdf), replaced.manifest["source"]["sha256"]
        )

    def test_valid_matching_conversion_is_reused_without_rewrite(self):
        config = self.config(b"%PDF same /Type /Page")
        first = self.module.import_mineru_output(config, self.auto, "1.0")
        before = first.manifest_path.stat().st_mtime_ns
        second = self.module.import_mineru_output(config, self.auto, "1.0")
        self.assertTrue(second.reused)
        self.assertEqual(before, second.manifest_path.stat().st_mtime_ns)

    def test_replacement_invokes_one_exchange_and_never_renames_target_away(self):
        parent = self.base / "publish"
        parent.mkdir()
        target = parent / "book"
        target.mkdir()
        (target / "old.txt").write_text("old\n", encoding="utf-8")
        staging = parent / ".book.staging"
        staging.mkdir()
        (staging / "new.txt").write_text("new\n", encoding="utf-8")

        def exchange_contents(source, destination):
            old = (Path(destination) / "old.txt").read_text(encoding="utf-8")
            new = (Path(source) / "new.txt").read_text(encoding="utf-8")
            (Path(destination) / "old.txt").unlink()
            (Path(source) / "new.txt").unlink()
            (Path(destination) / "new.txt").write_text(new, encoding="utf-8")
            (Path(source) / "old.txt").write_text(old, encoding="utf-8")

        with mock.patch.object(
            self.module,
            "_atomic_exchange_directories",
            side_effect=exchange_contents,
            create=True,
        ) as exchange, mock.patch.object(
            self.module.os, "replace", wraps=os.replace
        ) as replace:
            self.module.atomic_publish_directory(staging, target)

        exchange.assert_called_once_with(staging, target)
        replace.assert_not_called()
        self.assertEqual("new\n", (target / "new.txt").read_text(encoding="utf-8"))
        self.assertFalse((target / "old.txt").exists())
        self.assertFalse(staging.exists())

    def test_unsupported_atomic_exchange_fails_without_changing_either_directory(self):
        parent = self.base / "unsupported-publish"
        parent.mkdir()
        target = parent / "book"
        target.mkdir()
        (target / "old.txt").write_text("old\n", encoding="utf-8")
        staging = parent / ".book.staging"
        staging.mkdir()
        (staging / "new.txt").write_text("new\n", encoding="utf-8")

        with mock.patch.object(
            self.module,
            "_atomic_exchange_directories",
            side_effect=self.module.IngestionError("atomic exchange unsupported"),
            create=True,
        ) as exchange, mock.patch.object(
            self.module.os, "replace", wraps=os.replace
        ) as replace:
            with self.assertRaises(self.module.IngestionError):
                self.module.atomic_publish_directory(staging, target)

        exchange.assert_called_once_with(staging, target)
        replace.assert_not_called()
        self.assertEqual("old\n", (target / "old.txt").read_text(encoding="utf-8"))
        self.assertFalse((target / "new.txt").exists())
        self.assertEqual("new\n", (staging / "new.txt").read_text(encoding="utf-8"))
        self.assertFalse((staging / "old.txt").exists())

    def test_cleanup_failure_reports_published_target_without_removing_it(self):
        parent = self.base / "cleanup-publish"
        parent.mkdir()
        target = parent / "book"
        target.mkdir()
        (target / "old.txt").write_text("old\n", encoding="utf-8")
        staging = parent / ".book.staging"
        staging.mkdir()
        (staging / "new.txt").write_text("new\n", encoding="utf-8")

        def exchange_contents(source, destination):
            old = (Path(destination) / "old.txt").read_text(encoding="utf-8")
            new = (Path(source) / "new.txt").read_text(encoding="utf-8")
            (Path(destination) / "old.txt").unlink()
            (Path(source) / "new.txt").unlink()
            (Path(destination) / "new.txt").write_text(new, encoding="utf-8")
            (Path(source) / "old.txt").write_text(old, encoding="utf-8")

        with mock.patch.object(
            self.module,
            "_atomic_exchange_directories",
            side_effect=exchange_contents,
            create=True,
        ) as exchange, mock.patch.object(
            self.module.shutil, "rmtree", side_effect=OSError("cleanup blocked")
        ):
            with self.assertRaisesRegex(
                self.module.IngestionError, "published.*cleanup"
            ):
                self.module.atomic_publish_directory(staging, target)

        exchange.assert_called_once_with(staging, target)
        self.assertEqual("new\n", (target / "new.txt").read_text(encoding="utf-8"))
        self.assertFalse((target / "old.txt").exists())
        self.assertEqual("old\n", (staging / "old.txt").read_text(encoding="utf-8"))

    @unittest.skipUnless(sys.platform == "darwin", "requires macOS renamex_np")
    def test_real_macos_directory_exchange_swaps_sibling_directories(self):
        parent = self.base / "real-exchange"
        parent.mkdir()
        target = parent / "book"
        target.mkdir()
        (target / "old.txt").write_text("old\n", encoding="utf-8")
        staging = parent / ".book.staging"
        staging.mkdir()
        (staging / "new.txt").write_text("new\n", encoding="utf-8")
        exchange = getattr(self.module, "_atomic_exchange_directories", None)
        self.assertTrue(callable(exchange), "atomic exchange helper is missing")

        exchange(staging, target)

        self.assertEqual("new\n", (target / "new.txt").read_text(encoding="utf-8"))
        self.assertEqual("old\n", (staging / "old.txt").read_text(encoding="utf-8"))

    def test_failed_formatted_write_keeps_previous_conversion_generation(self):
        first = self.config(b"%PDF original /Type /Page")
        original = self.module.import_mineru_output(first, self.auto, "1.0")
        original_hash = original.manifest["source"]["sha256"]
        second = self.config(b"%PDF replacement /Type /Page")
        real_atomic_write = self.module.atomic_write_text

        def fail_formatted(path, text):
            if Path(path).name.endswith("-格式化.md"):
                raise OSError("injected formatted write failure")
            return real_atomic_write(path, text)

        with mock.patch.object(
            self.module, "atomic_write_text", side_effect=fail_formatted
        ):
            with self.assertRaises(self.module.IngestionError):
                self.module.import_mineru_output(
                    second, self.auto, "1.0", conflict_policy="replace"
                )
        persisted = json.loads(original.manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(original_hash, persisted["source"]["sha256"])

    def test_symlinked_destination_component_is_rejected(self):
        outside = self.base / "outside"
        outside.mkdir()
        markdown_root = self.base / "markdown"
        markdown_root.mkdir()
        (markdown_root / "商业管理").symlink_to(outside, target_is_directory=True)
        config = self.config(b"%PDF symlink /Type /Page")
        with self.assertRaises(self.module.IngestionError):
            self.module.import_mineru_output(config, self.auto, "1.0")
        self.assertEqual([], list(outside.iterdir()))

    def test_formatted_artifact_and_normalization_log_are_manifested(self):
        config = self.config(b"%PDF formatted /Type /Page")
        result = self.module.import_mineru_output(config, self.auto, "1.0")
        artifacts = result.manifest["artifacts"]
        formatted = result.manifest_path.parent / artifacts["formatted_markdown"]["path"]
        log = result.manifest_path.parent / artifacts["normalization_log"]["path"]
        self.assertTrue(formatted.is_file())
        self.assertTrue(log.is_file())
        self.assertEqual(self.module.sha256_file(formatted), artifacts["formatted_markdown"]["sha256"])
        self.assertEqual(self.module.sha256_file(log), artifacts["normalization_log"]["sha256"])

    def test_package_fallback_uses_formatted_not_raw_markdown(self):
        (self.auto / "book.md").write_text(
            "<!-- page: 1 -->\n正文。\n\nPage 1\n", encoding="utf-8"
        )
        config = self.config(b"%PDF fallback /Type /Page")
        result = self.module.import_mineru_output(config, self.auto, "1.0")
        package = self.module.initialize_book_package(
            result.manifest_path.parent, config.books_root
        )
        source = (package / "chapters" / "ch01" / "source.md").read_text(encoding="utf-8")
        self.assertIn("正文。", source)
        self.assertNotIn("Page 1", source)

    def test_existing_package_reuse_requires_all_artifacts_and_provenance(self):
        config = self.config(b"%PDF package /Type /Page")
        result = self.module.import_mineru_output(config, self.auto, "1.0")
        package = self.module.initialize_book_package(
            result.manifest_path.parent, config.books_root
        )
        (package / "chapters" / "ch01" / "reading.md").unlink()
        with self.assertRaises(self.module.IngestionError):
            self.module.initialize_book_package(
                result.manifest_path.parent, config.books_root
            )

    def test_existing_package_reuse_revalidates_linked_asset_existence_and_hash(self):
        (self.auto / "images" / "figure.png").write_bytes(b"original")
        (self.auto / "book.md").write_text(
            "# 第一章 系统\n\n![图](images/figure.png)\n", encoding="utf-8"
        )
        config = self.config(b"%PDF package-assets /Type /Page")
        result = self.module.import_mineru_output(config, self.auto, "1.0")
        package = self.module.initialize_book_package(
            result.manifest_path.parent, config.books_root
        )
        asset = package / "chapters" / "ch01" / "assets" / "figure.png"
        asset.unlink()
        with self.assertRaises(self.module.IngestionError):
            self.module.initialize_book_package(
                result.manifest_path.parent, config.books_root
            )

        asset.write_bytes(b"tampered")
        with self.assertRaises(self.module.IngestionError):
            self.module.initialize_book_package(
                result.manifest_path.parent, config.books_root
            )

    def test_existing_package_reuse_cannot_hide_missing_image_after_void_html(self):
        config = self.config(b"%PDF package-void-html /Type /Page")
        result = self.module.import_mineru_output(config, self.auto, "1.0")
        package = self.module.initialize_book_package(
            result.manifest_path.parent, config.books_root
        )
        source = package / "chapters" / "ch01" / "source.md"
        source.write_text(
            source.read_text(encoding="utf-8")
            + "\n<hr>\n\n![missing](assets/missing-after-hr.png)\n",
            encoding="utf-8",
        )
        provenance_path = package / "ingestion-provenance.json"
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        provenance["source_units"][0]["package_source_sha256"] = (
            self.module.sha256_file(source)
        )
        provenance_path.write_text(
            json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        with self.assertRaises(self.module.IngestionError):
            self.module.initialize_book_package(
                result.manifest_path.parent, config.books_root
            )


class MinerUExecutionContractTests(unittest.TestCase):
    def setUp(self):
        self._tempdir = tempfile.TemporaryDirectory()
        self.base = Path(self._tempdir.name)
        self.module = load_ingestion()

    def tearDown(self):
        self._tempdir.cleanup()

    def fake_mineru(self, *, complete: bool = True, mutate_pdf: bool = False) -> Path:
        binary = self.base / ("mineru-complete" if complete else "mineru-incomplete")
        content = [
            "#!/bin/sh",
            'if [ "$1" = "--version" ]; then echo "MinerU 9.9"; exit 0; fi',
            'pdf=""',
            'out=""',
            'while [ "$#" -gt 0 ]; do',
            '  case "$1" in',
            '    -p) pdf="$2"; shift 2 ;;',
            '    -o) out="$2"; shift 2 ;;',
            '    *) shift ;;',
            '  esac',
            'done',
            'mkdir -p "$out/job/auto"',
            "printf '# 第一章 系统\\n\\n正文。\\n' > \"$out/job/auto/book.md\"",
        ]
        if complete:
            content.append(
                "printf '{\"pages\":[{\"page_idx\":0,\"type\":\"text\"}]}\\n' > \"$out/job/auto/book_content_list_v2.json\""
            )
        if mutate_pdf:
            content.append("printf 'changed' >> \"$pdf\"")
        content.append("exit 0")
        binary.write_text("\n".join(content) + "\n", encoding="utf-8")
        binary.chmod(0o755)
        return binary

    def config(self, binary: Path):
        pdf = self.base / "book.pdf"
        pdf.write_bytes(b"%PDF fake /Type /Page")
        return self.module.IngestionConfig(
            pdf=pdf,
            category="技术",
            title="Fake Book",
            mineru_bin=binary,
            work_root=self.base,
            timeout=10,
        )

    def test_run_mineru_uses_safe_subprocess_options_and_validates_success(self):
        config = self.config(self.fake_mineru())
        real_run = subprocess.run
        with mock.patch.object(self.module.subprocess, "run", wraps=real_run) as run:
            result = self.module.run_mineru(config, self.base / "stage")
        self.assertTrue(result.auto_dir.is_dir())
        self.assertEqual(config.backend, result.command[result.command.index("-b") + 1])
        self.assertEqual(config.language, result.command[result.command.index("-l") + 1])
        self.assertEqual(2, run.call_count)
        for call in run.call_args_list:
            self.assertFalse(call.kwargs["shell"])
            self.assertTrue(call.kwargs["capture_output"])
            self.assertTrue(call.kwargs["text"])
            self.assertFalse(call.kwargs["check"])

    def test_run_mineru_rejects_zero_exit_with_incomplete_output(self):
        config = self.config(self.fake_mineru(complete=False))
        with self.assertRaises(self.module.IngestionError):
            self.module.run_mineru(config, self.base / "stage")

    def test_run_mineru_rejects_pdf_fingerprint_change(self):
        config = self.config(self.fake_mineru(mutate_pdf=True))
        with self.assertRaisesRegex(self.module.IngestionError, "changed during MinerU"):
            self.module.run_mineru(config, self.base / "stage")


if __name__ == "__main__":
    unittest.main()
