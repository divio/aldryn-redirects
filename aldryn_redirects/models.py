from __future__ import unicode_literals

from django.db import models
from django.contrib.sites.models import Site
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _, ugettext

from parler.models import TranslatableModel, TranslatedFields


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
        verbose_name = _('redirect')
        verbose_name_plural = _('redirects')
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
