#!/usr/bin/env python3
"""Measure local Django page and asset response sizes without contacting production.

Examples:
    python scripts/bandwidth_audit.py --output bandwidth-baseline.json
    python scripts/bandwidth_audit.py --repeat 10 --fail-if-total-mb 1 --fail-if-route-kb 150
    python scripts/bandwidth_audit.py --path / --path /mens/ --repeat 5 --no-include-assets
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

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
LOCAL_ATTR = re.compile(r"(?P<attr>src|srcset|href)\s*=\s*['\"](?P<value>[^'\"]+)['\"]", re.IGNORECASE)
ASSET_PREFIXES = ("/static/", "/assets/", "/media/", "/uploads/")
ASSET_EXTENSIONS = (".avif", ".css", ".gif", ".ico", ".jpeg", ".jpg", ".js", ".png", ".svg", ".webp", ".woff", ".woff2")
SKIP_PREFIXES = ("#", "data:", "mailto:", "tel:", "javascript:")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", action="append", dest="paths", help="Path to request; repeat for multiple paths")
    parser.add_argument("--repeat", type=int, default=1, help="Cold page visits per path (default: 1)")
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    parser.add_argument("--fail-if-total-mb", type=float, help="Exit 2 when measured body bytes exceed this total")
    parser.add_argument("--fail-if-route-kb", type=float, help="Exit 2 when any path exceeds this total")
    parser.add_argument("--fail-on-http-error", action="store_true", help="Exit 2 if any request returns HTTP 400 or higher")
    parser.add_argument("--include-assets", dest="include_assets", action="store_true", default=True, help="Request local assets referenced by HTML (default)")
    parser.add_argument("--no-include-assets", dest="include_assets", action="store_false", help="Measure only explicitly supplied paths")
    parser.add_argument("--accept-encoding", default="gzip, br", help="Accept-Encoding header used for requests")
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


def response_size(response) -> int:
    if getattr(response, "streaming", False):
        return sum(len(chunk) for chunk in response.streaming_content)
    return len(response.content)


def discover_local_assets(response) -> list[str]:
    content_type = response.headers.get("Content-Type", "")
    if not content_type.startswith("text/html"):
        return []
    html = response.content.decode(response.charset or "utf-8", errors="ignore")
    discovered: list[str] = []
    for match in LOCAL_ATTR.finditer(html):
        attr = match.group("attr").lower()
        values = match.group("value").split() if attr == "srcset" else [match.group("value")]
        for raw in values:
            raw = raw.strip().rstrip(",")
            if not raw or raw.startswith(SKIP_PREFIXES):
                continue
            parsed = urlsplit(raw)
            if parsed.scheme or parsed.netloc:
                continue
            path = parsed.path or "/"
            lower_path = path.lower()
            is_asset = lower_path.startswith(ASSET_PREFIXES) or lower_path.endswith(ASSET_EXTENSIONS)
            if is_asset and path.startswith("/") and path not in discovered:
                discovered.append(path)
    return discovered


def request_sizes(paths: list[str], repeat: int, include_assets: bool, accept_encoding: str) -> tuple[list[dict], Counter, Counter]:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shopease.settings")
    import django

    django.setup()
    from django.db import connections
    from django.test import Client

    client = Client(raise_request_exception=False)
    rows: list[dict] = []
    totals: Counter = Counter()
    statuses: Counter = Counter()
    headers = {"HTTP_ACCEPT_ENCODING": accept_encoding}

    def measure(path: str, parent_path: str | None, kind: str):
        response = client.get(path, follow=False, **headers)
        size = response_size(response)
        row = {
            "path": path,
            "parent_path": parent_path,
            "kind": kind,
            "status": response.status_code,
            "bytes": size,
            "content_type": response.headers.get("Content-Type", ""),
            "content_encoding": response.headers.get("Content-Encoding", ""),
            "content_length": response.headers.get("Content-Length", ""),
            "cache_control": response.headers.get("Cache-Control", ""),
        }
        rows.append(row)
        totals[path] += size
        statuses[str(response.status_code)] += 1
        return response

    for _ in range(repeat):
        for page_path in paths:
            page_response = measure(page_path, None, "page")
            if include_assets and 200 <= page_response.status_code < 300:
                for asset_path in discover_local_assets(page_response):
                    measure(asset_path, page_path, "referenced-asset")

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
        rows, totals, statuses = request_sizes(paths, args.repeat, args.include_assets, args.accept_encoding)

    total_bytes = sum(item["bytes"] for item in rows)
    route_rows = []
    for path, bytes_sent in totals.most_common():
        matching = [item for item in rows if item["path"] == path]
        route_rows.append({
            "path": path,
            "kind": matching[0]["kind"],
            "requests": len(matching),
            "bytes": bytes_sent,
            "mb": round(bytes_sent / 1024 / 1024, 3),
            "avg_bytes": round(bytes_sent / max(1, len(matching))),
        })
    report = {
        "mode": "local-isolated-django-test-client",
        "paths": paths,
        "repeat": args.repeat,
        "include_referenced_assets": args.include_assets,
        "accept_encoding": args.accept_encoding,
        "request_count": len(rows),
        "page_request_count": sum(item["kind"] == "page" for item in rows),
        "asset_request_count": sum(item["kind"] == "referenced-asset" for item in rows),
        "total_bytes": total_bytes,
        "total_mb": round(total_bytes / 1024 / 1024, 3),
        "status_counts": dict(statuses),
        "routes": route_rows,
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
    if args.fail_on_http_error and any(int(status) >= 400 for status in statuses):
        print(f"FAIL: HTTP errors observed: {dict(statuses)}", file=sys.stderr)
        failed = True
    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
