from __future__ import unicode_literals

from tablib import Dataset

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .importers import RedirectImporter, StaticRedirectImporter


class RedirectsImportForm(forms.Form):
    importer_class = RedirectImporter

    csv_file = forms.FileField(label=_('csv file'), required=True)

    def __init__(self, *args, **kwargs):
        super(RedirectsImportForm, self).__init__(*args, **kwargs)
        self.importer = self.importer_class()

    def clean_csv_file(self, *args, **kwargs):
        csv_file = self.cleaned_data['csv_file']
        csv_file.seek(0)
        dataset = Dataset().load(csv_file.read().decode('utf-8'), format='csv')

        for idx, row in enumerate(dataset, start=2):
            try:
                self.importer.validate_row(row)
            except ValidationError as e:
                raise forms.ValidationError('Line {}: {}'.format(idx, '\n'.join(e.messages)))

        return csv_file

    def do_import(self):
        csv_file = self.cleaned_data['csv_file']
        csv_file.seek(0)
        dataset = Dataset().load(csv_file.read().decode('utf-8'), format='csv')
        self.importer.import_from_dataset(dataset)


class StaticRedirectsImportForm(RedirectsImportForm):
    importer_class = StaticRedirectImporter
