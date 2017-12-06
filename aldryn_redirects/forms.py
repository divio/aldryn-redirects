from __future__ import unicode_literals
from collections import defaultdict

from tablib import Dataset

from django import forms
from django.core.exceptions import ValidationError
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


def validate_row(row, site_domain_id_mapping):
    def _flatten_error(e):
        result = []
        for key, values in e.message_dict.items():
            for value in values:
                result.append('{}: {}'.format(key, value))

        return '\n'.join(result)

    if len(row) < 4:
        raise ValidationError(_(
            'malformed row. Row must contain site (required), '
            'old_path (required), new_path (optional) and language_code (required).'
        ))

    domain, old_path, new_path, language = [x.strip() for x in row[:4]]

    if domain not in site_domain_id_mapping.keys():
        raise ValidationError(_('domain not found.'))

    redirect = Redirect(site_id=site_domain_id_mapping[domain], old_path=old_path)
    try:
        redirect.full_clean(validate_unique=False)
    except ValidationError as e:
        raise ValidationError(_flatten_error(e))

    redirect_translation = redirect.translations.model(master=redirect, language_code=language, new_path=new_path)
    try:
        redirect_translation.full_clean(validate_unique=False)
    except ValidationError as e:
        raise ValidationError(_flatten_error(e))


class RedirectsImportForm(forms.Form):
    csv_file = forms.FileField(label=_('csv file'), required=True)

    def clean_csv_file(self, *args, **kwargs):
        csv_file = self.cleaned_data['csv_file']
        csv_file.seek(0)
        dataset = Dataset().load(csv_file.read().decode('utf-8'), format='csv')
        site_domain_id_mapping = dict(Site.objects.values_list('domain', 'id'))

        for idx, row in enumerate(dataset, start=2):
            try:
                validate_row(row, site_domain_id_mapping)
            except ValidationError as e:
                raise forms.ValidationError('Line {}: {}'.format(idx, e))

        return csv_file

    def do_import(self):
        csv_file = self.cleaned_data['csv_file']
        csv_file.seek(0)
        dataset = Dataset().load(csv_file.read().decode('utf-8'), format='csv')
        return import_from_dataset(dataset)
