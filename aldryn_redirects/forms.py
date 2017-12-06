from __future__ import unicode_literals
from collections import defaultdict

from tablib import Dataset

from django import forms
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from .models import Redirect


def get_existing_redirects(paths):
    redirects = (
        Redirect
        .objects
        .filter(old_path__in=paths)
        .prefetch_related('translations')
    )
    existing_redirects = defaultdict(dict)

    for redirect in redirects:
        translations = redirect.translations.all()
        redirect._languages = [trans.language_code for trans in translations]
        existing_redirects[redirect.old_path] = redirect
    return existing_redirects


def import_from_dataset(dataset):
    new = 0
    imported_redirects = defaultdict(lambda: defaultdict(dict))

    for row in dataset:
        domain, old_path, new_path, language = row[:4]
        imported_redirects[domain][old_path][language] = new_path

    sites = Site.objects.filter(domain__in=imported_redirects)
    create_redirect = Redirect.objects.create

    for site in sites.iterator():
        _redirects = imported_redirects[site.domain]
        existing_redirects = get_existing_redirects(list(_redirects.keys()))

        for path in _redirects:
            if path not in existing_redirects:
                new += 1
                # creates redirect master object
                redirect = create_redirect(site=site, old_path=path)
                redirect._languages = []
                existing_redirects[path] = redirect
            else:
                redirect = existing_redirects[path]

            for language, new_path in _redirects[path].items():
                if language not in redirect._languages:
                    redirect._languages.append(language)
                    redirect.translations.create(language_code=language, new_path=new_path)
    return new


class RedirectsImportForm(forms.Form):
    csv_file = forms.FileField(label=_('csv file'), required=True)

    def clean_csv_file(self, *args, **kwargs):
        csv_file = self.cleaned_data['csv_file']
        csv_file.seek(0)
        dataset = Dataset().load(csv_file.read().decode('utf-8'), format='csv')
        allowed_domains = list(Site.objects.all().values_list('domain', flat=True))

        for idx, row in enumerate(dataset, start=2):
            if len(row) < 4:
                raise forms.ValidationError(_('Row {}: malformed.'.format(idx)))

            domain, old_path, new_path, language = [x.strip() for x in row[:4]]

            if domain not in allowed_domains:
                raise forms.ValidationError(_('Row {}: domain not found.'.format(idx)))

            if not old_path:
                raise forms.ValidationError(_('Row {}: old path is empty.'.format(idx)))

            if not language:
                raise forms.ValidationError(_('Row {}: language is empty.'.format(idx)))

        return csv_file

    def do_import(self):
        csv_file = self.cleaned_data['csv_file']
        csv_file.seek(0)
        dataset = Dataset().load(csv_file.read().decode('utf-8'), format='csv')
        return import_from_dataset(dataset)
