# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.test import TestCase

from aldryn_redirects.forms import validate_row


class ValidateRowTestCase(TestCase):
    def setUp(self):
        super(ValidateRowTestCase, self).setUp()
        self.site_domain_id_mapping = dict(Site.objects.values_list('domain', 'id'))
        self.row = [Site.objects.first().domain, '/origin/path', 'destination/path', 'en']

    def test_success(self):
        validate_row(self.row, self.site_domain_id_mapping)  # Nothing raised

        self.row[2] = ''  # New path is not required.
        validate_row(self.row, self.site_domain_id_mapping)  # Nothing raised

        self.row[3] = 'pt-br'  # This language is supported in our tests/settings.py
        validate_row(self.row, self.site_domain_id_mapping)  # Nothing raised

    def test_malformed_row(self):
        del self.row[2:]
        self.assertRaises(ValidationError, validate_row, self.row, self.site_domain_id_mapping)

    def test_domain_missing(self):
        self.row[0] = ''
        self.assertRaises(ValidationError, validate_row, self.row, self.site_domain_id_mapping)

    def test_domain_invalid(self):
        self.row[0] = 'unknown.domain.com'
        self.assertRaises(ValidationError, validate_row, self.row, self.site_domain_id_mapping)

    def test_old_path_missing(self):
        self.row[1] = ''
        self.assertRaises(ValidationError, validate_row, self.row, self.site_domain_id_mapping)

    def test_old_path_too_large(self):
        self.row[1] = '/path' * 100
        self.assertRaises(ValidationError, validate_row, self.row, self.site_domain_id_mapping)

    def test_new_path_too_large(self):
        self.row[2] = '/path' * 100
        self.assertRaises(ValidationError, validate_row, self.row, self.site_domain_id_mapping)

    def test_language_code_missing(self):
        self.row[3] = ''
        self.assertRaises(ValidationError, validate_row, self.row, self.site_domain_id_mapping)

    def test_language_code_invalid(self):
        self.row[3] = 'de'  # Not declared as a language in our tests/settings.py
        self.assertRaises(ValidationError, validate_row, self.row, self.site_domain_id_mapping)
