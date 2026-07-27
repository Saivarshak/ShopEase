"""Environment-driven settings for ShopEase."""
import os
from pathlib import Path
from urllib.parse import urlparse

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent.parent
if load_dotenv:
    load_dotenv(BASE_DIR / ".env")


def _env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _env_list(name, default=""):
    return [item.strip().rstrip("/") for item in os.environ.get(name, default).split(",") if item.strip()]


def _build_host_security_settings():
    """Build host and CSRF allowlists from the public callback URL too."""
    allowed_hosts = _env_list("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver")
    trusted_origins = _env_list("CSRF_TRUSTED_ORIGINS", "")
    for raw_url in (os.environ.get("APP_BASE_URL", ""), os.environ.get("PAYMENT_CALLBACK_BASE_URL", "")):
        parsed = urlparse(raw_url.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            continue
        if parsed.hostname not in allowed_hosts:
            allowed_hosts.append(parsed.hostname)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in trusted_origins:
            trusted_origins.append(origin)
    return allowed_hosts, trusted_origins


DEBUG = _env_bool("DEBUG", False)
IS_PRODUCTION = _env_bool("IS_PRODUCTION", not DEBUG) or os.environ.get("DJANGO_ENV", "").lower() == "production"
SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    if IS_PRODUCTION:
        raise ImproperlyConfigured("SECRET_KEY must be set when IS_PRODUCTION=true.")
    SECRET_KEY = "django-insecure-local-development-key"

APP_BASE_URL = os.environ.get("APP_BASE_URL", "").strip().rstrip("/")
ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS = _build_host_security_settings()
render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip()
if render_host and render_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_host)
_default_trusted_origins = APP_BASE_URL if APP_BASE_URL.startswith("https://") else ""
if _default_trusted_origins and _default_trusted_origins not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(_default_trusted_origins)
# Same-origin by default; cross-origin access must be explicitly allowed.
CORS_ALLOWED_ORIGINS = _env_list("CORS_ALLOWED_ORIGINS", _default_trusted_origins)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "social_django",
    "store",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "store.middleware.RestrictedCorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "store.middleware.ProductionSecurityHeadersMiddleware",
]
ROOT_URLCONF = "shopease.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "store.context_processors.user_profile",
    ]},
}]
WSGI_APPLICATION = "shopease.wsgi.application"

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if IS_PRODUCTION and not DATABASE_URL:
    raise ImproperlyConfigured("DATABASE_URL must point to managed PostgreSQL in production.")
DATABASES = {"default": dj_database_url.config(
    default=DATABASE_URL or f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    conn_max_age=int(os.environ.get("DB_CONN_MAX_AGE", "600")),
    conn_health_checks=True,
)}

AUTHENTICATION_BACKENDS = ["social_core.backends.google.GoogleOAuth2", "django.contrib.auth.backends.ModelBackend"]
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")

LANGUAGE_CODE = "en-us"
TIME_ZONE = os.environ.get("TIME_ZONE", "Asia/Kolkata")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {"staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}}
WHITENOISE_MAX_AGE = 31536000
WHITENOISE_USE_FINDERS = not IS_PRODUCTION
# The existing app stores new uploads in UploadedImage (PostgreSQL); MEDIA_ROOT
# exists only for legacy local uploads and is not relied upon in production.
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
MAX_UPLOAD_IMAGE_BYTES = int(os.environ.get("MAX_UPLOAD_IMAGE_BYTES", str(10 * 1024 * 1024)))

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = _env_bool("USE_X_FORWARDED_HOST", IS_PRODUCTION)
SECURE_SSL_REDIRECT = _env_bool("SECURE_SSL_REDIRECT", IS_PRODUCTION)
SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE", IS_PRODUCTION)
CSRF_COOKIE_SECURE = _env_bool("CSRF_COOKIE_SECURE", IS_PRODUCTION)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000" if IS_PRODUCTION else "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", IS_PRODUCTION)
SECURE_HSTS_PRELOAD = _env_bool("SECURE_HSTS_PRELOAD", False)

RAZORPAY_MODE = os.environ.get("RAZORPAY_MODE", "test").strip().lower()
RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "")
PAYMENT_CALLBACK_BASE_URL = os.environ.get("PAYMENT_CALLBACK_BASE_URL", APP_BASE_URL).strip().rstrip("/")
RAZORPAY_PAYMENT_LINK_OVERRIDE_URL = os.environ.get("RAZORPAY_PAYMENT_LINK_OVERRIDE_URL", "")
RAZORPAY_PAYMENT_HANDLE_URL = os.environ.get("RAZORPAY_PAYMENT_HANDLE_URL", "")

EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = _env_bool("EMAIL_USE_TLS", True)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@localhost")
SHOP_ADMIN_EMAIL = os.environ.get("SHOP_ADMIN_EMAIL", "")

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO" if IS_PRODUCTION else "DEBUG")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"verbose": {"format": "{asctime} {levelname} {name} {message}", "style": "{"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "verbose"}},
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
