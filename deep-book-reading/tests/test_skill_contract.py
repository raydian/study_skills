import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    def test_required_directories_exist(self):
        for name in ("agents", "workflows", "references", "profiles", "templates", "tests", "scripts"):
            self.assertTrue((ROOT / name).is_dir(), name)

    def test_skill_routes_all_six_passes(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for number in range(6):
            self.assertIn(f"PASS {number}", text)

    def test_core_contract_terms_are_present(self):
        corpus = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [ROOT / "SKILL.md", *sorted((ROOT / "references").glob("*.md"))]
        )
        for term in (
            "immutable",
            "Reading Ledger",
            "Evidence Ledger",
            "Book Manifest",
            "ai_inference",
            "Counterexample",
            "Skillability",
            "source_refs",
        ):
            self.assertIn(term, corpus)

    def test_no_unresolved_placeholders(self):
        for path in ROOT.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".yaml", ".py"}:
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("[" + "TODO", text, str(path))
                self.assertNotIn("TB" + "D", text, str(path))

    def test_pdf_ingestion_resources_exist(self):
        required = (
            ROOT / "workflows" / "pdf-ingestion.md",
            ROOT / "references" / "pdf-ingestion-contract.md",
            ROOT / "templates" / "ingestion" / "conversion-manifest.json",
            ROOT / "scripts" / "ingest_pdf.py",
            ROOT / "scripts" / "pdf_ingestion.py",
        )
        for path in required:
            self.assertTrue(path.is_file(), str(path))

    def test_skill_routes_pdf_through_mineru_before_pass_zero(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("INGEST PDF", text)
        self.assertIn("MinerU", text)
        self.assertLess(text.index("INGEST PDF"), text.index("PASS 0"))

    def test_skill_has_no_external_pdf_skill_dependency(self):
        forbidden = "pdf-" + "markdown"
        corpus = "\n".join(
            path.read_text(encoding="utf-8")
            for path in ROOT.rglob("*")
            if path.is_file()
            and path.suffix in {".md", ".yaml", ".py", ".json"}
            and "tests" not in path.parts
        )
        self.assertNotIn(forbidden, corpus.lower())


if __name__ == "__main__":
    unittest.main()
