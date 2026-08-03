from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "init_subject_video.py"


class InitSubjectVideoTest(unittest.TestCase):
    def run_initializer(self, subject: str, knowledge_name: str, root: Path) -> Path:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                subject,
                knowledge_name,
                "--root",
                str(root),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        project = Path(result.stdout.strip())
        self.assertTrue(project.is_dir())
        return project

    def test_physics_project_contains_physics_planning_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = self.run_initializer("物理", "牛顿第二定律", Path(directory))
            content = (project / "content-design.md").read_text(encoding="utf-8")
            storyboard = (project / "storyboard.md").read_text(encoding="utf-8")

            for heading in (
                "## 视频类型路由",
                "## 核心问题与物理模型",
                "## 核心考核重点",
                "## 难点分析",
                "## 易错点与认知误区",
                "## 典型母题",
                "## 单条件变式",
                "## 场景连续性设计",
                "## 物理准确性检查",
            ):
                self.assertIn(heading, content)

            for column in (
                "所属阶段/类型",
                "核心问题",
                "继承对象/结论",
                "考点/难点/易错点",
                "下一场桥接",
            ):
                self.assertIn(column, storyboard)

    def test_non_physics_project_keeps_generic_template(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = self.run_initializer("化学", "氧化还原反应", Path(directory))
            content = (project / "content-design.md").read_text(encoding="utf-8")

            self.assertIn("## 知识点分析", content)
            self.assertIn("## 学生难点与误区", content)
            self.assertNotIn("## 视频类型路由", content)
            self.assertNotIn("## 典型母题", content)


if __name__ == "__main__":
    unittest.main()
