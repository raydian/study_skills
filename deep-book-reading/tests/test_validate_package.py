import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_book_package.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_book_package", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("validator module cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateBookPackageTests(unittest.TestCase):
    def make_package(self, root: Path, *, traceable: bool = True) -> Path:
        package = root / "example-book"
        chapter = package / "chapters" / "ch01"
        synthesis = package / "synthesis"
        chapter.mkdir(parents=True)
        synthesis.mkdir(parents=True)

        (package / "BOOK.md").write_text("# Example book\n", encoding="utf-8")

        (package / "manifest.yaml").write_text(
            "schema_version: 1\nbook_id: example-book\nsource_state: sealed\n"
            "source_sha256: " + "a" * 64 + "\n",
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

    def test_valid_package_passes(self):
        module = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            issues = module.validate_package(self.make_package(Path(temp)))
        self.assertEqual([], [issue for issue in issues if issue.severity == "error"])

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
