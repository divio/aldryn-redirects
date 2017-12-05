# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from django.contrib.sites.models import Site
from django.test import TestCase
from django.test.client import RequestFactory

from aldryn_redirects.models import StaticRedirect


class StaticRedirectManagerTestCase(TestCase):
    def setUp(self, *args, **kwargs):
        super(StaticRedirectManagerTestCase, self).setUp(*args, **kwargs)
        self.site = Site.objects.first()
        self.another_site = Site.objects.create(domain='hamster.com', name='hamster')

    def create_fake_request(self, url):
        request = RequestFactory().get(url)
        request.site = self.site
        return request

    def test_get_for_request_without_matches(self):
        request = self.create_fake_request('http://example.com/origin')
        self.assertIsNone(StaticRedirect.objects.get_for_request(request))

    def test_get_for_request_without_query_params(self):
        redirect = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='/destination')
        redirect.sites.add(self.site)

        # Noise
        StaticRedirect.objects.create(inbound_route='/original', outbound_route='/destination')
        StaticRedirect.objects.create(inbound_route='/x/origin', outbound_route='/destination')
        StaticRedirect.objects.create(inbound_route='/origin/x', outbound_route='/destination')
        redirect_other_site = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='/destination')
        redirect_other_site.sites.add(self.another_site)

        request = self.create_fake_request('http://example.com/origin')
        self.assertEquals(StaticRedirect.objects.get_for_request(request), redirect)

    def test_get_for_request_without_query_params_with_trailing_slash(self):
        redirect = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='/destination')
        redirect.sites.add(self.site)

        request = self.create_fake_request('http://example.com/origin/')
        self.assertEquals(StaticRedirect.objects.get_for_request(request), redirect)

    def test_get_for_request_with_query_params(self):
        redirect = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='/dest')
        redirect.sites.add(self.site)
        redirect.query_params.create(key='key1', value='value1')
        redirect.query_params.create(key='key2', value='value2')

        # Noise
        redirect_no_params = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='/dest')
        redirect_no_params.sites.add(self.site)
        redirect_params_subset = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='/dest')
        redirect_params_subset.sites.add(self.site)
        redirect_params_subset.query_params.create(key='key1', value='value1')
        redirect_params_superset = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='/dest')
        redirect_params_superset.sites.add(self.site)
        redirect_params_superset.query_params.create(key='key1', value='value1')
        redirect_params_superset.query_params.create(key='key2', value='value2')
        redirect_params_superset.query_params.create(key='key3', value='value3')
        redirect_params_different = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='/dest')
        redirect_params_different.sites.add(self.site)
        redirect_params_different.query_params.create(key='key1', value='valueXXX')
        redirect_params_different.query_params.create(key='key2', value='valueYYY')

        request = self.create_fake_request('http://example.com/origin?key2=value2&key1=value1')
        self.assertEquals(StaticRedirect.objects.get_for_request(request), redirect)

    def test_get_for_request_with_query_params_with_trailing_slash(self):
        redirect = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='/dest')
        redirect.sites.add(self.site)
        redirect.query_params.create(key='key1', value='value1')
        redirect.query_params.create(key='key2', value='value2')

        request = self.create_fake_request('http://example.com/origin/?key2=value2&key1=value1')
        self.assertEquals(StaticRedirect.objects.get_for_request(request), redirect)

    def test_get_for_request_with_query_params_malformed(self):
        redirect = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='/dest')
        redirect.sites.add(self.site)
        redirect.query_params.create(key='key1', value='')

        request = self.create_fake_request('http://example.com/origin?key1')
        self.assertEquals(StaticRedirect.objects.get_for_request(request), redirect)
