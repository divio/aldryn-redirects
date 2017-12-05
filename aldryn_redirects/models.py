from __future__ import unicode_literals

from django.db import models
from django.contrib.sites.models import Site
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _, ugettext

from parler.models import TranslatableModel, TranslatedFields
from six.moves.urllib.parse import urlparse, urljoin

from .managers import StaticRedirectManager
from .validators import validate_inbound_route, validate_outbound_route


@python_2_unicode_compatible
class Redirect(TranslatableModel):
    site = models.ForeignKey(
        Site, related_name='aldryn_redirects_redirect_set')
    old_path = models.CharField(
        _('redirect from'), max_length=200, db_index=True,
        help_text=_(
            "This should be an absolute path, excluding the domain name. "
            "Example: '/events/search/'."
        ),
    )
    translations = TranslatedFields(
        new_path=models.CharField(
            _('redirect to'), max_length=200, blank=True,
            help_text=_(
                "This can be either an absolute path (as above) or a full URL "
                "starting with 'http://'."
            ),
        ),
    )

    class Meta:
        verbose_name = 'Multilanguage Redirect'
        verbose_name_plural = 'Multilanguage Redirects'
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
        max_length=255,
        db_index=True,
        validators=[validate_inbound_route, ],
        help_text=_('Redirect origin. Do not provide the domain. Always add a leading slash here.'),
    )
    outbound_route = models.CharField(
        max_length=255,
        validators=[validate_outbound_route, ],
        help_text=_('Redirect destination. Domain is not required (defaults to inbound route domain).'),
    )

    objects = StaticRedirectManager.as_manager()

    def get_outbound_url(self, request):
        parsed_outbound_route = urlparse(self.outbound_route)
        if parsed_outbound_route.netloc and parsed_outbound_route.scheme:
            return self.outbound_route

        full_domain = '{}://{}'.format(request.scheme, request.site.domain)
        return urljoin(full_domain, self.outbound_route)

    def __str__(self):
        return '{} --> {}'.format(self.inbound_route, self.outbound_route)


class StaticRedirectInboundRouteQueryParam(models.Model):
    static_redirect = models.ForeignKey(StaticRedirect, related_name='query_params')
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return '{}="{}"'.format(self.key, self.value)
