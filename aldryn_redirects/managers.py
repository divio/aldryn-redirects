from __future__ import unicode_literals

from django.conf import settings
from django.db import models

from six.moves.urllib.parse import urlparse, parse_qsl


class StaticRedirectManager(models.QuerySet):
    def get_for_request(self, request):
        path_info = request.path_info
        # request.GET sounds tempting below but wouldn't work for malformed querystrings (such as '/path?hamster').
        request_query_params = dict(parse_qsl(urlparse(request.get_full_path()).query, keep_blank_values=True))

        candidates = self.filter(sites__id__exact=settings.SITE_ID, inbound_route=path_info)
        if settings.APPEND_SLASH and path_info.endswith('/'):
            candidates = self.filter(sites__id__exact=settings.SITE_ID, inbound_route=path_info[:-1])

        for candidate in candidates:
            candidate_query_params = dict(candidate.query_params.values_list('key', 'value'))
            if candidate_query_params == request_query_params:
                return candidate
