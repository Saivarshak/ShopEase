from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
IMAGE_EXTS = {'.avif', '.gif', '.jpeg', '.jpg', '.png', '.svg', '.webp'}
SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}
rows = []
for path in ROOT.rglob('*'):
    if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
        continue
    if any(part in SKIP_DIRS for part in path.parts):
        continue
    data = path.read_bytes()
    row = {
        'path': path.relative_to(ROOT).as_posix(),
        'bytes': len(data),
        'kb': round(len(data) / 1024, 2),
        'extension': path.suffix.lower().lstrip('.'),
        'sha256': hashlib.sha256(data).hexdigest(),
        'width': None,
        'height': None,
        'format': None,
        'mode': None,
        'error': None,
    }
    if path.suffix.lower() != '.svg':
        try:
            with Image.open(path) as im:
                row.update(width=im.width, height=im.height, format=im.format, mode=im.mode)
        except Exception as exc:
            row['error'] = str(exc)
    rows.append(row)

rows.sort(key=lambda r: r['bytes'], reverse=True)
with (ROOT / 'image-audit.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else ['path'])
    writer.writeheader()
    writer.writerows(rows)

by_hash = {}
for row in rows:
    by_hash.setdefault(row['sha256'], []).append(row['path'])
duplicates = [paths for paths in by_hash.values() if len(paths) > 1]
summary = {
    'root': str(ROOT),
    'image_count': len(rows),
    'total_bytes': sum(r['bytes'] for r in rows),
    'total_mb': round(sum(r['bytes'] for r in rows) / 1024 / 1024, 3),
    'by_extension': {},
    'duplicates': duplicates,
    'largest': rows[:25],
}
for row in rows:
    ext = row['extension']
    bucket = summary['by_extension'].setdefault(ext, {'count': 0, 'bytes': 0})
    bucket['count'] += 1
    bucket['bytes'] += row['bytes']
for bucket in summary['by_extension'].values():
    bucket['mb'] = round(bucket['bytes'] / 1024 / 1024, 3)
(ROOT / 'image-audit-summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print(json.dumps(summary, indent=2))
