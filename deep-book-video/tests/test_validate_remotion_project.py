import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_remotion_project.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_remotion_project", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def build_project(root: Path, *, symlink_modules: bool = True, programmatic: bool = False) -> tuple[Path, Path]:
    video_root = root / "video"
    shared = video_root / "node_modules"
    for package in ("remotion", "react", "react-dom"):
        package_dir = shared / package
        package_dir.mkdir(parents=True, exist_ok=True)
        (package_dir / "package.json").write_text(json.dumps({"name": package}), encoding="utf-8")

    project = video_root / "books" / "example" / "remotion"
    (project / "src" / "data").mkdir(parents=True, exist_ok=True)
    if symlink_modules:
        (project / "node_modules").symlink_to(shared, target_is_directory=True)
    else:
        (project / "node_modules").mkdir()

    timeline = {
        "fps": 30,
        "totalFrames": 300,
        "scenes": [
            {
                "id": "P001",
                "name": "P001｜开场：看不见的规则",
                "durationFrames": 300,
            }
        ],
    }
    (project / "src" / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False), encoding="utf-8")
    script = {
        "pages": [
            {
                "page_id": "P001",
                "page_name": "开场：看不见的规则",
                "studio_sequence_name": "P001｜开场：看不见的规则",
            }
        ]
    }
    (project / "src" / "data" / "video-script.json").write_text(json.dumps(script, ensure_ascii=False), encoding="utf-8")
    if programmatic:
        markup = "script.pages.map((page) => <Series.Sequence name={page.studio_sequence_name} />)"
    else:
        markup = '<Series.Sequence name="P001｜开场：看不见的规则" durationInFrames={300}>'
    (project / "src" / "BookVideo.tsx").write_text(markup, encoding="utf-8")
    return project, video_root


class RemotionProjectValidatorTests(unittest.TestCase):
    def test_valid_shared_modules_and_named_timeline_pass(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            project, video_root = build_project(Path(tmp))
            self.assertEqual([], validator.validate_project(project, video_root))

    def test_real_project_node_modules_is_rejected(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            project, video_root = build_project(Path(tmp), symlink_modules=False)
            codes = {issue.code for issue in validator.validate_project(project, video_root)}
            self.assertIn("NODE_MODULES_NOT_SYMLINK", codes)

    def test_programmatic_sequence_map_is_rejected(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as tmp:
            project, video_root = build_project(Path(tmp), programmatic=True)
            codes = {issue.code for issue in validator.validate_project(project, video_root)}
            self.assertIn("PROGRAMMATIC_TIMELINE_FORBIDDEN", codes)


if __name__ == "__main__":
    unittest.main()
