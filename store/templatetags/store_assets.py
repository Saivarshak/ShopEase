from pathlib import Path

from django import template
from django.urls import reverse


register = template.Library()


@register.simple_tag
def asset_src(asset_path):
    normalized = (asset_path or '').strip().replace('\\', '/').lstrip('/')
    if not normalized:
        return ''
    if normalized.startswith('static/'):
        normalized = normalized[len('static/'):]
    if '/' not in normalized:
        normalized = f'images/{normalized}'

    candidate = Path(normalized)
    if candidate.is_absolute() or '..' in candidate.parts or candidate.parts[:1] != ('images',):
        return ''

    return reverse('store_asset', kwargs={'asset_path': candidate.as_posix()})
