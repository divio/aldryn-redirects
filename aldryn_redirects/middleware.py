from django import http
from django.conf import settings

from .models import Redirect


class RedirectFallbackMiddleware(object):
    def process_request(self, request):
        path = request.get_full_path()
        try:
            r = Redirect.objects.get(site__id__exact=settings.SITE_ID, old_path=path)
        except Redirect.DoesNotExist:
            r = None
        if r is None and settings.APPEND_SLASH:
            # Try removing the trailing slash.
            try:
                r = Redirect.objects.get(
                    site__id__exact=settings.SITE_ID,
                    old_path=path[:path.rfind('/')]+path[path.rfind('/')+1:]
                )
            except Redirect.DoesNotExist:
                pass
        if r is not None:
            if r.new_path == '':
                return http.HttpResponseGone()
            return http.HttpResponsePermanentRedirect(r.new_path)
