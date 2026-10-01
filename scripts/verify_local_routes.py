"""Read-only HTTP verification of ShopEase's public and protected GET routes.

Run while ``python manage.py runserver 127.0.0.1:8024 --noreload`` is active.
It deliberately makes no POST, PUT, PATCH, or DELETE requests.
"""
import os
import re
import sys
from collections import deque
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shopease.settings")
import django  # noqa: E402

django.setup()

from store.models import FashionCategory, Product, UploadedImage  # noqa: E402

BASE = os.environ.get("VERIFY_BASE_URL", "http://127.0.0.1:8024").rstrip("/")
TIMEOUT = 20
STATUS_OK = {200, 301, 302, 303, 307, 308, 401, 403, 405}
ATTRIBUTE_URL = re.compile(r'''(?:href|src)=["']([^"'#]+)''', re.I)


def category_path(category):
    segments = []
    current = category
    while current and current.parent_id:
        segments.append(current.slug)
        current = current.parent
    return "/".join(reversed(segments))


def absolute(path):
    return urljoin(BASE, path)


def internal_url(candidate):
    parsed = urlparse(candidate)
    if parsed.scheme and parsed.netloc != urlparse(BASE).netloc:
        return None
    if parsed.scheme in {"mailto", "tel", "javascript", "data"}:
        return None
    return candidate if parsed.scheme else absolute(candidate)


seed_paths = {
    "/", "/health/", "/mens/", "/men/", "/womens/", "/women/", "/kids/",
    "/accessories/common/", "/contact-us/", "/contact.html", "/privacy-policy/",
    "/refund-policy/", "/terms-and-conditions/", "/search/?q=shirt", "/catalog/",
    "/api/products/", "/api/categories/", "/login/", "/register/", "/cart/",
    "/payment/", "/orders/", "/wishlist/", "/dashboard/", "/dashboard/profile/",
    "/dashboard/addresses/", "/admin/", "/admin_panel/", "/admin-panel/",
    "/admin-panel/backgrounds/", "/admin-panel/orders/", "/admin-panel/customers/",
    "/admin-panel/inventory/", "/admin-panel/categories/", "/admin-panel/products/add/",
    "/under-maintenance/",
}

for product in Product.objects.filter(is_active=True).only("product_id"):
    seed_paths.add(f"/catalog/product/{product.product_id}/")
    seed_paths.add(f"/product/{product.product_id}/")

for category in FashionCategory.objects.filter(is_active=True).exclude(
    root_category__category_name__in=["mens", "womens", "kids"]
).select_related("parent", "root_category"):
    path = category_path(category)
    if category.root_category and path:
        gender = category.root_category.category_name.lower()
        if gender in {"mens", "womens", "kids"}:
            seed_paths.add(f"/{gender}/{path}/")

for image in UploadedImage.objects.only("path"):
    seed_paths.add(f"/assets/{image.path}")

session = requests.Session()
queue = deque(sorted(absolute(path) for path in seed_paths))
seen = set()
failures = []
checked = []

while queue:
    url = queue.popleft()
    if url in seen:
        continue
    seen.add(url)
    try:
        # Authentication may deliberately redirect to a third-party OAuth
        # provider.  Verify the local response, but never send the crawler to
        # that external endpoint.
        response = session.get(url, timeout=TIMEOUT, allow_redirects=False)
    except requests.RequestException as exc:
        failures.append((url, "REQUEST_ERROR", str(exc)))
        continue
    checked.append((url, response.status_code, len(response.content)))
    if response.status_code not in STATUS_OK:
        failures.append((url, response.status_code, response.url))
        continue
    if response.is_redirect:
        location = response.headers.get("location", "")
        target = internal_url(location)
        if target and target not in seen:
            queue.append(target)
        continue
    if "text/html" not in response.headers.get("content-type", ""):
        continue
    for raw in ATTRIBUTE_URL.findall(response.text):
        target = internal_url(raw)
        if target and target not in seen:
            queue.append(target)

print(f"Checked {len(checked)} unique local URLs")
print(f"Database-backed image records checked: {UploadedImage.objects.count()}")
print("Status summary:", {
    status: sum(1 for _, code, _ in checked if code == status)
    for status in sorted({code for _, code, _ in checked})
})
if failures:
    print("Failures:")
    for failure in failures:
        print(*failure, sep=" | ")
    sys.exit(1)
print("PASS: no unexpected HTTP status, broken internal link, or asset request found")
