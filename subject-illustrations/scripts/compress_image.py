#!/usr/bin/env python3
"""Compress an image to WebP/JPEG/PNG, targeting <= 1MB when possible."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required: python3 -m pip install Pillow") from exc


MAX_BYTES = 1_000_000


def save_candidate(img: Image.Image, out: Path, quality: int, max_width: int | None) -> None:
    work = img
    if max_width and img.width > max_width:
        ratio = max_width / img.width
        size = (max_width, max(1, round(img.height * ratio)))
        work = img.resize(size, Image.Resampling.LANCZOS)
    if out.suffix.lower() == ".png":
        work.save(out, optimize=True)
    elif out.suffix.lower() in {".jpg", ".jpeg"}:
        work.convert("RGB").save(out, quality=quality, optimize=True, progressive=True)
    else:
        work.save(out, format="WEBP", quality=quality, method=6)


def compress(input_path: Path, output_path: Path, target: int) -> tuple[Path, int]:
    img = Image.open(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    widths = [None, 1800, 1500, 1200, 1000, 800]
    qualities = [90, 84, 78, 72, 66, 60, 54, 48, 42]

    best_path = output_path
    best_size = None
    for width in widths:
        for quality in qualities:
            save_candidate(img, output_path, quality, width)
            size = output_path.stat().st_size
            if best_size is None or size < best_size:
                best_size = size
            if size <= target:
                return output_path, size

    return best_path, os.path.getsize(best_path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--target-bytes", type=int, default=MAX_BYTES)
    args = parser.parse_args()

    output = args.output
    if output is None:
        output = args.input.with_suffix(".webp")
    path, size = compress(args.input, output, args.target_bytes)
    print(f"{path} {size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
