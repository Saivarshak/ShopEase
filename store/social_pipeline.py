"""Small post-authentication hooks for Google sign-in."""

import logging

logger = logging.getLogger(__name__)


def sync_google_login_session(strategy, user=None, backend=None, response=None, details=None, *args, **kwargs):
    """Merge a guest cart and cache the Google profile photo after login."""
    if user is None or getattr(backend, "name", "") != "google-oauth2":
        return

    request = getattr(strategy, "request", None)
    if request is None:
        return

    try:
        from .views import _merge_session_cart_into_db, _set_session_profile_photo

        google_profile_photo = {}
        if isinstance(response, dict):
            google_profile_photo.update(response)
        if isinstance(details, dict):
            google_profile_photo.update(details)

        _merge_session_cart_into_db(request, user)
        _set_session_profile_photo(request, user, profile_photo_url=google_profile_photo)
    except Exception:
        # Authentication must not fail because a stale guest-cart item or an
        # optional avatar lookup is malformed.
        logger.exception("Could not complete ShopEase Google-login session setup")
