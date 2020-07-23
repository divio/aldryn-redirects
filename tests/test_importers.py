# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.test import TestCase

from aldryn_redirects.importers import RedirectImporter, StaticRedirectImporter
from aldryn_redirects.models import Redirect, StaticRedirect, StaticRedirectInboundRouteQueryParam


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


class StaticRedirectImporterValidateRowTestCase(TestCase):
    def setUp(self):
        super(StaticRedirectImporterValidateRowTestCase, self).setUp()
        self.row = [Site.objects.first().domain, '/origin/path', '/destination/path']
        self.validate_row = StaticRedirectImporter().validate_row

    def test_success(self):
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

    def test_inbound_route_missing(self):
        self.row[1] = ''
        self.assertRaises(ValidationError, self.validate_row, self.row)

    def test_inbound_route_too_large(self):
        self.row[1] = '/path' * 100
        self.assertRaises(ValidationError, self.validate_row, self.row)

    def test_inbound_route_sanity(self):
        # NOTE: Use of query params in inbound_route is disallowed in models, but importer deals with that
        self.row[1] = '/origin?key1=value1'
        self.validate_row(self.row)  # Nothing raised

        self.row[1] = 'http://example.com/origin'
        self.assertRaises(ValidationError, self.validate_row, self.row)

        self.row[1] = 'origin'
        self.assertRaises(ValidationError, self.validate_row, self.row)

        self.row[1] = '/origin/'
        self.assertRaises(ValidationError, self.validate_row, self.row)

        self.row[1] = '/<script>hello</script>'
        self.assertRaises(ValidationError, self.validate_row, self.row)

    def test_outbound_route_missing(self):
        self.row[2] = ''
        self.assertRaises(ValidationError, self.validate_row, self.row)

    def test_outbound_route_too_large(self):
        self.row[2] = '/path' * 100
        self.assertRaises(ValidationError, self.validate_row, self.row)

    def test_outbound_route_sanity(self):
        self.row[2] = 'http://example.com/destination'
        self.validate_row(self.row)  # Nothing raised

        self.row[2] = 'https://example.com/destination'
        self.validate_row(self.row)  # Nothing raised

        self.row[2] = '/destination'
        self.validate_row(self.row)  # Nothing raised

        self.row[2] = '/destination/'
        self.validate_row(self.row)  # Nothing raised

        self.row[2] = '/destination/?xxx=yyy'
        self.validate_row(self.row)  # Nothing raised

        self.row[2] = 'www.google.com/destination/?xxx=yyy'
        self.assertRaises(ValidationError, self.validate_row, self.row)

    def test_new_duplicated_row_is_ok(self):
        ''' Dupes will be handled on StaticImporter.import_from_dataset as if they are updates. '''
        redirect = StaticRedirect.objects.create(inbound_route='/origin/path', outbound_route='/destination/path')
        redirect.sites.add(Site.objects.first())
        self.validate_row(self.row)  # Nothing raised


class StaticRedirectImporterImportFromDatasetTestCase(TestCase):
    def setUp(self):
        super(StaticRedirectImporterImportFromDatasetTestCase, self).setUp()
        self.site = Site.objects.first()
        self.dataset = [
            [self.site.domain, '/origin/path?query=param&empty=', '/destination/path']
        ]
        self.import_from_dataset = StaticRedirectImporter().import_from_dataset

    def test_common(self):
        self.assertEquals(StaticRedirect.objects.count(), 0)
        self.assertEquals(StaticRedirectInboundRouteQueryParam.objects.count(), 0)

        self.import_from_dataset(self.dataset)

        self.assertEquals(StaticRedirect.objects.count(), 1)
        self.assertEquals(StaticRedirectInboundRouteQueryParam.objects.count(), 2)

        redirect = StaticRedirect.objects.get()
        self.assertEquals(redirect.sites.count(), 1)
        self.assertTrue(redirect.sites.filter(domain=self.dataset[0][0]).exists())

        self.assertEquals(redirect.inbound_route, self.dataset[0][1].split('?')[0])  # no query params here
        self.assertEquals(redirect.outbound_route, self.dataset[0][2])

        self.assertEquals(redirect.query_params.count(), 2)
        self.assertTrue(redirect.query_params.filter(key='query', value='param').exists())
        self.assertTrue(redirect.query_params.filter(key='empty', value='').exists())

    def test_update_existing_rows_is_ok(self):
        self.assertEquals(StaticRedirect.objects.count(), 0)
        self.assertEquals(StaticRedirectInboundRouteQueryParam.objects.count(), 0)

        self.import_from_dataset(self.dataset)

        self.assertEquals(StaticRedirect.objects.count(), 1)
        self.assertEquals(StaticRedirectInboundRouteQueryParam.objects.count(), 2)
        self.assertEquals(StaticRedirect.objects.get().outbound_route, self.dataset[0][2])

        self.dataset[0][2] = 'new-destination'
        self.import_from_dataset(self.dataset)

        self.assertEquals(StaticRedirect.objects.count(), 1)
        self.assertEquals(StaticRedirectInboundRouteQueryParam.objects.count(), 2)
        self.assertEquals(StaticRedirect.objects.get().outbound_route, 'new-destination')

    def test_incremental_import_is_ok(self):
        self.assertEquals(StaticRedirect.objects.count(), 0)
        self.assertEquals(StaticRedirectInboundRouteQueryParam.objects.count(), 0)

        self.import_from_dataset(self.dataset)

        self.assertEquals(StaticRedirect.objects.count(), 1)
        self.assertEquals(StaticRedirectInboundRouteQueryParam.objects.count(), 2)

        self.dataset.append([Site.objects.first().domain, '/origin2', '/destination2'])
        self.import_from_dataset(self.dataset)

        self.assertEquals(StaticRedirect.objects.count(), 2)
        self.assertEquals(StaticRedirectInboundRouteQueryParam.objects.count(), 2)

        qs = StaticRedirect.objects.filter(
            sites=self.site, inbound_route='/origin/path', outbound_route='/destination/path'
        )
        self.assertEquals(qs.count(), 1)

        qs = StaticRedirect.objects.filter(
            sites=self.site, inbound_route='/origin2', outbound_route='/destination2'
        )
        self.assertEquals(qs.count(), 1)

    def test_importing_many_times_is_ok(self):
        self.assertEquals(StaticRedirect.objects.count(), 0)
        self.assertEquals(StaticRedirectInboundRouteQueryParam.objects.count(), 0)

        self.import_from_dataset(self.dataset)
        self.import_from_dataset(self.dataset)
        self.import_from_dataset(self.dataset)

        self.assertEquals(StaticRedirect.objects.count(), 1)
        self.assertEquals(StaticRedirectInboundRouteQueryParam.objects.count(), 2)
