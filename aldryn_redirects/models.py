from __future__ import unicode_literals

from django.db import models
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _, ugettext

from parler.models import TranslatableModel, TranslatedFields
from six.moves.urllib.parse import urlparse, urljoin

from .managers import StaticRedirectManager, StaticRedirectInboundRouteQueryParamManager
from .utils import add_query_params_to_url
from .validators import validate_inbound_route, validate_outbound_route


@python_2_unicode_compatible
class Redirect(TranslatableModel):
    site = models.ForeignKey(
        Site, related_name='aldryn_redirects_redirect_set')
    old_path = models.CharField(
        _('redirect from'), max_length=400, db_index=True,
        help_text=_(
            "This should be an absolute path, excluding the domain name. "
            "Example: '/events/search/'."
        ),
    )
    translations = TranslatedFields(
        new_path=models.CharField(
            _('redirect to'), max_length=400, blank=True,
            help_text=_(
                "This can be either an absolute path (as above) or a full URL "
                "starting with 'http://'."
            ),
        ),
    )

    class Meta:
        verbose_name = _('Multilanguage Redirect')
        verbose_name_plural = _('Multilanguage Redirects')
        unique_together = (('site', 'old_path'),)
        ordering = ('old_path',)

    def __str__(self):
        new_paths = ', '.join([
            '{}:{}'.format(t.language_code, t.new_path)
            for t in self.translations.all()
        ])
        if not new_paths:
            new_paths = ugettext('None')
        return "{} ---> {}".format(self.old_path or 'None', new_paths)


class StaticRedirect(models.Model):
    sites = models.ManyToManyField('sites.Site', related_name='+')
    inbound_route = models.CharField(
        _('Redirect from'),
        max_length=255,
        db_index=True,
        validators=[validate_inbound_route, ],
        help_text=_('Redirect origin. Do not provide the domain. Always add a leading slash here.'),
    )
    outbound_route = models.CharField(
        _('Redirect to'),
        max_length=255,
        validators=[validate_outbound_route, ],
        help_text=_('Redirect destination. Domain is not required (defaults to inbound route domain).'),
    )

    objects = StaticRedirectManager.as_manager()

    class Meta:
        verbose_name = _('Static Redirect')
        verbose_name_plural = _('Static Redirects')

    def __str__(self):
        return '{} --> {}'.format(self.inbound_route, self.outbound_route)

    def get_admin_change_url(self):
        return reverse(
            "admin:{}_{}_change".format(self._meta.app_label, self._meta.model_name),
            args=(self.pk, )
        )

    def get_outbound_url(self, domain):
        parsed_outbound_route = urlparse(self.outbound_route)
        if parsed_outbound_route.netloc and parsed_outbound_route.scheme:
            return self.outbound_route

        return urljoin(domain, self.outbound_route)

    def get_full_inbound_route(self):
        return add_query_params_to_url(self.inbound_route, self.query_params.as_dict())


class StaticRedirectInboundRouteQueryParam(models.Model):
    static_redirect = models.ForeignKey(StaticRedirect, related_name='query_params', on_delete=models.CASCADE)
    key = models.CharField(_('Key'), max_length=255)
    value = models.CharField(_('Value'), max_length=255, blank=True)

    objects = StaticRedirectInboundRouteQueryParamManager.as_manager()

    def __str__(self):
        return '{}="{}"'.format(self.key, self.value)
