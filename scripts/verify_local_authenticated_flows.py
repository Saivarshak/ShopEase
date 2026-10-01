"""Temporary, self-cleaning authenticated HTTP smoke test for local ShopEase."""
import os
import re
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shopease.settings")
import django  # noqa: E402

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from store.models import CartItem, Product  # noqa: E402

BASE = os.environ.get("VERIFY_BASE_URL", "http://127.0.0.1:8027").rstrip("/")
USERNAME = "route-check-admin@example.invalid"
PASSWORD = "RouteCheck!2026"
CSRF_RE = re.compile(r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)')


def csrf(session, path):
    response = session.get(f"{BASE}{path}", timeout=20)
    response.raise_for_status()
    token = CSRF_RE.search(response.text)
    if not token:
        raise AssertionError(f"No CSRF token at {path}")
    return token.group(1)


def expect(response, *statuses):
    if response.status_code not in statuses:
        raise AssertionError(f"{response.request.method} {response.url}: {response.status_code}")


User = get_user_model()
User.objects.filter(username=USERNAME).delete()
session = requests.Session()
try:
    # Exercise public registration over HTTP, then grant staff rights only in
    # the local database so the protected admin reads can be verified.
    token = csrf(session, "/register/")
    register = session.post(
        f"{BASE}/register/",
        data={
            "csrfmiddlewaretoken": token,
            "username": USERNAME,
            "email": USERNAME,
            "password": PASSWORD,
            "confirm_password": PASSWORD,
        },
        allow_redirects=False,
        timeout=20,
    )
    expect(register, 200, 302)
    user = User.objects.get(username=USERNAME)
    user.is_staff = True
    user.save(update_fields=["is_staff"])
    session.get(f"{BASE}/logout/", timeout=20)

    token = csrf(session, "/login/")
    login = session.post(
        f"{BASE}/login/",
        data={"csrfmiddlewaretoken": token, "email": USERNAME, "password": PASSWORD},
        allow_redirects=False,
        timeout=20,
    )
    expect(login, 302)

    protected_paths = [
        "/dashboard/", "/dashboard/profile/", "/dashboard/addresses/", "/wishlist/",
        "/orders/", "/admin/", "/admin_panel/", "/admin-panel/",
        "/admin-panel/backgrounds/", "/admin-panel/orders/", "/admin-panel/customers/",
        "/admin-panel/inventory/", "/admin-panel/categories/", "/api/categories/",
    ]
    for path in protected_paths:
        expect(session.get(f"{BASE}{path}", timeout=20), 200)

    product = Product.objects.filter(is_active=True).first()
    if product:
        token = csrf(session, f"/catalog/product/{product.product_id}/")
        cart = session.post(
            f"{BASE}/cart/add/{product.product_id}/",
            data={"csrfmiddlewaretoken": token, "quantity": 1},
            allow_redirects=False,
            timeout=20,
        )
        expect(cart, 302)
        expect(session.get(f"{BASE}/cart/", timeout=20), 200)

    print("PASS: registration, login, protected pages/API, and cart mutation verified")
finally:
    CartItem.objects.filter(user__username=USERNAME).delete()
    User.objects.filter(username=USERNAME).delete()
