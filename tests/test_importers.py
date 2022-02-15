from __future__ import print_function, division

from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.test import TestCase

from aldryn_redirects.importers import RedirectImporter
from aldryn_redirects.models import Redirect


class RedirectImporterGetExistingRedirectsTestCase(TestCase):
    def setUp(self):
        super(RedirectImporterGetExistingRedirectsTestCase, self).setUp()
        self.get_existing_redirects = RedirectImporter().get_existing_redirects

    def test_common(self):
        site1 = Site.objects.get()
        site2 = Site.objects.create(domain='testtest.com')

        redirect1 = Redirect.objects.create(site=site1, old_path='/old1')
        redirect1.translations.create(language_code='de', new_path='/new1/de')
        redirect1.translations.create(language_code='pt', new_path='/new1/pt')

        redirect2 = Redirect.objects.create(site=site1, old_path='/old2')
        redirect2.translations.create(language_code='de', new_path='/new1/de')

        redirect3 = Redirect.objects.create(site=site2, old_path='/old1')
        redirect3.translations.create(language_code='de', new_path='/new1/de')

        # Noise
        Redirect.objects.create(site=site1, old_path='/xxx/old1')
        Redirect.objects.create(site=site1, old_path='/old1/xxx')

        result = self.get_existing_redirects(site1, ['/old1', '/old2'])
        self.assertEquals(list(result.keys()), ['/old1', '/old2'])
        self.assertEquals(list(result.values()), [redirect1, redirect2])
        self.assertFalse(hasattr(redirect1, '_languages'))
        self.assertFalse(hasattr(redirect2, '_languages'))
        enriched_redirect1, enriched_redirect2 = result.values()
        self.assertEquals(enriched_redirect1._languages, ['de', 'pt'])
        self.assertEquals(enriched_redirect2._languages, ['de'])

        result = self.get_existing_redirects(site2, ['/old1', '/old2'])
        self.assertEquals(list(result.keys()), ['/old1'])
        self.assertEquals(list(result.values()), [redirect3])


class RedirectImporterValidateRowTestCase(TestCase):
    def setUp(self):
        super(RedirectImporterValidateRowTestCase, self).setUp()
        self.row = [Site.objects.first().domain, '/origin/path', 'destination/path', 'en']
        self.validate_row = RedirectImporter().validate_row

    def test_success(self):
        self.validate_row(self.row)  # Nothing raised

        self.row[2] = ''  # New path is not required.
        self.validate_row(self.row)  # Nothing raised

        self.row[3] = 'pt-br'  # This language is supported in our tests/settings.py
        self.validate_row(self.row)  # Nothing raised

    def test_malformed_row(self):
        del self.row[2:]
        self.assertRaises(ValidationError, self.validate_row, self.row)

    def test_domain_missing(self):
        self.row[0] = ''
        self.assertRaises(ValidationError, self.validate_row, self.row)

    def test_domain_invalid(self):
        self.row[0] = 'unknown.domain.com'
        self.assertRaises(ValidationError, self.validate_row, self.row)

    def test_old_path_missing(self):
        self.row[1] = ''
        self.assertRaises(ValidationError, self.validate_row, self.row)

    def test_old_path_too_large(self):
        self.row[1] = '/path' * 100
        self.assertRaises(ValidationError, self.validate_row, self.row)

    def test_new_path_too_large(self):
        self.row[2] = '/path' * 100
        self.assertRaises(ValidationError, self.validate_row, self.row)

    def test_language_code_missing(self):
        self.row[3] = ''
        self.assertRaises(ValidationError, self.validate_row, self.row)

    def test_language_code_invalid(self):
        self.row[3] = 'de'  # Not declared as a language in our tests/settings.py
        self.assertRaises(ValidationError, self.validate_row, self.row)
