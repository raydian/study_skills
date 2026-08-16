import importlib.util
import hashlib
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_book_package.py"
HARDENING_TEST_PATH = ROOT / "tests" / "test_pdf_ingestion_hardening.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_book_package", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("validator module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_hardening_helpers():
    spec = importlib.util.spec_from_file_location(
        "pdf_ingestion_hardening_helpers", HARDENING_TEST_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("hardening test helpers cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateBookPackageTests(unittest.TestCase):
    def make_package(self, root: Path, *, traceable: bool = True) -> Path:
        package = root / "books" / "example-book"
        chapter = package / "chapters" / "ch01"
        synthesis = package / "synthesis"
        chapter.mkdir(parents=True)
        synthesis.mkdir(parents=True)

        (package / "BOOK.md").write_text("# Example book\n", encoding="utf-8")

        (package / "manifest.yaml").write_text(
            "schema_version: 1\nbook_id: example-book\nsource:\n  format: markdown\n"
            "  source_state: sealed\n  source_sha256: " + "a" * 64 + "\n",
            encoding="utf-8",
        )
        (package / "reading-ledger.yaml").write_text(
            "passes:\n  pass_0: complete\n  pass_1: complete\n"
            "  pass_2: complete\n  pass_3: complete\n  pass_4: complete\n  pass_5: complete\n"
            "coverage:\n  chapters: {reviewed: 1, total: 1}\n"
            "  sections: {reviewed: 1, total: 1}\n"
            "  pages: {reviewed: 1, total: 1}\n"
            "  paragraphs: {reviewed: 1, total: 1}\n"
            "  figures: {reviewed: 1, total: 1}\n"
            "  tables: {reviewed: 0, total: 0}\n"
            "  equations: {reviewed: 0, total: 0}\n"
            "  code_blocks: {reviewed: 0, total: 0}\n"
            "  footnotes: {reviewed: 0, total: 0}\n"
            "  sidebars: {reviewed: 0, total: 0}\n"
            "  appendices: {reviewed: 0, total: 0}\n",
            encoding="utf-8",
        )
        (package / "evidence-ledger.yaml").write_text(
            "evidence:\n  - id: ev-001\n    source_refs: [ch01-p001]\n",
            encoding="utf-8",
        )
        (chapter / "source.md").write_text(
            '<!-- source-state: sealed -->\n<!-- page: 001 -->\n<p id="ch01-p001">Original.</p>\n'
            '<figure id="ch01-fig001">Figure caption.</figure>\n',
            encoding="utf-8",
        )
        source_ref = "[source: ch01-p001; page: 001]" if traceable else ""
        (chapter / "reading.md").write_text(
            f"# Main reading\n\n<span id=\"r-ch01-001\">A material point.</span> {source_ref}\n",
            encoding="utf-8",
        )
        (chapter / "annotated.md").write_text(
            "> Original.\n\n> [!AI-EXPLANATION]\n> Explanation.\n",
            encoding="utf-8",
        )
        (chapter / "annotations.yaml").write_text(
            "annotations:\n  - id: ann-001\n    attribution: ai_explanation\n"
            "    source_refs: [ch01-p001]\n    revision: 1\n",
            encoding="utf-8",
        )
        (chapter / "knowledge.yaml").write_text(
            "knowledge_units:\n  - id: ku-001\n    type: Concept\n"
            "    attribution: author_claim\n    source_refs: [ch01-p001]\n",
            encoding="utf-8",
        )
        for name in (
            "book-map.md",
            "core-thesis.md",
            "concept-evolution.md",
            "argument-map.md",
            "critical-reading.md",
            "full-book-reading.md",
        ):
            (synthesis / name).write_text("# Complete\n", encoding="utf-8")
        return package

    def make_pdf_package(
        self,
        root: Path,
        *,
        gate_status: str = "passed",
        conversion_status: str = "passed",
        conversion_hash: str | None = None,
        include_conversion_manifest: bool = True,
    ) -> Path:
        package = self.make_package(root)
        helpers = load_hardening_helpers()
        conversion_dir = root / "markdown" / "商业管理" / "系统思考"
        _, conversion = helpers.make_valid_conversion(conversion_dir)
        conversion_manifest = conversion_dir / "conversion-manifest.json"
        source_hash = conversion["source"]["sha256"]
        if conversion_hash is not None:
            conversion["source"]["sha256"] = conversion_hash
        conversion["validation"]["status"] = conversion_status
        conversion_manifest.write_text(
            json.dumps(conversion, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if not include_conversion_manifest:
            conversion_manifest.unlink()
        manifest = package / "manifest.yaml"
        manifest.write_text(
            manifest.read_text(encoding="utf-8")
            .replace("format: markdown", "format: pdf")
            .replace("a" * 64, source_hash)
            + "ingestion:\n"
            + f"  conversion_dir: {conversion_dir}\n"
            + f"  conversion_manifest: {conversion_manifest}\n"
            + f"  source_pdf_sha256: {source_hash}\n"
            + f"  gate_status: {gate_status}\n",
            encoding="utf-8",
        )
        conversion_source = conversion_dir / "拆分" / "章节" / "01-第一章 系统.md"
        package_source = package / "chapters" / "ch01" / "source.md"
        (package / "ingestion-provenance.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "source_pdf_sha256": source_hash,
                    "conversion_dir": str(conversion_dir),
                    "conversion_manifest": str(conversion_manifest),
                    "conversion_manifest_sha256": hashlib.sha256(
                        conversion_manifest.read_bytes()
                    ).hexdigest()
                    if conversion_manifest.is_file()
                    else "0" * 64,
                    "created_at": "2026-08-15T00:00:00Z",
                    "source_units": [
                        {
                            "chapter_id": "ch01",
                            "conversion_path": conversion_source.relative_to(
                                conversion_dir
                            ).as_posix(),
                            "conversion_sha256": hashlib.sha256(
                                conversion_source.read_bytes()
                            ).hexdigest(),
                            "package_source": package_source.relative_to(
                                package
                            ).as_posix(),
                            "package_source_sha256": hashlib.sha256(
                                package_source.read_bytes()
                            ).hexdigest(),
                            "assets": [],
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        with manifest.open("a", encoding="utf-8") as output:
            output.write("  provenance_index: ingestion-provenance.json\n")
        return package

    def test_valid_package_passes(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            issues = module.validate_package(self.make_package(Path(temp)))
        self.assertEqual([], [issue for issue in issues if issue.severity == "error"])

    def test_valid_pdf_package_passes(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            issues = module.validate_package(self.make_pdf_package(Path(temp)))
        self.assertEqual([], [issue for issue in issues if issue.severity == "error"])

    def test_pdf_package_requires_passed_ingestion_gate(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            issues = module.validate_package(self.make_pdf_package(Path(temp), gate_status="blocked"))
        codes = {issue.code for issue in issues}
        self.assertIn("INGESTION_GATE_NOT_PASSED", codes)

    def test_pdf_package_requires_conversion_manifest(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            issues = module.validate_package(self.make_pdf_package(Path(temp), include_conversion_manifest=False))
        codes = {issue.code for issue in issues}
        self.assertIn("INGESTION_MANIFEST_MISSING", codes)

    def test_pdf_package_requires_conversion_manifest_field(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_pdf_package(Path(temp))
            manifest = package / "manifest.yaml"
            manifest.write_text(
                "\n".join(
                    line
                    for line in manifest.read_text(encoding="utf-8").splitlines()
                    if "conversion_manifest:" not in line
                )
                + "\n",
                encoding="utf-8",
            )
            issues = module.validate_package(package)
        codes = {issue.code for issue in issues}
        self.assertIn("INGESTION_MANIFEST_MISSING", codes)

    def test_pdf_package_reports_malformed_conversion_manifest_json(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_pdf_package(Path(temp))
            manifest = package / "manifest.yaml"
            conversion_manifest = Path(
                module.manifest_scalar(
                    manifest.read_text(encoding="utf-8"),
                    "ingestion",
                    "conversion_manifest",
                )
            )
            conversion_manifest.write_text("{not-json", encoding="utf-8")
            issues = module.validate_package(package)
        codes = {issue.code for issue in issues}
        self.assertIn("INGESTION_MANIFEST_INVALID", codes)

    def test_pdf_package_accepts_contained_relative_conversion_paths(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_pdf_package(Path(temp))
            manifest = package / "manifest.yaml"
            text = manifest.read_text(encoding="utf-8")
            conversion_dir = Path(temp) / "markdown" / "商业管理" / "系统思考"
            text = text.replace(
                f"conversion_dir: {conversion_dir}",
                "conversion_dir: ../../markdown/商业管理/系统思考",
            ).replace(
                f"conversion_manifest: {conversion_dir / 'conversion-manifest.json'}",
                "conversion_manifest: ../../markdown/商业管理/系统思考/conversion-manifest.json",
            )
            manifest.write_text(text, encoding="utf-8")
            issues = module.validate_package(package)
        self.assertNotIn(
            "INGESTION_PATH_ESCAPE", {issue.code for issue in issues}, issues
        )

    def test_pdf_package_rejects_escaping_relative_conversion_manifest_path(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_pdf_package(Path(temp))
            manifest = package / "manifest.yaml"
            text = manifest.read_text(encoding="utf-8")
            conversion_dir = Path(temp) / "markdown" / "商业管理" / "系统思考"
            text = text.replace(
                f"conversion_manifest: {conversion_dir / 'conversion-manifest.json'}",
                "conversion_manifest: ../../../outside/conversion-manifest.json",
            )
            manifest.write_text(text, encoding="utf-8")
            issues = module.validate_package(package)
        codes = {issue.code for issue in issues}
        self.assertIn("INGESTION_PATH_ESCAPE", codes)

    def test_pdf_package_requires_conversion_validation_to_pass(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            issues = module.validate_package(self.make_pdf_package(Path(temp), conversion_status="invalid"))
        codes = {issue.code for issue in issues}
        self.assertIn("INGESTION_GATE_NOT_PASSED", codes)

    def test_pdf_package_requires_matching_source_hash(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            issues = module.validate_package(self.make_pdf_package(Path(temp), conversion_hash="b" * 64))
        codes = {issue.code for issue in issues}
        self.assertIn("INGESTION_SOURCE_HASH_MISMATCH", codes)

    def test_pdf_package_reconciles_provenance_units_with_actual_chapters(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_pdf_package(Path(temp))
            provenance_path = package / "ingestion-provenance.json"
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            injected = dict(provenance["source_units"][0])
            injected["chapter_id"] = "ch99"
            provenance["source_units"].append(injected)
            provenance_path.write_text(
                json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            issues = module.validate_package(package)
        codes = {issue.code for issue in issues}
        self.assertIn("INGESTION_PROVENANCE_INVALID", codes)

    def test_untraceable_reading_claim_fails(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            issues = module.validate_package(self.make_package(Path(temp), traceable=False))
        codes = {issue.code for issue in issues}
        self.assertIn("READING_UNTRACED", codes)

    def test_unsealed_source_fails(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            (package / "chapters" / "ch01" / "source.md").write_text(
                '<!-- page: 001 -->\n<p id="ch01-p001">Original.</p>\n', encoding="utf-8"
            )
            issues = module.validate_package(package)
        codes = {issue.code for issue in issues}
        self.assertIn("SOURCE_NOT_SEALED", codes)

    def test_missing_multimodal_coverage_fails(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            ledger = package / "reading-ledger.yaml"
            ledger.write_text(ledger.read_text(encoding="utf-8").replace("  figures:", "  omitted_figures:"), encoding="utf-8")
            issues = module.validate_package(package)
        codes = {issue.code for issue in issues}
        self.assertIn("COVERAGE_KIND_MISSING", codes)

    def test_missing_table_coverage_fails(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            ledger = package / "reading-ledger.yaml"
            ledger.write_text(ledger.read_text(encoding="utf-8").replace("  tables:", "  omitted_tables:"), encoding="utf-8")
            issues = module.validate_package(package)
        codes = {issue.code for issue in issues}
        self.assertIn("COVERAGE_KIND_MISSING", codes)

    def test_missing_book_navigation_fails(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            (package / "BOOK.md").unlink()
            issues = module.validate_package(package)
        codes = {issue.code for issue in issues}
        self.assertIn("ROOT_FILE_MISSING", codes)

    def test_missing_full_book_reading_fails(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            package = self.make_package(Path(temp))
            (package / "synthesis" / "full-book-reading.md").unlink()
            issues = module.validate_package(package)
        codes = {issue.code for issue in issues}
        self.assertIn("SYNTHESIS_FILE_MISSING", codes)


if __name__ == "__main__":
    unittest.main()
