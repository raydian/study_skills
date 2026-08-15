import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_video_script.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_video_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def valid_page():
    return {
        "page_id": "P001",
        "page_name": "开场：看不见的规则",
        "studio_sequence_name": "P001｜开场：看不见的规则",
        "sequence": 1,
        "page_type": "hook",
        "page_purpose": "用反常识问题建立全片认知张力。",
        "thesis_relation": "opens",
        "content_route": {
            "primary_role": "argument",
            "depth_engine": "argument-assumption",
            "reasoning_move": "把常见归因改写为作者真正追问的问题。",
        },
        "claim": "作者把部分失败重新解释为结构性规则对行动边界的提前限定。",
        "knowledge_unit_ids": ["ku-claim-0001"],
        "source_refs": [{"ref": "ch01-p003", "relation": "states"}],
        "attribution": "author_claim",
        "evidence_quality": {
            "strength": "moderate",
            "directness": "direct",
            "limitations": ["开场仅提出问题，后页展开证据。"],
        },
        "subtitle": {
            "text": "真正限制我们的，也许不是能力，而是看不见的规则。",
            "lines": ["真正限制我们的，也许不是能力", "而是看不见的规则"],
            "placement": "lower_third",
            "font_family": "Noto Sans CJK SC",
            "font_size_px": 72,
            "font_weight": 700,
            "text_color": "#FFFFFF",
            "background_treatment": "solid_scrim_72pct",
            "contrast_ratio_target": 7.0,
        },
        "voiceover": {
            "text": "我们通常把失败归因于能力不足，但作者追问的是：是否有一套看不见的规则，提前划定了行动边界？",
            "delivery": "克制、清晰，在问句前短暂停顿。",
        },
        "duration_seconds": 10,
        "remotion_timeline": {
            "start_frame": 0,
            "duration_in_frames": 300,
            "end_frame_exclusive": 300,
            "image_src": "images/p001.png",
        },
        "visual": {
            "function": "symbolize",
            "image_prompt": {
                "subject": "一位人物站在由透明边界切割的空间中",
                "setting": "抽象但可信的现代城市边缘",
                "action": "人物试探性地伸手触碰不可见边界",
                "era_culture": "当代中国城市语境，服饰与建筑准确",
                "art_direction": "电影感写实摄影，避免概念海报俗套",
                "palette": "深蓝灰背景配一处暖色人物光",
                "lighting": "侧逆光勾勒轮廓，字幕区保持均匀暗部",
                "camera": "35mm 中远景，视线高度平视",
                "composition": "人物置于右侧三分线，左下至中下留连续纯净暗区",
                "symbolic_elements": ["透明边界", "远处开放通道"],
                "continuity": "沿用全片深蓝灰与暖色主体的视觉母题",
                "safe_text_area": "画面下方 36% 无人物、无高光、无复杂纹理",
                "realism_constraints": ["手部结构正常", "城市透视正确", "不生成可核验数据"],
                "negative_prompt": "文字、字母、数字、书名、标志、水印、边框、畸形手、杂乱下三分之一",
                "rendered_prompt": "16:9 全屏电影感写实画面：当代中国城市边缘，一位人物站在由透明边界切割的空间中，伸手触碰不可见边界。35mm 平视中远景，人物位于右侧三分线，深蓝灰环境以暖色侧逆光勾勒主体；画面下方 36% 保持连续、均匀、低纹理暗区，禁止人物、高光和复杂物体进入字幕安全区。透明边界与远处开放通道形成克制象征。建筑透视、服饰、手部结构准确。不生成文字、字母、数字、书名、标志、水印、边框或可核验数据。",
            },
            "composition": {
                "focal_point": "右侧人物与透明边界接触处",
                "depth_layers": ["前景暗部", "中景人物", "远景通道"],
                "text_safe_zone": "bottom_36_percent",
                "reading_order": "先人物，再边界，最后字幕",
                "crop_safety": "主体和字幕安全区兼容 16:9 中心裁切",
            },
            "readability": {
                "background_control": "字幕区降细节并压暗",
                "local_contrast": "白字对深色实底",
                "busy_area_avoidance": "字幕区不出现脸、手、边缘线或光源",
                "subtitle_box": "黑色实底 72% 不透明度，内边距不小于一行字高的 0.35 倍",
                "min_font_px": 64,
            },
        },
        "transition": "hard_cut",
    }


def valid_script():
    return {
        "schema_version": 3,
        "project": {
            "title": "示例精读视频",
            "book_title": "示例书",
            "target_audience": "普通成年读者",
            "target_duration_seconds": 10,
            "aspect_ratio": "16:9",
            "resolution": "1920x1080",
            "spoiler_policy": "necessary",
        },
        "global_video_thesis": {
            "statement": "隐形规则常比显性能力更早决定行动边界。",
            "viewer_shift": "从只看个人能力，转向同时观察结构约束。",
            "scope": "仅解释作者讨论的制度与组织场景。",
            "counter_thesis": "个人能动性仍可能改变局部结果。",
        },
        "book_profile": {
            "primary_type": "思想与社会科学",
            "secondary_types": ["案例研究"],
            "knowledge_structure": {"conceptual": 4, "causal": 4, "evidential": 3},
        },
        "narrative_plan": {
            "mode": "question_to_model",
            "arc_steps": ["问题", "模型", "证据", "边界", "综合"],
            "selected_unit_ids": ["ku-claim-0001"],
        },
        "visual_bible": {
            "style": "电影感写实摄影",
            "palette": "深蓝灰与克制暖色",
            "recurring_motifs": ["透明边界", "开放通道"],
            "character_continuity": "同一人物保持年龄、服饰和发型一致",
            "forbidden_elements": ["画内文字", "标志", "水印", "伪造数据图表"],
        },
        "remotion": {
            "engine": "remotion",
            "composition_id": "DeepBookVideo",
            "fps": 30,
            "width": 1920,
            "height": 1080,
            "duration_in_frames": 300,
            "studio_confirmation": "pending",
            "render_policy": "do_not_render",
            "audio_policy": "no_audio_before_studio_confirmation",
            "dependency_policy": "reuse_video_shared_node_modules_symlink",
            "studio_timeline_mode": "explicit_named_sequences",
        },
        "voiceover_handoff": {
            "skill": "video-voiceover",
            "status": "blocked_until_studio_confirmed",
            "script_file": "voiceover-script.json",
            "sync_remotion": True,
            "subject_hint": "历史",
            "render_after_voiceover": False,
            "preview_after_voiceover": True,
        },
        "pages": [valid_page()],
    }


class ValidatorTests(unittest.TestCase):
    def test_valid_script_passes(self):
        validator = load_validator()
        self.assertEqual([], validator.validate_script(valid_script()))

    def test_missing_source_refs_is_blocking(self):
        validator = load_validator()
        data = valid_script()
        data["pages"][0]["source_refs"] = []
        codes = {issue.code for issue in validator.validate_script(data)}
        self.assertIn("PAGE_SOURCE_REFS_MISSING", codes)

    def test_missing_page_claim_is_blocking(self):
        validator = load_validator()
        data = valid_script()
        del data["pages"][0]["claim"]
        codes = {issue.code for issue in validator.validate_script(data)}
        self.assertIn("PAGE_FIELD_MISSING", codes)

    def test_unknown_depth_engine_is_blocking(self):
        validator = load_validator()
        data = valid_script()
        data["pages"][0]["content_route"]["depth_engine"] = "generic-summary"
        codes = {issue.code for issue in validator.validate_script(data)}
        self.assertIn("DEPTH_ENGINE_INVALID", codes)

    def test_studio_sequence_name_must_include_page_number_and_name(self):
        validator = load_validator()
        data = valid_script()
        data["pages"][0]["studio_sequence_name"] = "开场"
        codes = {issue.code for issue in validator.validate_script(data)}
        self.assertIn("STUDIO_SEQUENCE_NAME_INVALID", codes)

    def test_unknown_narrative_mode_is_blocking(self):
        validator = load_validator()
        data = valid_script()
        data["narrative_plan"]["mode"] = "chapter-by-chapter"
        codes = {issue.code for issue in validator.validate_script(data)}
        self.assertIn("NARRATIVE_MODE_INVALID", codes)

    def test_non_remotion_engine_is_blocking(self):
        validator = load_validator()
        data = valid_script()
        data["remotion"]["engine"] = "ffmpeg-slideshow"
        codes = {issue.code for issue in validator.validate_script(data)}
        self.assertIn("REMOTION_ENGINE_REQUIRED", codes)

    def test_audio_asset_before_studio_confirmation_is_blocking(self):
        validator = load_validator()
        data = valid_script()
        data["pages"][0]["remotion_timeline"]["audio_src"] = "audio/p001.wav"
        codes = {issue.code for issue in validator.validate_script(data)}
        self.assertIn("PRECONFIRM_AUDIO_FORBIDDEN", codes)

    def test_render_configuration_is_blocking(self):
        validator = load_validator()
        data = valid_script()
        data["remotion"]["output_file"] = "out/deep-book-video.mp4"
        codes = {issue.code for issue in validator.validate_script(data)}
        self.assertIn("RENDER_CONFIGURATION_FORBIDDEN", codes)

    def test_voiceover_handoff_must_wait_for_studio(self):
        validator = load_validator()
        data = valid_script()
        data["voiceover_handoff"]["status"] = "ready"
        codes = {issue.code for issue in validator.validate_script(data)}
        self.assertIn("VOICEOVER_HANDOFF_PREMATURE", codes)

    def test_approved_studio_allows_ready_voiceover_handoff(self):
        validator = load_validator()
        data = valid_script()
        data["remotion"]["studio_confirmation"] = "approved"
        data["voiceover_handoff"]["status"] = "ready"
        self.assertEqual([], validator.validate_script(data))

    def test_unresolved_voice_profile_blocks_ready_handoff(self):
        validator = load_validator()
        data = valid_script()
        data["remotion"]["studio_confirmation"] = "approved"
        data["voiceover_handoff"]["status"] = "ready"
        data["voiceover_handoff"]["subject_hint"] = "requires_user_selection"
        codes = {issue.code for issue in validator.validate_script(data)}
        self.assertIn("VOICEOVER_PROFILE_UNRESOLVED", codes)

    def test_page_frame_math_must_be_exact(self):
        validator = load_validator()
        data = valid_script()
        data["pages"][0]["remotion_timeline"]["end_frame_exclusive"] = 299
        codes = {issue.code for issue in validator.validate_script(data)}
        self.assertIn("PAGE_FRAME_MATH_INVALID", codes)

    def test_composition_frame_total_must_match_pages(self):
        validator = load_validator()
        data = valid_script()
        data["remotion"]["duration_in_frames"] = 299
        codes = {issue.code for issue in validator.validate_script(data)}
        self.assertIn("COMPOSITION_FRAME_TOTAL_MISMATCH", codes)

    def test_seconds_and_frames_must_agree(self):
        validator = load_validator()
        data = valid_script()
        data["pages"][0]["duration_seconds"] = 9
        data["project"]["target_duration_seconds"] = 9
        codes = {issue.code for issue in validator.validate_script(data)}
        self.assertIn("PAGE_SECONDS_FRAMES_MISMATCH", codes)

    def test_image_prompt_cannot_be_used_as_evidence(self):
        validator = load_validator()
        data = valid_script()
        data["pages"][0]["source_refs"] = [{"ref": "ai-image-p001", "relation": "illustrates"}]
        codes = {issue.code for issue in validator.validate_script(data)}
        self.assertIn("AI_IMAGE_AS_EVIDENCE", codes)

    def test_small_subtitle_is_blocking(self):
        validator = load_validator()
        data = valid_script()
        data["pages"][0]["subtitle"]["font_size_px"] = 42
        codes = {issue.code for issue in validator.validate_script(data)}
        self.assertIn("SUBTITLE_TOO_SMALL", codes)

    def test_cli_returns_nonzero_for_invalid_script(self):
        validator = load_validator()
        data = valid_script()
        data["pages"][0]["transition"] = "pan_and_zoom"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "video-script.json"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                self.assertEqual(1, validator.main([str(path)]))


if __name__ == "__main__":
    unittest.main()
