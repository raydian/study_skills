#!/usr/bin/env python3
"""image-gen-multi 产物校验。

检查生成的图片文件：存在性、非空、格式（magic bytes）、尺寸（可选，用 PIL 或 file 命令）。

用法：
    python3 verify_image.py path/to/image.png
    python3 verify_image.py path/to/output/          # 校验目录下所有图片
    python3 verify_image.py path/to/image.png --strict
"""

import argparse
import json
import struct
import sys
from pathlib import Path

# 常见图片格式 magic bytes 表
MAGIC = {
    ".png": (b"\x89PNG\r\n\x1a\n", "PNG"),
    ".jpg": (b"\xff\xd8\xff", "JPEG"),
    ".jpeg": (b"\xff\xd8\xff", "JPEG"),
    ".webp": (b"RIFF", "WEBP"),
    ".gif": (b"GIF8", "GIF"),
    ".bmp": (b"BM", "BMP"),
}


def check_format(path: Path) -> tuple[bool, str]:
    """用 magic bytes 校验格式与扩展名是否匹配。"""
    with open(path, "rb") as f:
        head = f.read(12)
    ext = path.suffix.lower()
    if ext not in MAGIC:
        return True, f"未知扩展名 {ext}（跳过格式校验）"
    magic, name = MAGIC[ext]
    if ext == ".webp":
        ok = head.startswith(b"RIFF") and head[8:12] == b"WEBP"
    else:
        ok = head.startswith(magic)
    return (ok, f"{name} 格式正确") if ok else (False, f"格式不匹配：扩展名 {ext} 但内容非 {name}")


def read_png_size(path: Path) -> tuple[int, int] | None:
    """解析 PNG IHDR 获取宽高。"""
    try:
        with open(path, "rb") as f:
            head = f.read(26)
        if not head.startswith(b"\x89PNG\r\n\x1a\n"):
            return None
        w, h = struct.unpack(">II", head[16:24])
        return w, h
    except Exception:
        return None


def check_size(path: Path) -> str | None:
    """返回尺寸描述（仅 PNG/JPEG）。"""
    if path.suffix.lower() == ".png":
        size = read_png_size(path)
        return f"{size[0]}x{size[1]}" if size else None
    if path.suffix.lower() in (".jpg", ".jpeg"):
        # 简易 JPEG SOF 解析
        try:
            with open(path, "rb") as f:
                data = f.read(64 * 1024)
            if not data.startswith(b"\xff\xd8"):
                return None
            i = 2
            while i < len(data):
                if data[i] != 0xFF:
                    i += 1
                    continue
                marker = data[i + 1]
                if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    h, w = struct.unpack(">HH", data[i + 5:i + 9])
                    return f"{w}x{h}"
                seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
                i += 2 + seg_len
        except Exception:
            return None
    return None


def verify_file(path: Path, strict: bool = False) -> dict:
    result = {"path": str(path), "ok": True, "issues": []}

    if not path.exists():
        return {"path": str(path), "ok": False, "issues": ["文件不存在"]}

    stat = path.stat()
    if stat.st_size == 0:
        return {"path": str(path), "ok": False, "issues": ["文件为空"]}
    result["size_bytes"] = stat.st_size
    result["size_human"] = f"{stat.st_size / 1024:.1f} KB" if stat.st_size < 1024 * 1024 else f"{stat.st_size / 1024 / 1024:.2f} MB"

    fmt_ok, fmt_msg = check_format(path)
    if not fmt_ok:
        result["ok"] = False
        result["issues"].append(fmt_msg)
    else:
        result["format"] = fmt_msg

    dims = check_size(path)
    if dims:
        result["dimensions"] = dims

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="image-gen-multi 产物校验")
    parser.add_argument("target", help="图片文件或目录")
    parser.add_argument("--strict", action="store_true", help="严格模式：任何问题都返回非零退出码")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    target = Path(args.target)
    files = [target] if target.is_file() else sorted(target.glob("*")) if target.is_dir() else []
    files = [f for f in files if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")]

    if not files:
        print(f"未找到图片文件: {target}", file=sys.stderr)
        sys.exit(2)

    results = [verify_file(f, args.strict) for f in files]
    all_ok = all(r["ok"] for r in results)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            status = "OK " if r["ok"] else "FAIL"
            extra = []
            if "dimensions" in r:
                extra.append(r["dimensions"])
            if "size_human" in r:
                extra.append(r["size_human"])
            print(f"[{status}] {r['path']} {' '.join(extra)}")
            for issue in r["issues"]:
                print(f"       - {issue}")
        print(f"\n总计 {len(results)} 个文件，{'全部通过' if all_ok else '存在失败'}")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
