from django import http
from django.conf import settings
from django.db.models import Q

from .models import Redirect


class RedirectFallbackMiddleware(object):

    def process_request(self, request):
        path = request.path_info
        path_with_queries = request.get_full_path()
        queries = (
            Q(old_path__iexact=path)
            | Q(old_path__iexact=path_with_queries)
        )

        if settings.APPEND_SLASH and path.endswith('/'):
            path_with_queries_no_slash = path[:-1] + path_with_queries[len(path):]
            queries |= (
                Q(old_path__iexact=path[:-1])
                | Q(old_path__iexact=path_with_queries_no_slash)
            )

        try:
            r = Redirect.objects.filter(
                queries,
                site__id__exact=settings.SITE_ID
            ).distinct().get()
        except Redirect.DoesNotExist:
            return

        if r.new_path == '':
            return http.HttpResponseGone()
        return http.HttpResponsePermanentRedirect(r.new_path)
