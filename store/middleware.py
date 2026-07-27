"""Small, dependency-free HTTP hardening middleware for the deployed app."""
from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


SYNC_SCRIPT = """
<script>
(() => {
  const key = 'shopease:catalog-updated';
  window.addEventListener('storage', (event) => {
    if (event.key === key && event.newValue && !location.pathname.startsWith('/admin')) {
      location.reload();
    }
  });
})();
</script>
"""


class StorefrontSyncMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        content_type = response.get('Content-Type', '')
        if 'text/html' not in content_type or response.streaming:
            return response
        try:
            content = response.content.decode(response.charset or 'utf-8')
        except (UnicodeDecodeError, AttributeError):
            return response
        if '</body>' not in content or 'shopease:catalog-updated' in content:
            return response
        response.content = content.replace('</body>', f'{SYNC_SCRIPT}</body>').encode(response.charset or 'utf-8')
        response['Content-Length'] = str(len(response.content))
        return response


class RestrictedCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get("Origin", "").rstrip("/")
        allowed = origin and origin in settings.CORS_ALLOWED_ORIGINS
        response = HttpResponse(status=204) if request.method == "OPTIONS" and allowed else self.get_response(request)
        if allowed:
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, X-Requested-With"
            response["Vary"] = "Origin"
        return response


class ProductionSecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.setdefault("X-DNS-Prefetch-Control", "off")
        response.setdefault("Cross-Origin-Resource-Policy", "same-site")
        return response
