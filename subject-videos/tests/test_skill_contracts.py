from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (SKILL_ROOT / relative_path).read_text(encoding="utf-8")


class SkillContractTest(unittest.TestCase):
    def test_subject_videos_contains_no_voiceover_operations(self) -> None:
        self.assertFalse((SKILL_ROOT / "references/audio-voiceover.md").exists())
        markdown_files = (SKILL_ROOT / "references").rglob("*.md")
        combined = read("SKILL.md") + "\n" + "\n".join(
            path.read_text(encoding="utf-8")
            for path in markdown_files
            if path.name != "audio-voiceover.md"
        )

        for forbidden in (
            "$video-voiceover",
            "ffprobe",
            "audio_timeline.json",
            "speechRate",
            "call TTS",
            "Doubao TTS",
        ):
            self.assertNotIn(forbidden, combined)

    def test_voiceover_is_an_explicit_external_handoff(self) -> None:
        skill = read("SKILL.md")
        english = read("references/english-video-structure.md")

        self.assertIn("Narration Handoff Boundary", skill)
        self.assertIn("Do not generate or attach audio", skill)
        self.assertNotIn("$video-voiceover", skill)
        self.assertNotIn("audio_timeline.json", skill)
        self.assertNotIn("zh_female_yingyujiaoxue_uranus_bigtts", skill)
        self.assertNotIn("$video-voiceover", english)
        self.assertNotIn("ffprobe", english)

    def test_english_videos_build_three_parts_then_merge(self) -> None:
        skill = read("SKILL.md")
        english = read("references/english-video-structure.md")

        self.assertIn("English Video Routing", skill)
        self.assertIn("three independently authored parts", skill)
        self.assertIn("unit-cover", skill)
        self.assertIn("chapter-01", skill)
        self.assertIn("English-only narration/script text", skill)
        self.assertIn("shadowing", skill)
        self.assertIn("Build Independently, Then Merge", english)
        self.assertIn("subtitleEn === textEn", english)
        self.assertIn("Narration Handoff", english)

    def test_english_vocabulary_videos_use_a_dedicated_learning_route(self) -> None:
        skill = read("SKILL.md")
        english = read("references/english-video-structure.md")

        self.assertIn("Vocabulary and Phrase Specialization", skill)
        self.assertIn("vocabulary-and-phrase route takes precedence", skill)
        self.assertIn("all core vocabulary and core phrases", skill)
        self.assertIn("Vocabulary and Phrase Route", english)
        self.assertIn("semantic module", english)
        self.assertIn("scene + communicative function + usage frame", english)
        self.assertIn("recognition", english)
        self.assertIn("retrieval", english)
        self.assertIn("transfer", english)
        self.assertIn("one primary module", english)

    def test_english_vocabulary_videos_do_not_force_full_course_sections(self) -> None:
        skill = read("SKILL.md")
        english = read("references/english-video-structure.md")
        combined = skill + "\n" + english

        self.assertIn("Do not force the full reading", combined)
        self.assertIn("shadowing", combined)
        self.assertIn("spoken-output section", combined)
        self.assertIn("short sentence-level application", combined)

    def test_cover_title_is_dominant_core_knowledge_point(self) -> None:
        skill = read("SKILL.md")
        cover = read("references/cover-design.md")

        self.assertIn("current core knowledge point", skill)
        self.assertIn("128-160px", cover)
        self.assertIn("largest and first visual focus", cover)

    def test_subtitles_are_verbatim_and_capped_at_two_lines(self) -> None:
        files = (
            "SKILL.md",
            "references/teaching-script.md",
            "references/visual-system.md",
            "references/chinese-visual-design.md",
            "references/physics-video-structure.md",
        )
        combined = "\n".join(read(path) for path in files)

        self.assertNotIn("exactly one line", combined)
        self.assertNotIn("exactly one rendered line", combined)
        self.assertIn("at most two rendered lines", combined)
        self.assertIn("subtitle === text", combined)
        self.assertIn(
            "never summarize, shorten, omit, paraphrase, or rewrite", combined
        )

    def test_physics_projects_use_template_and_shared_dependencies(self) -> None:
        skill = read("SKILL.md")
        visual = read("references/physics-visual-design.md")

        self.assertIn("scripts/create_physics_video.py", skill)
        self.assertIn("video/物理/物理视频模板/", skill)
        self.assertIn("video/物理/node_modules", skill)
        self.assertIn("node_modules -> ../node_modules", skill)
        self.assertIn("only the standardized cover and closing page", skill)
        self.assertIn("#151A24", visual)
        self.assertIn("#68C3FF", visual)
        self.assertIn("#FFB547", visual)
        self.assertIn("#FF5A5F", visual)
        self.assertIn("Never use black text", visual)
        self.assertIn("Do not let lines, symbols, arrows, or labels overlap", visual)
        self.assertIn("Do not render unless the user explicitly asks", visual)


if __name__ == "__main__":
    unittest.main()
