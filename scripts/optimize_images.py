#!/usr/bin/env python3
"""Create safe WebP derivatives for oversized JPEG and PNG source images.

The originals are never deleted or overwritten. By default only source roots
such as static/images and media are scanned; generated staticfiles are excluded.

Examples:
    python scripts/optimize_images.py --dry-run
    python scripts/optimize_images.py --min-kb 50 --max-dimension 1600 --quality 82
    python scripts/optimize_images.py --root static/images --root media --manifest image-optimization.json
    python scripts/optimize_images.py --force
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

BASE_DIR = Path(__file__).resolve().parents[1]
RASTER_EXTENSIONS = {".jpg", ".jpeg", ".png"}
DEFAULT_ROOTS = [BASE_DIR / "static" / "images", BASE_DIR / "media"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", type=Path, help="Source directory; repeatable (default: static/images and media)")
    parser.add_argument("--min-kb", type=float, default=50, help="Only process files at or above this size")
    parser.add_argument("--max-dimension", type=int, default=1600, help="Maximum width or height; never upscales")
    parser.add_argument("--quality", type=int, default=82, help="WebP quality from 1 to 100")
    parser.add_argument("--method", type=int, default=6, choices=range(0, 7), help="WebP encoder effort, 0 through 6")
    parser.add_argument("--force", action="store_true", help="Replace an existing WebP derivative")
    parser.add_argument("--dry-run", action="store_true", help="Report planned work without writing WebP files")
    parser.add_argument("--manifest", type=Path, default=BASE_DIR / "image-optimization-manifest.json", help="JSON manifest output path")
    parser.add_argument("--csv", type=Path, help="Optional CSV manifest output path")
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def process_one(source: Path, args: argparse.Namespace) -> dict:
    target = source.with_suffix(".webp")
    before = source.stat().st_size
    result = {
        "source": source.relative_to(BASE_DIR).as_posix(),
        "output": target.relative_to(BASE_DIR).as_posix(),
        "source_bytes": before,
        "source_kb": round(before / 1024, 2),
        "source_sha256": sha256(source),
        "status": "planned" if args.dry_run else "converted",
        "output_bytes": None,
        "output_kb": None,
        "saving_bytes": None,
        "saving_percent": None,
        "source_dimensions": None,
        "output_dimensions": None,
        "mode": None,
        "error": None,
    }
    try:
        with Image.open(source) as original:
            image = ImageOps.exif_transpose(original)
            result["source_dimensions"] = [image.width, image.height]
            result["mode"] = image.mode
            if max(image.size) > args.max_dimension:
                image.thumbnail((args.max_dimension, args.max_dimension), Image.Resampling.LANCZOS)
            result["output_dimensions"] = [image.width, image.height]
            if args.dry_run:
                if target.exists() and not args.force:
                    result["status"] = "skipped-existing"
                return result
            if target.exists() and not args.force:
                result["status"] = "skipped-existing"
                result["output_bytes"] = target.stat().st_size
                result["output_kb"] = round(result["output_bytes"] / 1024, 2)
                return result
            target.parent.mkdir(parents=True, exist_ok=True)
            # Preserve alpha where present; WebP supports RGBA and RGB.
            if image.mode not in {"RGB", "RGBA"}:
                image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
            with tempfile.NamedTemporaryFile(prefix=target.stem + ".", suffix=".webp", dir=target.parent, delete=False) as temp:
                temporary = Path(temp.name)
            try:
                image.save(temporary, "WEBP", quality=args.quality, method=args.method, lossless=False)
                os.replace(temporary, target)
            finally:
                if temporary.exists():
                    temporary.unlink()
            output_bytes = target.stat().st_size
            result["output_bytes"] = output_bytes
            result["output_kb"] = round(output_bytes / 1024, 2)
            result["saving_bytes"] = before - output_bytes
            result["saving_percent"] = round((before - output_bytes) * 100 / before, 2)
            result["output_sha256"] = sha256(target)
    except Exception as exc:
        result["status"] = "error"
        result["error"] = str(exc)
    return result


def write_outputs(results: list[dict], args: argparse.Namespace) -> None:
    summary = {
        "dry_run": args.dry_run,
        "min_kb": args.min_kb,
        "max_dimension": args.max_dimension,
        "quality": args.quality,
        "method": args.method,
        "candidate_count": len(results),
        "converted_count": sum(r["status"] == "converted" for r in results),
        "skipped_count": sum(r["status"].startswith("skipped") for r in results),
        "error_count": sum(r["status"] == "error" for r in results),
        "source_bytes": sum(r["source_bytes"] for r in results),
        "output_bytes": sum(r["output_bytes"] or 0 for r in results if r["status"] == "converted"),
        "saving_bytes": sum(r["saving_bytes"] or 0 for r in results if r["status"] == "converted"),
        "files": results,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = sorted({key for row in results for key in row})
        with args.csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    print(json.dumps(summary, indent=2))


def main() -> int:
    args = parse_args()
    if not 1 <= args.quality <= 100:
        raise SystemExit("--quality must be between 1 and 100")
    if args.min_kb < 0 or args.max_dimension < 1:
        raise SystemExit("--min-kb must be non-negative and --max-dimension must be positive")
    roots = [((root if root.is_absolute() else BASE_DIR / root).resolve()) for root in (args.root or DEFAULT_ROOTS)]
    candidates = []
    for root in roots:
        if not root.exists():
            continue
        candidates.extend(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in RASTER_EXTENSIONS and path.stat().st_size >= args.min_kb * 1024)
    results = [process_one(path, args) for path in sorted(set(candidates))]
    write_outputs(results, args)
    return 1 if any(row["status"] == "error" for row in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
