from __future__ import annotations
import json
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent
ATTR_RE = re.compile(r'(?P<attr>src|srcset|href)\s*=\s*["\'](?P<value>[^"\']+)["\']', re.I)
refs = defaultdict(list)
for path in (ROOT / 'templates').rglob('*.html'):
    text = path.read_text(encoding='utf-8', errors='ignore')
    for match in ATTR_RE.finditer(text):
        value = match.group('value').strip()
        if any(token in value.lower() for token in ('.png', '.jpg', '.jpeg', '.webp', '.avif', '.gif', '.svg', 'static', 'asset_src')):
            refs[value].append({'template': path.relative_to(ROOT).as_posix(), 'attribute': match.group('attr')})
summary = {
    'reference_count': sum(len(v) for v in refs.values()),
    'unique_reference_count': len(refs),
    'references': dict(sorted(refs.items(), key=lambda item: (-len(item[1]), item[0].lower()))),
}
(ROOT / 'image-reference-audit.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print(json.dumps(summary, indent=2))
