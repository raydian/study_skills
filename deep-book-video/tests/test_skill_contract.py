import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    def test_required_files_exist(self):
        for relative in (
            "SKILL.md",
            "agents/openai.yaml",
            "references/input-contract.md",
            "references/routing-and-engines.md",
            "references/static-visual-principles.md",
            "references/video-script-schema.md",
            "references/quality-gates.md",
            "references/remotion-production.md",
            "references/remotion-project-setup.md",
            "scripts/validate_video_script.py",
            "scripts/validate_remotion_project.py",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_required_architecture_is_documented(self):
        corpus = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [ROOT / "SKILL.md", *sorted((ROOT / "references").glob("*.md"))]
            if path.is_file()
        )
        for term in (
            "Book Profile",
            "Content Unit Router",
            "Depth Engine",
            "Narrative Mode",
            "Global Video Thesis",
            "source_refs",
            "Evidence Gate",
            "Visual Legibility Gate",
            "image_prompt",
            "subtitle",
            "voiceover",
            "duration_seconds",
            "page_purpose",
            "Remotion",
            "duration_in_frames",
            "staticFile",
            "Series.Sequence",
            "Studio Confirmation Gate",
            "video-voiceover",
            "--sync-remotion",
            "voiceover-handoff.json",
            "MUST NOT render",
            "node_modules",
            "symbolic link",
            "explicit authored JSX",
            "studio_sequence_name",
        ):
            self.assertIn(term, corpus)

    def test_no_placeholders_remain(self):
        for path in ROOT.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".yaml", ".py", ".json"}:
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("[" + "TODO", text, str(path))
                self.assertNotIn("TB" + "D", text, str(path))


if __name__ == "__main__":
    unittest.main()
