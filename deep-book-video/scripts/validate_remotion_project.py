#!/usr/bin/env python3
"""Validate shared dependencies and an editable named Remotion Studio timeline."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, NamedTuple


class Issue(NamedTuple):
    severity: str
    code: str
    path: str
    message: str


def add(issues: list[Issue], code: str, path: Path | str, message: str) -> None:
    issues.append(Issue("error", code, str(path), message))


def read_json(path: Path, issues: list[Issue], code: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        add(issues, code, path, str(exc))
        return None


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def validate_project(project: Path, video_root: Path) -> list[Issue]:
    issues: list[Issue] = []
    project = project.resolve()
    video_root = video_root.resolve()

    if not is_within(project, video_root):
        add(issues, "PROJECT_OUTSIDE_VIDEO_ROOT", project, "Remotion project must be inside the declared video root")

    modules_link = project / "node_modules"
    if not modules_link.exists() and not modules_link.is_symlink():
        add(issues, "NODE_MODULES_MISSING", modules_link, "project requires a shared node_modules symbolic link")
    elif not modules_link.is_symlink():
        add(issues, "NODE_MODULES_NOT_SYMLINK", modules_link, "project-local node_modules copies are forbidden")
    else:
        try:
            modules_target = modules_link.resolve(strict=True)
        except OSError as exc:
            add(issues, "NODE_MODULES_LINK_BROKEN", modules_link, str(exc))
        else:
            if not is_within(modules_target, video_root):
                add(
                    issues,
                    "NODE_MODULES_TARGET_OUTSIDE_VIDEO_ROOT",
                    modules_link,
                    "shared node_modules target must remain inside the video root",
                )
            for package in ("remotion", "react", "react-dom"):
                manifest = modules_target / package / "package.json"
                if not manifest.is_file():
                    add(issues, "SHARED_PACKAGE_MISSING", manifest, f"shared dependency is missing: {package}")

    timeline_path = project / "src" / "timeline.json"
    script_path = project / "src" / "data" / "video-script.json"
    component_path = project / "src" / "BookVideo.tsx"
    timeline = read_json(timeline_path, issues, "TIMELINE_READ_ERROR")
    script = read_json(script_path, issues, "SCRIPT_READ_ERROR")
    try:
        component = component_path.read_text(encoding="utf-8")
    except OSError as exc:
        add(issues, "BOOK_VIDEO_READ_ERROR", component_path, str(exc))
        component = ""

    scenes = timeline.get("scenes") if isinstance(timeline, dict) else None
    pages = script.get("pages") if isinstance(script, dict) else None
    if not isinstance(scenes, list) or not scenes:
        add(issues, "TIMELINE_SCENES_MISSING", timeline_path, "timeline requires a non-empty scenes array")
        scenes = []
    if not isinstance(pages, list) or not pages:
        add(issues, "SCRIPT_PAGES_MISSING", script_path, "script requires a non-empty pages array")
        pages = []

    for index, scene in enumerate(scenes):
        scene_path = f"{timeline_path}:scenes[{index}]"
        if not isinstance(scene, dict):
            add(issues, "TIMELINE_SCENE_INVALID", scene_path, "scene must be an object")
            continue
        if not isinstance(scene.get("id"), str) or not scene["id"]:
            add(issues, "TIMELINE_SCENE_ID_INVALID", scene_path, "scene requires a page ID")
        if not isinstance(scene.get("name"), str) or not scene["name"]:
            add(issues, "TIMELINE_SCENE_NAME_INVALID", scene_path, "scene requires a visible Studio name")
        if not isinstance(scene.get("durationFrames"), int) or scene.get("durationFrames", 0) <= 0:
            add(issues, "TIMELINE_SCENE_DURATION_INVALID", scene_path, "durationFrames must be a positive integer")

    if isinstance(timeline, dict):
        if not isinstance(timeline.get("fps"), int) or timeline.get("fps", 0) <= 0:
            add(issues, "TIMELINE_FPS_INVALID", timeline_path, "fps must be a positive integer")
        valid_durations = [scene.get("durationFrames") for scene in scenes if isinstance(scene, dict)]
        if all(isinstance(value, int) and value > 0 for value in valid_durations):
            if timeline.get("totalFrames") != sum(valid_durations):
                add(issues, "TIMELINE_TOTAL_MISMATCH", timeline_path, "totalFrames must equal the sum of scene durations")

    if len(scenes) != len(pages):
        add(issues, "TIMELINE_PAGE_COUNT_MISMATCH", timeline_path, "timeline scenes and script pages must have equal counts")
    for index, (scene, page) in enumerate(zip(scenes, pages)):
        if not isinstance(scene, dict) or not isinstance(page, dict):
            continue
        if scene.get("id") != page.get("page_id"):
            add(issues, "TIMELINE_PAGE_ORDER_MISMATCH", f"{timeline_path}:scenes[{index}]", "scene ID/order must match script page ID/order")
        expected_name = page.get("studio_sequence_name")
        if scene.get("name") != expected_name:
            add(issues, "TIMELINE_SCENE_NAME_MISMATCH", f"{timeline_path}:scenes[{index}]", "scene name must match studio_sequence_name")

    if re.search(
        r"\.map\s*\(\s*(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*<(?:Series\.)?Sequence\b",
        component,
    ):
        add(
            issues,
            "PROGRAMMATIC_TIMELINE_FORBIDDEN",
            component_path,
            "use explicit authored JSX for each Studio timeline sequence; do not generate sequences with map()",
        )
    explicit_count = len(re.findall(r"<(?:Series\.)?Sequence\b", component))
    if pages and explicit_count != len(pages):
        add(
            issues,
            "EXPLICIT_SEQUENCE_COUNT_MISMATCH",
            component_path,
            "BookVideo.tsx must contain one explicit Sequence element per page",
        )
    for index, page in enumerate(pages):
        if not isinstance(page, dict):
            continue
        studio_name = page.get("studio_sequence_name")
        literal_name = None
        if isinstance(studio_name, str):
            literal_name = re.search(
                r"<(?:Series\.)?Sequence\b[^>]*\bname\s*=\s*[\"']"
                + re.escape(studio_name)
                + r"[\"']",
                component,
            )
        if isinstance(studio_name, str) and literal_name is None:
            add(
                issues,
                "STUDIO_SEQUENCE_NAME_MISSING",
                f"{component_path}:pages[{index}]",
                "explicit Sequence must use the page's literal studio_sequence_name in its name prop",
            )

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a deep-book-video Remotion Studio project")
    parser.add_argument("project", type=Path)
    parser.add_argument("--video-root", required=True, type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    issues = validate_project(args.project, args.video_root)
    if args.as_json:
        print(json.dumps([issue._asdict() for issue in issues], ensure_ascii=False, indent=2))
    elif issues:
        for issue in issues:
            print(f"{issue.severity.upper()} {issue.code} {issue.path}: {issue.message}")
    else:
        print("OK: Remotion project uses shared dependencies and an explicit named Studio timeline")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
