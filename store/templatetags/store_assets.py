from pathlib import Path

from django import template
from django.conf import settings
from django.urls import reverse
from django.db.utils import OperationalError, ProgrammingError
from store.models import UploadedImage


register = template.Library()
PLACEHOLDER_ASSET = 'images/placeholder.svg'


def _asset_file_exists(candidate):
    if candidate.parts[:1] == ('dbuploads',):
        try:
            return UploadedImage.objects.filter(path=candidate.as_posix()).exists()
        except (ProgrammingError, OperationalError):
            return False
    if candidate.parts[:1] == ('uploads',):
        return (Path(settings.MEDIA_ROOT) / candidate).exists()
    if candidate.parts[:1] == ('images',):
        return (Path(settings.BASE_DIR) / 'static' / candidate).exists()
    return False


@register.simple_tag
def asset_src(asset_path):
    normalized = (asset_path or '').strip().replace('\\', '/').lstrip('/')
    if not normalized:
        normalized = PLACEHOLDER_ASSET
    if normalized.startswith('static/'):
        normalized = normalized[len('static/'):]
    if '/' not in normalized:
        normalized = f'images/{normalized}'

    if normalized.startswith(('http://', 'https://')):
        return normalized

    candidate = Path(normalized)
    if candidate.is_absolute() or '..' in candidate.parts or candidate.parts[:1] not in {('images',), ('uploads',), ('dbuploads',)}:
        candidate = Path(PLACEHOLDER_ASSET)
    elif not _asset_file_exists(candidate):
        image_fallback = Path('images') / candidate.name
        if _asset_file_exists(image_fallback):
            candidate = image_fallback
        else:
            candidate = Path(PLACEHOLDER_ASSET)

    return reverse('store_asset', kwargs={'asset_path': candidate.as_posix()})
