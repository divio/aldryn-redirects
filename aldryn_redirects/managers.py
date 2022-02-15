from django.conf import settings
from django.db import models

from .utils import get_query_params_dict


class StaticRedirectManager(models.QuerySet):
    def get_for_request(self, request):
        path_info = request.path_info
        request_query_params = get_query_params_dict(request.get_full_path())

        if settings.APPEND_SLASH and path_info.endswith('/'):
            candidates = self.filter(sites__id__exact=settings.SITE_ID, inbound_route=path_info[:-1])
        else:
            candidates = self.filter(sites__id__exact=settings.SITE_ID, inbound_route=path_info)

        for candidate in candidates:
            candidate_query_params = candidate.query_params.as_dict()
            if candidate_query_params == request_query_params:
                return candidate


class StaticRedirectInboundRouteQueryParamManager(models.QuerySet):
    def as_dict(self):
        return dict(self.values_list('key', 'value'))
