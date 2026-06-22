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
