from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (SKILL_ROOT / relative_path).read_text(encoding="utf-8")


class SkillContractTest(unittest.TestCase):
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
            "references/audio-voiceover.md",
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

    def test_measured_audio_drives_visual_frame_state(self) -> None:
        skill = read("SKILL.md")
        audio = read("references/audio-voiceover.md")

        self.assertIn(
            "measured audio timing is the source of truth for subtitles, "
            "scene boundaries, visual steps, and total frames",
            skill,
        )
        self.assertIn(
            "measured audio cue -> subtitle cue -> visualCueId/stepId -> "
            "Remotion frame state",
            audio,
        )
        self.assertIn("must not appear before its spoken cue", audio)

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
