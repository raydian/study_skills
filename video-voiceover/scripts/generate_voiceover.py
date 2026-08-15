#!/usr/bin/env python3
"""Generate subject-specific voiceover audio for high-school video projects."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
import urllib.error
import urllib.request
from collections import OrderedDict
from pathlib import Path


VOICE_PROFILES = {
    "语文": {
        "speaker": "zh_male_yuanboxiaoshu_uranus_bigtts",
        "speechRate": -2,
        "pauseAfterMs": 260,
        "recitationRate": -14,
        "recitationPauseAfterMs": 420,
        "loudnessRate": 0,
    },
    "数学": {"speaker": "zh_female_yingyujiaoxue_uranus_bigtts", "speechRate": 2, "pauseAfterMs": 180, "loudnessRate": 0},
    "英语": {"speaker": "zh_male_yuanboxiaoshu_uranus_bigtts", "speechRate": 0, "pauseAfterMs": 220, "loudnessRate": 0},
    "物理": {"speaker": "zh_female_yingyujiaoxue_uranus_bigtts", "speechRate": 1, "pauseAfterMs": 200, "loudnessRate": 0},
    "化学": {"speaker": "zh_female_yingyujiaoxue_uranus_bigtts", "speechRate": 1, "pauseAfterMs": 210, "loudnessRate": 0},
    "生物": {"speaker": "zh_female_yingyujiaoxue_uranus_bigtts", "speechRate": 0, "pauseAfterMs": 220, "loudnessRate": 0},
    "历史": {"speaker": "zh_male_yuanboxiaoshu_uranus_bigtts", "speechRate": -1, "pauseAfterMs": 240, "loudnessRate": 0},
    "地理": {"speaker": "zh_male_yuanboxiaoshu_uranus_bigtts", "speechRate": 0, "pauseAfterMs": 220, "loudnessRate": 0},
    "精读图书": {"speaker": "zh_male_yuanboxiaoshu_uranus_bigtts", "speechRate": 0, "pauseAfterMs": 240, "loudnessRate": 0},
    "精读图书视频讲解": {"speaker": "zh_male_yuanboxiaoshu_uranus_bigtts", "speechRate": 0, "pauseAfterMs": 240, "loudnessRate": 0},
}

SCRIPT_CANDIDATES = [
    "voiceover/voiceover_marks.json",
    "口播稿.md",
    "配音稿.md",
    "audio_script.md",
    "script.md",
]


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def require_binary(name: str) -> None:
    if not shutil.which(name):
        raise SystemExit(f"Missing required binary: {name}")


def infer_subject(video_dir: Path) -> str:
    parts = list(video_dir.parts)
    for i, part in enumerate(parts):
        if part == "video" and i + 1 < len(parts):
            return parts[i + 1]
    for part in reversed(parts):
        if part in VOICE_PROFILES:
            return part
    return "语文"


def find_script(video_dir: Path) -> Path:
    for candidate in SCRIPT_CANDIDATES:
        path = video_dir / candidate
        if path.exists():
            return path
    raise SystemExit(
        "No script supplied and no default script file found. "
        "Pass --script or create 口播稿.md / 配音稿.md / voiceover/voiceover_marks.json."
    )


def split_text(text: str, max_len: int = 90) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    pieces = re.split(r"(?<=[。！？；.!?;])", text)
    result: list[str] = []
    buf = ""
    for piece in pieces:
        piece = piece.strip()
        if not piece:
            continue
        if len(buf) + len(piece) <= max_len:
            buf += piece
            continue
        if buf:
            result.append(buf)
        if len(piece) <= max_len:
            buf = piece
        else:
            result.extend(piece[i : i + max_len] for i in range(0, len(piece), max_len))
            buf = ""
    if buf:
        result.append(buf)
    return result


def parse_markdown(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    marks: list[dict] = []
    scene = "01"
    scene_index = 1
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        paragraph = " ".join(x.strip() for x in buffer if x.strip()).strip()
        buffer = []
        for segment in split_text(paragraph):
            marks.append({"scene": scene, "text": segment})

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        if line.startswith("#"):
            flush()
            title = line.lstrip("#").strip()
            match = re.search(r"(\d{1,3})", title)
            if match:
                scene = f"{int(match.group(1)):02d}"
            else:
                scene_index += 1
                scene = f"{scene_index:02d}"
            continue
        if re.match(r"^[-*+]\s+", line):
            flush()
            item = re.sub(r"^[-*+]\s+", "", line).strip()
            for segment in split_text(item):
                marks.append({"scene": scene, "text": segment})
            continue
        buffer.append(line)
    flush()
    return marks


def load_script(path: Path) -> list[dict]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = data.get("segments") or data.get("marks") or data.get("items")
        if not isinstance(data, list):
            raise SystemExit("JSON script must be a list, or an object with segments/marks/items.")
        return [dict(item) if isinstance(item, dict) else {"text": str(item)} for item in data]
    return parse_markdown(path)


def is_recitation(mark: dict, subject: str) -> bool:
    if subject != "语文":
        return False
    tone = str(mark.get("tone", ""))
    text = str(mark.get("text", ""))
    scene = str(mark.get("scene", ""))
    if re.search(r"朗读|诵读|原文|古诗|文言|诗歌", tone + scene):
        return True
    return bool(len(text) <= 38 and re.search(r"[，。！？；]", text) and not re.search(r"我们|这一|这里|说明|表现|注意", text))


def normalize_marks(raw_marks: list[dict], subject: str, speaker_override: str | None) -> list[dict]:
    profile = VOICE_PROFILES.get(subject, VOICE_PROFILES["语文"])
    scene_counts: dict[str, int] = {}
    marks: list[dict] = []
    for index, mark in enumerate(raw_marks, start=1):
        text = str(mark.get("text") or mark.get("content") or "").strip()
        if not text:
            continue
        scene = str(mark.get("scene") or mark.get("page") or "01").strip()
        if scene.isdigit():
            scene = f"{int(scene):02d}"
        scene_counts[scene] = scene_counts.get(scene, 0) + 1
        recitation = is_recitation(mark, subject)
        speech_rate = mark.get("speechRate", mark.get("speech_rate"))
        if speech_rate is None:
            speech_rate = profile.get("recitationRate" if recitation else "speechRate", 0)
        pause = mark.get("pauseAfterMs", mark.get("pause_after_ms"))
        if pause is None:
            pause = profile.get("recitationPauseAfterMs" if recitation else "pauseAfterMs", 220)
        marks.append(
            {
                "id": str(mark.get("id") or f"{scene}-{scene_counts[scene]:03d}"),
                "scene": scene,
                "text": text,
                "subtitle": str(mark.get("subtitle") or text),
                "tone": str(mark.get("tone") or ("正式朗读" if recitation else "")),
                "speaker": speaker_override or str(mark.get("speaker") or profile["speaker"]),
                "speechRate": int(speech_rate),
                "loudnessRate": int(mark.get("loudnessRate", mark.get("loudness_rate", profile.get("loudnessRate", 0)))),
                "pauseAfterMs": int(pause),
                "order": index,
            }
        )
    if not marks:
        raise SystemExit("No voiceover text found in script.")
    return marks


def tts_segment(
    text: str,
    speaker: str,
    api_key: str,
    api_base: str,
    resource_id: str,
    sample_rate: int,
    audio_format: str,
    bit_rate: int,
    speech_rate: int,
    loudness_rate: int,
) -> bytes:
    endpoint = api_base.rstrip("/") + "/api/v3/tts/unidirectional/sse"
    body = {
        "user": {"uid": "codex-video-voiceover"},
        "req_params": {
            "text": text,
            "speaker": speaker,
            "audio_params": {
                "format": audio_format,
                "sample_rate": sample_rate,
                "speech_rate": speech_rate,
                "loudness_rate": loudness_rate,
                "bit_rate": bit_rate,
            },
            "additions": json.dumps(
                {"disable_markdown_filter": False, "enable_latex_tn": True, "enable_english": True},
                ensure_ascii=False,
            ),
        },
    }
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key,
        "X-Api-Resource-Id": resource_id,
        "X-Api-Request-Id": str(uuid.uuid4()),
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    audio = bytearray()
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            for raw in response:
                line = raw.decode("utf-8", errors="ignore").strip()
                if not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if not payload or payload == "[DONE]":
                    continue
                event = json.loads(payload)
                data = event.get("data") or event.get("audio") or ""
                if data:
                    audio.extend(base64.b64decode(data))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")[:500]
        raise RuntimeError(f"TTS request failed with HTTP {exc.code}: {detail}") from exc
    if not audio:
        raise RuntimeError("TTS returned no audio bytes.")
    return bytes(audio)


def probe_duration(path: Path) -> float:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
    )
    return float(result.stdout.strip())


def silence_file(work_dir: Path, pause_ms: int, sample_rate: int) -> Path:
    pause_ms = max(0, int(pause_ms))
    path = work_dir / f"silence_{pause_ms}.mp3"
    if path.exists():
        return path
    duration = max(pause_ms / 1000, 0.001)
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"anullsrc=r={sample_rate}:cl=mono",
            "-t",
            f"{duration:.3f}",
            "-q:a",
            "9",
            "-acodec",
            "libmp3lame",
            str(path),
        ]
    )
    return path


def concat_audio(files: list[Path], output: Path, sample_rate: int, bit_rate: int) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        list_path = Path(td) / "concat.txt"
        lines = [f"file '{str(file.resolve()).replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'" for file in files]
        list_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_path),
                "-ar",
                str(sample_rate),
                "-ac",
                "1",
                "-b:a",
                str(bit_rate),
                str(output),
            ]
        )


def read_timeline_scenes(path: Path) -> list[str]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    scenes = data.get("scenes", []) if isinstance(data, dict) else []
    return [str(scene.get("id", "")).strip() for scene in scenes if str(scene.get("id", "")).strip()]


def build_audio_timeline(marks: list[dict], fps: int, scene_order: list[str]) -> dict:
    ordered = OrderedDict((scene, []) for scene in scene_order)
    for mark in marks:
        ordered.setdefault(mark["scene"], []).append(mark)
    scenes = []
    subtitles = []
    global_cursor = 0.0
    for scene_id, scene_marks in ordered.items():
        if not scene_marks:
            continue
        scene_start = global_cursor
        local_cursor = 0.0
        scene_subtitles = []
        for mark in scene_marks:
            start = local_cursor
            end = local_cursor + float(mark["audioSeconds"])
            subtitle = {
                "id": mark["id"],
                "scene": scene_id,
                "text": mark["subtitle"],
                "start": round(scene_start + start, 3),
                "end": round(scene_start + end, 3),
                "startFrame": round((scene_start + start) * fps),
                "endFrame": round((scene_start + end) * fps),
            }
            scene_subtitles.append(subtitle)
            subtitles.append(subtitle)
            local_cursor = end + mark["pauseAfterMs"] / 1000
        scene_end = scene_start + local_cursor
        start_frame = round(scene_start * fps)
        end_frame = round(scene_end * fps)
        duration_frames = max(1, end_frame - start_frame)
        scenes.append(
            {
                "id": scene_id,
                "durationFrames": duration_frames,
                "durationSeconds": round(local_cursor, 3),
                "subtitles": scene_subtitles,
            }
        )
        global_cursor = scene_end
    return {
        "fps": fps,
        "totalSeconds": round(global_cursor, 3),
        "totalFrames": round(global_cursor * fps),
        "scenes": scenes,
        "subtitles": subtitles,
    }


def sync_remotion(video_dir: Path, audio_timeline: dict) -> None:
    timeline_path = video_dir / "src" / "timeline.json"
    subtitles_path = video_dir / "src" / "data" / "subtitles.ts"
    if timeline_path.exists():
        try:
            timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Cannot parse {timeline_path}: {exc}") from exc
        scene_durations = {scene["id"]: scene["durationFrames"] for scene in audio_timeline["scenes"]}
        if isinstance(timeline, dict) and isinstance(timeline.get("scenes"), list):
            for scene in timeline["scenes"]:
                scene_id = str(scene.get("id", ""))
                if scene_id in scene_durations:
                    scene["durationFrames"] = scene_durations[scene_id]
            known = {str(scene.get("id", "")) for scene in timeline["scenes"]}
            for scene in audio_timeline["scenes"]:
                if scene["id"] not in known:
                    timeline["scenes"].append({"id": scene["id"], "durationFrames": scene["durationFrames"]})
            timeline["totalFrames"] = audio_timeline["totalFrames"]
        timeline_path.write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if subtitles_path.parent.exists():
        subtitles_path.write_text(
            "export const subtitles = "
            + json.dumps(audio_timeline["subtitles"], ensure_ascii=False, indent=2)
            + " as const;\n",
            encoding="utf-8",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video-dir", required=True, type=Path)
    parser.add_argument("--script", type=Path)
    parser.add_argument("--subject")
    parser.add_argument("--speaker")
    parser.add_argument("--api-key-env", default="MODEL_SPEECH_API_KEY")
    parser.add_argument("--api-base", default=os.environ.get("MODEL_SPEECH_API_BASE", "https://openspeech.bytedance.com"))
    parser.add_argument("--resource-id", default=os.environ.get("MODEL_SPEECH_TTS_RESOURCE_ID", "seed-tts-2.0"))
    parser.add_argument("--sample-rate", type=int, default=24000)
    parser.add_argument("--format", default="mp3")
    parser.add_argument("--bit-rate", type=int, default=64000)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--sync-remotion", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    video_dir = args.video_dir.resolve()
    script_path = (args.script or find_script(video_dir)).resolve()
    subject = args.subject or infer_subject(video_dir)
    marks = normalize_marks(load_script(script_path), subject, args.speaker)

    voiceover_dir = video_dir / "voiceover"
    segments_dir = voiceover_dir / "segments"
    public_audio = video_dir / "public" / "audio" / "voiceover.mp3"
    voiceover_dir.mkdir(parents=True, exist_ok=True)
    segments_dir.mkdir(parents=True, exist_ok=True)

    marks_path = voiceover_dir / "voiceover_marks.json"
    marks_path.write_text(json.dumps(marks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.dry_run:
        print(json.dumps({"subject": subject, "segments": len(marks), "marks": str(marks_path)}, ensure_ascii=False, indent=2))
        return 0

    require_binary("ffmpeg")
    require_binary("ffprobe")
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise SystemExit(f"{args.api_key_env} is not set.")

    concat_files: list[Path] = []
    with tempfile.TemporaryDirectory() as td:
        silence_dir = Path(td)
        for i, mark in enumerate(marks, start=1):
            output = segments_dir / f"{i:03d}-{mark['id']}.{args.format}"
            if args.force or not output.exists():
                eprint(f"Synthesizing {i}/{len(marks)} {mark['id']}")
                audio = tts_segment(
                    mark["text"],
                    mark["speaker"],
                    api_key,
                    args.api_base,
                    args.resource_id,
                    args.sample_rate,
                    args.format,
                    args.bit_rate,
                    mark["speechRate"],
                    mark["loudnessRate"],
                )
                output.write_bytes(audio)
                time.sleep(0.12)
            mark["audioFile"] = str(output.relative_to(video_dir))
            mark["audioSeconds"] = round(probe_duration(output), 3)
            concat_files.append(output)
            if mark["pauseAfterMs"] > 0:
                concat_files.append(silence_file(silence_dir, mark["pauseAfterMs"], args.sample_rate))
        concat_audio(concat_files, public_audio, args.sample_rate, args.bit_rate)

    scene_order = read_timeline_scenes(video_dir / "src" / "timeline.json")
    audio_timeline = build_audio_timeline(marks, args.fps, scene_order)
    audio_timeline["audioFile"] = str(public_audio.relative_to(video_dir))
    audio_timeline["subject"] = subject
    audio_timeline["speakerDefaults"] = sorted({mark["speaker"] for mark in marks})

    marks_path.write_text(json.dumps(marks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    timeline_path = voiceover_dir / "audio_timeline.json"
    timeline_path.write_text(json.dumps(audio_timeline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.sync_remotion:
        sync_remotion(video_dir, audio_timeline)

    print(
        json.dumps(
            {
                "subject": subject,
                "segments": len(marks),
                "audio": str(public_audio),
                "durationSeconds": round(probe_duration(public_audio), 3),
                "marks": str(marks_path),
                "timeline": str(timeline_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
