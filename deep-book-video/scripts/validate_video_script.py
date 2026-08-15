#!/usr/bin/env python3
"""Validate the observable deep-book-video script contract using stdlib only."""

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


ROOT_OBJECTS = (
    "project",
    "global_video_thesis",
    "book_profile",
    "narrative_plan",
    "visual_bible",
    "remotion",
    "voiceover_handoff",
    "pages",
)
PROJECT_FIELDS = (
    "title",
    "book_title",
    "target_audience",
    "target_duration_seconds",
    "aspect_ratio",
    "resolution",
    "spoiler_policy",
)
THESIS_FIELDS = ("statement", "viewer_shift", "scope", "counter_thesis")
PROFILE_FIELDS = ("primary_type", "secondary_types", "knowledge_structure")
NARRATIVE_FIELDS = ("mode", "arc_steps", "selected_unit_ids")
VISUAL_BIBLE_FIELDS = (
    "style",
    "palette",
    "recurring_motifs",
    "character_continuity",
    "forbidden_elements",
)
REMOTION_FIELDS = (
    "engine",
    "composition_id",
    "fps",
    "width",
    "height",
    "duration_in_frames",
    "studio_confirmation",
    "render_policy",
    "audio_policy",
    "dependency_policy",
    "studio_timeline_mode",
)
VOICEOVER_HANDOFF_FIELDS = (
    "skill",
    "status",
    "script_file",
    "sync_remotion",
    "subject_hint",
    "render_after_voiceover",
    "preview_after_voiceover",
)
PAGE_FIELDS = (
    "page_id",
    "page_name",
    "studio_sequence_name",
    "sequence",
    "page_type",
    "page_purpose",
    "thesis_relation",
    "content_route",
    "claim",
    "knowledge_unit_ids",
    "source_refs",
    "attribution",
    "evidence_quality",
    "subtitle",
    "voiceover",
    "duration_seconds",
    "remotion_timeline",
    "visual",
    "transition",
)
ROUTE_FIELDS = ("primary_role", "depth_engine", "reasoning_move")
EVIDENCE_FIELDS = ("strength", "directness", "limitations")
SUBTITLE_FIELDS = (
    "text",
    "lines",
    "placement",
    "font_family",
    "font_size_px",
    "font_weight",
    "text_color",
    "background_treatment",
    "contrast_ratio_target",
)
VOICEOVER_FIELDS = ("text", "delivery")
REMOTION_TIMELINE_FIELDS = (
    "start_frame",
    "duration_in_frames",
    "end_frame_exclusive",
    "image_src",
)
VISUAL_FIELDS = ("function", "image_prompt", "composition", "readability")
PROMPT_FIELDS = (
    "subject",
    "setting",
    "action",
    "era_culture",
    "art_direction",
    "palette",
    "lighting",
    "camera",
    "composition",
    "symbolic_elements",
    "continuity",
    "safe_text_area",
    "realism_constraints",
    "negative_prompt",
    "rendered_prompt",
)
COMPOSITION_FIELDS = (
    "focal_point",
    "depth_layers",
    "text_safe_zone",
    "reading_order",
    "crop_safety",
)
READABILITY_FIELDS = (
    "background_control",
    "local_contrast",
    "busy_area_avoidance",
    "subtitle_box",
    "min_font_px",
)
PAGE_TYPES = {
    "title",
    "hook",
    "context",
    "question",
    "definition",
    "claim",
    "mechanism",
    "evidence",
    "case",
    "turning_point",
    "method",
    "derivation",
    "close_reading",
    "counterpoint",
    "limitation",
    "application",
    "synthesis",
    "ending",
    "credits",
}
THESIS_RELATIONS = {
    "opens",
    "defines",
    "advances",
    "evidences",
    "explains",
    "contrasts",
    "qualifies",
    "applies",
    "synthesizes",
}
DEPTH_ENGINES = {
    "system-mechanism",
    "causal-contingency",
    "argument-assumption",
    "evidence-calibration",
    "procedure-tradeoff",
    "derivation-proof",
    "character-choice",
    "close-reading-form",
    "interpretive-tradition",
    "visual-analysis",
    "comparison-boundary",
    "cluster-constellation",
}
NARRATIVE_MODES = {
    "question_to_model",
    "causal_investigation",
    "turning_points",
    "mechanism_discovery",
    "debate_dialectic",
    "problem_to_method",
    "guided_derivation",
    "scene_to_meaning",
    "thematic_constellation",
    "case_led_transfer",
    "visual_tour",
}
ATTRIBUTIONS = {
    "author_claim",
    "source_evidence",
    "quoted_view",
    "case",
    "ai_explanation",
    "ai_inference",
    "ai_synthesis",
    "critical_analysis",
    "editorial_note",
}
MOTION_TERMS = re.compile(
    r"\b(?:pan|zoom|parallax|motion graphics?|animated?|camera movement)\b|推拉|摇移|运镜|动效|动画",
    re.IGNORECASE,
)
AI_EVIDENCE = re.compile(r"^(?:ai[-_ ]?image|image[-_ ]?prompt|generated[-_ ]?image)", re.IGNORECASE)


def add(issues: list[Issue], code: str, path: str, message: str) -> None:
    issues.append(Issue("error", code, path, message))


def require_fields(
    obj: Any,
    fields: tuple[str, ...],
    path: str,
    issues: list[Issue],
    code: str,
) -> None:
    if not isinstance(obj, dict):
        add(issues, code, path, "must be an object")
        return
    for field in fields:
        value = obj.get(field)
        if value is None or value == "" or value == []:
            add(issues, code, f"{path}.{field}", "required field is missing or empty")


def cjk_count(text: str) -> int:
    return len(re.findall(r"[\u3400-\u9fff]", text))


def is_safe_public_path(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts and not value.startswith("public/")


def validate_page(page: Any, index: int, issues: list[Issue]) -> None:
    path = f"pages[{index}]"
    require_fields(page, PAGE_FIELDS, path, issues, "PAGE_FIELD_MISSING")
    if not isinstance(page, dict):
        return

    page_id = page.get("page_id")
    page_name = page.get("page_name")
    studio_sequence_name = page.get("studio_sequence_name")
    if not isinstance(page_id, str) or not re.fullmatch(r"P\d{3,}", page_id):
        add(issues, "PAGE_ID_FORMAT_INVALID", f"{path}.page_id", "page ID must use the stable P### format")
    if not isinstance(page_name, str) or not page_name.strip():
        add(issues, "PAGE_NAME_INVALID", f"{path}.page_name", "page name must be non-empty")
    expected_studio_name = f"{page_id}｜{page_name}" if isinstance(page_id, str) and isinstance(page_name, str) else None
    if not isinstance(studio_sequence_name, str) or studio_sequence_name != expected_studio_name:
        add(
            issues,
            "STUDIO_SEQUENCE_NAME_INVALID",
            f"{path}.studio_sequence_name",
            "Studio sequence name must equal page_id + '｜' + page_name",
        )

    page_type = page.get("page_type")
    if page_type not in PAGE_TYPES:
        add(issues, "PAGE_TYPE_INVALID", f"{path}.page_type", f"unsupported page type: {page_type!r}")
    relation = page.get("thesis_relation")
    if relation not in THESIS_RELATIONS:
        add(issues, "THESIS_RELATION_INVALID", f"{path}.thesis_relation", f"unsupported relation: {relation!r}")

    route = page.get("content_route")
    require_fields(route, ROUTE_FIELDS, f"{path}.content_route", issues, "CONTENT_ROUTE_INCOMPLETE")
    if isinstance(route, dict) and route.get("depth_engine") not in DEPTH_ENGINES:
        add(issues, "DEPTH_ENGINE_INVALID", f"{path}.content_route.depth_engine", "unsupported Depth Engine")

    refs = page.get("source_refs")
    if not isinstance(refs, list) or not refs:
        add(issues, "PAGE_SOURCE_REFS_MISSING", f"{path}.source_refs", "every page requires source or editorial provenance")
    else:
        for ref_index, record in enumerate(refs):
            ref_path = f"{path}.source_refs[{ref_index}]"
            if not isinstance(record, dict) or not record.get("ref") or not record.get("relation"):
                add(issues, "SOURCE_REF_INVALID", ref_path, "source ref requires ref and relation")
                continue
            if AI_EVIDENCE.match(str(record["ref"])):
                add(issues, "AI_IMAGE_AS_EVIDENCE", ref_path, "AI images and prompts cannot serve as evidence")

    if page.get("attribution") not in ATTRIBUTIONS:
        add(issues, "ATTRIBUTION_INVALID", f"{path}.attribution", "attribution is missing or unsupported")

    evidence = page.get("evidence_quality")
    require_fields(evidence, EVIDENCE_FIELDS, f"{path}.evidence_quality", issues, "EVIDENCE_QUALITY_INCOMPLETE")
    if isinstance(evidence, dict):
        if evidence.get("strength") not in {"strong", "moderate", "weak", "not_applicable"}:
            add(issues, "EVIDENCE_STRENGTH_INVALID", f"{path}.evidence_quality.strength", "invalid evidence strength")
        if evidence.get("directness") not in {"direct", "indirect", "anecdotal", "inferred", "not_applicable"}:
            add(issues, "EVIDENCE_DIRECTNESS_INVALID", f"{path}.evidence_quality.directness", "invalid evidence directness")

    subtitle = page.get("subtitle")
    require_fields(subtitle, SUBTITLE_FIELDS, f"{path}.subtitle", issues, "SUBTITLE_INCOMPLETE")
    if isinstance(subtitle, dict):
        lines = subtitle.get("lines")
        if not isinstance(lines, list) or not 1 <= len(lines) <= 3 or not all(isinstance(line, str) and line.strip() for line in lines):
            add(issues, "SUBTITLE_LINE_COUNT", f"{path}.subtitle.lines", "subtitle requires 1-3 non-empty lines")
        else:
            for line_index, line in enumerate(lines):
                if cjk_count(line) > 20:
                    add(issues, "SUBTITLE_LINE_TOO_LONG", f"{path}.subtitle.lines[{line_index}]", "Chinese subtitle line exceeds 20 CJK characters")
                if cjk_count(line) == 0 and len(line) > 42:
                    add(issues, "SUBTITLE_LINE_TOO_LONG", f"{path}.subtitle.lines[{line_index}]", "Latin subtitle line exceeds 42 characters")
        if not isinstance(subtitle.get("font_size_px"), (int, float)) or subtitle.get("font_size_px", 0) < 64:
            add(issues, "SUBTITLE_TOO_SMALL", f"{path}.subtitle.font_size_px", "1920x1080 normal subtitles must be at least 64 px")
        if not isinstance(subtitle.get("font_weight"), (int, float)) or subtitle.get("font_weight", 0) < 700:
            add(issues, "SUBTITLE_WEIGHT_TOO_LIGHT", f"{path}.subtitle.font_weight", "subtitle weight must be at least 700")
        if not isinstance(subtitle.get("contrast_ratio_target"), (int, float)) or subtitle.get("contrast_ratio_target", 0) < 7:
            add(issues, "SUBTITLE_CONTRAST_LOW", f"{path}.subtitle.contrast_ratio_target", "contrast target must be at least 7:1")

    voiceover = page.get("voiceover")
    require_fields(voiceover, VOICEOVER_FIELDS, f"{path}.voiceover", issues, "VOICEOVER_INCOMPLETE")
    duration = page.get("duration_seconds")
    if not isinstance(duration, (int, float)) or not 4 <= duration <= 25:
        add(issues, "PAGE_DURATION_INVALID", f"{path}.duration_seconds", "page duration must be between 4 and 25 seconds")

    timeline = page.get("remotion_timeline")
    require_fields(timeline, REMOTION_TIMELINE_FIELDS, f"{path}.remotion_timeline", issues, "REMOTION_TIMELINE_INCOMPLETE")
    if isinstance(timeline, dict):
        start = timeline.get("start_frame")
        frames = timeline.get("duration_in_frames")
        end = timeline.get("end_frame_exclusive")
        if not all(isinstance(value, int) for value in (start, frames, end)) or frames <= 0:
            add(issues, "PAGE_FRAME_VALUE_INVALID", f"{path}.remotion_timeline", "frame values must be integers and duration must be positive")
        elif end != start + frames:
            add(issues, "PAGE_FRAME_MATH_INVALID", f"{path}.remotion_timeline", "exclusive end must equal start plus duration")
        for asset_field in ("image_src",):
            if not is_safe_public_path(timeline.get(asset_field)):
                add(issues, "REMOTION_ASSET_PATH_INVALID", f"{path}.remotion_timeline.{asset_field}", "asset path must be relative to public/, without the public/ prefix or parent traversal")

    visual = page.get("visual")
    require_fields(visual, VISUAL_FIELDS, f"{path}.visual", issues, "VISUAL_INCOMPLETE")
    if isinstance(visual, dict):
        prompt = visual.get("image_prompt")
        require_fields(prompt, PROMPT_FIELDS, f"{path}.visual.image_prompt", issues, "IMAGE_PROMPT_INCOMPLETE")
        if isinstance(prompt, dict):
            rendered = prompt.get("rendered_prompt", "")
            if not isinstance(rendered, str) or len(rendered.strip()) < 120:
                add(issues, "IMAGE_PROMPT_TOO_SHALLOW", f"{path}.visual.image_prompt.rendered_prompt", "assembled image prompt must be at least 120 characters")
            negative = str(prompt.get("negative_prompt", ""))
            if not re.search(r"文字|text|letters?", negative, re.IGNORECASE) or not re.search(r"水印|watermark", negative, re.IGNORECASE):
                add(issues, "NEGATIVE_PROMPT_INCOMPLETE", f"{path}.visual.image_prompt.negative_prompt", "negative prompt must forbid generated text and watermarks")
            combined = " ".join(str(prompt.get(key, "")) for key in ("action", "camera", "rendered_prompt"))
            if MOTION_TERMS.search(combined):
                add(issues, "MOTION_SPECIFIED", f"{path}.visual.image_prompt", "static pages cannot specify motion or simulated camera movement")

        composition = visual.get("composition")
        require_fields(composition, COMPOSITION_FIELDS, f"{path}.visual.composition", issues, "COMPOSITION_INCOMPLETE")
        readability = visual.get("readability")
        require_fields(readability, READABILITY_FIELDS, f"{path}.visual.readability", issues, "READABILITY_INCOMPLETE")
        if isinstance(readability, dict):
            if not isinstance(readability.get("min_font_px"), (int, float)) or readability.get("min_font_px", 0) < 64:
                add(issues, "READABILITY_MIN_FONT_TOO_SMALL", f"{path}.visual.readability.min_font_px", "readability constraint must preserve at least 64 px")

    if page.get("transition") != "hard_cut":
        add(issues, "NON_STATIC_TRANSITION", f"{path}.transition", "only hard_cut is allowed")


def validate_script(data: Any) -> list[Issue]:
    issues: list[Issue] = []
    if not isinstance(data, dict):
        return [Issue("error", "ROOT_INVALID", "$", "script root must be a JSON object")]
    if data.get("schema_version") != 3:
        add(issues, "SCHEMA_VERSION_INVALID", "schema_version", "schema_version must be 3")
    require_fields(data, ROOT_OBJECTS, "$", issues, "ROOT_FIELD_MISSING")
    require_fields(data.get("project"), PROJECT_FIELDS, "project", issues, "PROJECT_INCOMPLETE")
    require_fields(data.get("global_video_thesis"), THESIS_FIELDS, "global_video_thesis", issues, "THESIS_INCOMPLETE")
    require_fields(data.get("book_profile"), PROFILE_FIELDS, "book_profile", issues, "BOOK_PROFILE_INCOMPLETE")
    require_fields(data.get("narrative_plan"), NARRATIVE_FIELDS, "narrative_plan", issues, "NARRATIVE_PLAN_INCOMPLETE")
    narrative = data.get("narrative_plan")
    if isinstance(narrative, dict) and narrative.get("mode") not in NARRATIVE_MODES:
        add(issues, "NARRATIVE_MODE_INVALID", "narrative_plan.mode", "unsupported Narrative Mode")
    require_fields(data.get("visual_bible"), VISUAL_BIBLE_FIELDS, "visual_bible", issues, "VISUAL_BIBLE_INCOMPLETE")
    remotion = data.get("remotion")
    require_fields(remotion, REMOTION_FIELDS, "remotion", issues, "REMOTION_CONFIG_INCOMPLETE")
    if isinstance(remotion, dict):
        if remotion.get("engine") != "remotion":
            add(issues, "REMOTION_ENGINE_REQUIRED", "remotion.engine", "engine must be remotion")
        if not isinstance(remotion.get("fps"), int) or remotion.get("fps", 0) <= 0:
            add(issues, "REMOTION_FPS_INVALID", "remotion.fps", "fps must be a positive integer")
        for dimension in ("width", "height"):
            if not isinstance(remotion.get(dimension), int) or remotion.get(dimension, 0) <= 0:
                add(issues, "REMOTION_DIMENSION_INVALID", f"remotion.{dimension}", "dimension must be a positive integer")
        if not isinstance(remotion.get("duration_in_frames"), int) or remotion.get("duration_in_frames", 0) <= 0:
            add(issues, "REMOTION_DURATION_INVALID", "remotion.duration_in_frames", "duration must be a positive integer")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]*", str(remotion.get("composition_id", ""))):
            add(issues, "REMOTION_COMPOSITION_ID_INVALID", "remotion.composition_id", "composition ID must be CLI-safe")
        if remotion.get("studio_confirmation") not in {"pending", "approved"}:
            add(issues, "STUDIO_CONFIRMATION_INVALID", "remotion.studio_confirmation", "Studio confirmation must be pending or approved")
        if remotion.get("render_policy") != "do_not_render":
            add(issues, "RENDER_POLICY_INVALID", "remotion.render_policy", "render policy must be do_not_render")
        if remotion.get("audio_policy") != "no_audio_before_studio_confirmation":
            add(issues, "AUDIO_POLICY_INVALID", "remotion.audio_policy", "audio policy must prohibit audio before Studio confirmation")
        if remotion.get("dependency_policy") != "reuse_video_shared_node_modules_symlink":
            add(
                issues,
                "DEPENDENCY_POLICY_INVALID",
                "remotion.dependency_policy",
                "dependencies must reuse a compatible node_modules inside the video root through a symbolic link",
            )
        if remotion.get("studio_timeline_mode") != "explicit_named_sequences":
            add(
                issues,
                "STUDIO_TIMELINE_MODE_INVALID",
                "remotion.studio_timeline_mode",
                "Studio timeline must use explicit named sequences",
            )
        if any(key in remotion for key in ("codec", "output_file", "render_command")):
            add(issues, "RENDER_CONFIGURATION_FORBIDDEN", "remotion", "render configuration is outside this skill")

    handoff = data.get("voiceover_handoff")
    require_fields(handoff, VOICEOVER_HANDOFF_FIELDS, "voiceover_handoff", issues, "VOICEOVER_HANDOFF_INCOMPLETE")
    if isinstance(handoff, dict):
        if handoff.get("skill") != "video-voiceover":
            add(issues, "VOICEOVER_SKILL_INVALID", "voiceover_handoff.skill", "handoff skill must be video-voiceover")
        if handoff.get("sync_remotion") is not True:
            add(issues, "VOICEOVER_SYNC_REQUIRED", "voiceover_handoff.sync_remotion", "voiceover handoff must sync measured audio back to Remotion")
        if handoff.get("render_after_voiceover") is not False:
            add(issues, "POST_VOICEOVER_RENDER_FORBIDDEN", "voiceover_handoff.render_after_voiceover", "voiceover handoff must not render")
        if handoff.get("preview_after_voiceover") is not True:
            add(issues, "POST_VOICEOVER_PREVIEW_REQUIRED", "voiceover_handoff.preview_after_voiceover", "voiceover handoff must return to Studio preview")
        confirmation = remotion.get("studio_confirmation") if isinstance(remotion, dict) else None
        status = handoff.get("status")
        if confirmation == "pending" and status != "blocked_until_studio_confirmed":
            add(issues, "VOICEOVER_HANDOFF_PREMATURE", "voiceover_handoff.status", "voiceover must wait for explicit Studio confirmation")
        if confirmation == "approved" and status not in {"ready", "completed"}:
            add(issues, "VOICEOVER_HANDOFF_STATUS_INVALID", "voiceover_handoff.status", "approved Studio state requires a ready or completed handoff")
        if status in {"ready", "completed"} and handoff.get("subject_hint") == "requires_user_selection":
            add(issues, "VOICEOVER_PROFILE_UNRESOLVED", "voiceover_handoff.subject_hint", "select a supported subject or explicit speaker before handoff")

    pages = data.get("pages")
    if not isinstance(pages, list) or not pages:
        add(issues, "PAGES_MISSING", "pages", "pages must be a non-empty array")
        return issues
    for index, page in enumerate(pages):
        validate_page(page, index, issues)
        if isinstance(page, dict):
            timeline = page.get("remotion_timeline")
            confirmation = remotion.get("studio_confirmation") if isinstance(remotion, dict) else None
            if isinstance(timeline, dict) and timeline.get("audio_src") and confirmation != "approved":
                add(issues, "PRECONFIRM_AUDIO_FORBIDDEN", f"pages[{index}].remotion_timeline.audio_src", "audio cannot be added before Studio confirmation")

    sequences = [page.get("sequence") for page in pages if isinstance(page, dict)]
    if sequences != list(range(1, len(pages) + 1)):
        add(issues, "PAGE_SEQUENCE_INVALID", "pages", "page sequence must be contiguous, ordered, and start at 1")
    page_ids = [page.get("page_id") for page in pages if isinstance(page, dict)]
    if len(page_ids) != len(set(page_ids)):
        add(issues, "PAGE_ID_DUPLICATE", "pages", "page IDs must be unique")
    studio_names = [page.get("studio_sequence_name") for page in pages if isinstance(page, dict)]
    if len(studio_names) != len(set(studio_names)):
        add(issues, "STUDIO_SEQUENCE_NAME_DUPLICATE", "pages", "Studio sequence names must be unique")

    timelines = [page.get("remotion_timeline") for page in pages if isinstance(page, dict)]
    if len(timelines) == len(pages) and all(isinstance(item, dict) for item in timelines):
        starts = [item.get("start_frame") for item in timelines]
        ends = [item.get("end_frame_exclusive") for item in timelines]
        if starts and starts[0] != 0:
            add(issues, "TIMELINE_START_INVALID", "pages[0].remotion_timeline.start_frame", "first page must start at frame 0")
        for index in range(1, len(timelines)):
            if starts[index] != ends[index - 1]:
                add(issues, "TIMELINE_NOT_CONTIGUOUS", f"pages[{index}].remotion_timeline.start_frame", "page must start at previous exclusive end")
        if isinstance(remotion, dict) and ends and isinstance(ends[-1], int):
            if remotion.get("duration_in_frames") != ends[-1]:
                add(issues, "COMPOSITION_FRAME_TOTAL_MISMATCH", "remotion.duration_in_frames", "composition duration must equal final exclusive end")
            fps = remotion.get("fps")
            if isinstance(fps, int) and fps > 0:
                for index, (page, timeline) in enumerate(zip(pages, timelines)):
                    seconds = page.get("duration_seconds") if isinstance(page, dict) else None
                    frames = timeline.get("duration_in_frames")
                    if isinstance(seconds, (int, float)) and isinstance(frames, int):
                        if abs(frames - round(seconds * fps)) > 1:
                            add(issues, "PAGE_SECONDS_FRAMES_MISMATCH", f"pages[{index}].remotion_timeline.duration_in_frames", "page seconds and Remotion frames disagree")

    project = data.get("project")
    if isinstance(project, dict) and isinstance(project.get("target_duration_seconds"), (int, float)):
        durations = [page.get("duration_seconds") for page in pages if isinstance(page, dict)]
        if all(isinstance(value, (int, float)) for value in durations):
            actual = sum(durations)
            target = project["target_duration_seconds"]
            tolerance = max(2.0, target * 0.01)
            if abs(actual - target) > tolerance:
                add(issues, "TOTAL_DURATION_MISMATCH", "project.target_duration_seconds", f"target is {target}s but pages total {actual}s")
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a deep-book-video video-script.json")
    parser.add_argument("script", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.script.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        issues = [Issue("error", "SCRIPT_READ_ERROR", str(args.script), str(exc))]
    else:
        issues = validate_script(data)

    if args.as_json:
        print(json.dumps([issue._asdict() for issue in issues], ensure_ascii=False, indent=2))
    elif issues:
        for issue in issues:
            print(f"{issue.severity.upper()} {issue.code} {issue.path}: {issue.message}")
    else:
        print("OK: video script satisfies deep-book-video structural contracts")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
