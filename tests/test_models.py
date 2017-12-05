# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test.client import RequestFactory

from aldryn_redirects.models import StaticRedirect


class StaticRedirectTestCase(TestCase):
    def setUp(self, *args, **kwargs):
        super(StaticRedirectTestCase, self).setUp(*args, **kwargs)

        self.request = RequestFactory().get('http://example.com/path?query1=param1')
        self.site = Site.objects.get()
        self.request.site = self.site

    def test_get_outbound_url_with_full_domain_present(self):
        redirect = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='http://my.cool/destination')
        self.assertEquals(redirect.get_outbound_url(self.request), redirect.outbound_route)

    def test_get_outbound_url_without_full_domain_present(self):
        redirect = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='/destination')
        self.assertEquals(redirect.get_outbound_url(self.request), 'http://example.com/destination')

    def test_inbound_route_sanity(self):
        redirect = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='/destination')
        redirect.clean_fields()  # Nothing raised

        redirect.inbound_route = 'http://example.com/origin'
        self.assertRaises(ValidationError, redirect.clean_fields)

        redirect.inbound_route = '/origin?key1=value1'
        self.assertRaises(ValidationError, redirect.clean_fields)

        redirect.inbound_route = 'origin'
        self.assertRaises(ValidationError, redirect.clean_fields)

        redirect.inbound_route = '/origin/'
        self.assertRaises(ValidationError, redirect.clean_fields)

    def test_outbound_route_sanity(self):
        redirect = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='/destination')
        redirect.clean_fields()  # Nothing raised

        redirect.outbound_route = 'http://example.com/destination'
        redirect.clean_fields()  # Nothing raised

        redirect.outbound_route = 'https://example.com/destination'
        redirect.clean_fields()  # Nothing raised

        redirect.outbound_route = '/destination'
        redirect.clean_fields()  # Nothing raised

        redirect.outbound_route = '/destination/'
        redirect.clean_fields()  # Nothing raised

        redirect.outbound_route = '/destination/?xxx=yyy'
        redirect.clean_fields()  # Nothing raised

        redirect.outbound_route = 'www.google.com/destination/?xxx=yyy'
        self.assertRaises(ValidationError, redirect.clean_fields)
