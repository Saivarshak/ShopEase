#!/usr/bin/env python3
"""Measure local Django response sizes without contacting production.

Examples:
    python scripts/bandwidth_audit.py
    python scripts/bandwidth_audit.py --repeat 20 --fail-if-total-mb 25
    python scripts/bandwidth_audit.py --path / --path /men/ --repeat 5
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
DEFAULT_PATHS = [
    "/",
    "/mens/",
    "/womens/",
    "/kids/",
    "/static/images/shirt.webp",
    "/static/images/logo1.webp",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", action="append", dest="paths", help="Path to request; repeat for multiple paths")
    parser.add_argument("--repeat", type=int, default=1, help="Requests per path (default: 1)")
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    parser.add_argument("--fail-if-total-mb", type=float, help="Exit 2 when the run exceeds this total")
    parser.add_argument("--fail-if-route-kb", type=float, help="Exit 2 when any route exceeds this total")
    return parser.parse_args()


def configure_isolated_database() -> tempfile.TemporaryDirectory:
    temp_dir = tempfile.TemporaryDirectory(prefix="shopease-bandwidth-", ignore_cleanup_errors=True)
    source = BASE_DIR / "db.sqlite3"
    target = Path(temp_dir.name) / "db.sqlite3"
    if source.exists():
        shutil.copy2(source, target)
    else:
        target.touch()
    os.environ["DATABASE_URL"] = f"sqlite:///{target.as_posix()}"
    os.environ["DEBUG"] = "True"
    os.environ["IS_PRODUCTION"] = "False"
    os.environ["ALLOWED_HOSTS"] = "testserver,localhost,127.0.0.1"
    os.environ["MEDIA_ROOT"] = str(BASE_DIR / "media")
    return temp_dir


def request_sizes(paths: list[str], repeat: int) -> tuple[list[dict], Counter, defaultdict]:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shopease.settings")
    import django

    django.setup()
    from django.db import connections
    from django.test import Client

    client = Client()
    rows: list[dict] = []
    totals = Counter()
    statuses = Counter()
    for _ in range(repeat):
        for path in paths:
            response = client.get(path, follow=False)
            if getattr(response, "streaming", False):
                size = sum(len(chunk) for chunk in response.streaming_content)
            else:
                size = len(response.content)
            rows.append({
                "path": path,
                "status": response.status_code,
                "bytes": size,
                "content_type": response.headers.get("Content-Type", ""),
                "cache_control": response.headers.get("Cache-Control", ""),
            })
            totals[path] += size
            statuses[f"{response.status_code}"] += 1
    connections.close_all()
    try:
        from django.db import connection
        connection.close()
    except Exception:
        pass
    return rows, totals, statuses


def main() -> int:
    args = parse_args()
    if args.repeat < 1:
        raise SystemExit("--repeat must be at least 1")
    paths = args.paths or DEFAULT_PATHS
    with configure_isolated_database():
        rows, totals, statuses = request_sizes(paths, args.repeat)

    total_bytes = sum(item["bytes"] for item in rows)
    request_count = len(rows)
    report = {
        "mode": "local-isolated-django-test-client",
        "paths": paths,
        "repeat": args.repeat,
        "request_count": request_count,
        "total_bytes": total_bytes,
        "total_mb": round(total_bytes / 1024 / 1024, 3),
        "status_counts": dict(statuses),
        "routes": [
            {
                "path": path,
                "requests": sum(1 for item in rows if item["path"] == path),
                "bytes": bytes_sent,
                "mb": round(bytes_sent / 1024 / 1024, 3),
                "avg_bytes": round(bytes_sent / max(1, args.repeat)),
            }
            for path, bytes_sent in totals.most_common()
        ],
        "responses": rows,
    }
    print(json.dumps(report, indent=2))
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Report written to {args.output}", file=sys.stderr)

    failed = False
    if args.fail_if_total_mb is not None and total_bytes > args.fail_if_total_mb * 1024 * 1024:
        print(f"FAIL: total {total_bytes / 1024 / 1024:.3f} MB exceeds budget {args.fail_if_total_mb:.3f} MB", file=sys.stderr)
        failed = True
    if args.fail_if_route_kb is not None:
        for path, bytes_sent in totals.items():
            if bytes_sent > args.fail_if_route_kb * 1024:
                print(f"FAIL: {path} uses {bytes_sent / 1024:.1f} KB and exceeds route budget {args.fail_if_route_kb:.1f} KB", file=sys.stderr)
                failed = True
    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
