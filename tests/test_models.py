# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.test import TestCase

from aldryn_redirects.models import StaticRedirect


class StaticRedirectTestCase(TestCase):
    def setUp(self, *args, **kwargs):
        super(StaticRedirectTestCase, self).setUp(*args, **kwargs)
        self.site = Site.objects.get()

    def test_get_outbound_url_with_full_domain_present(self):
        redirect = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='http://my.cool/destination')
        self.assertEquals(redirect.get_outbound_url('http://www.example.com'), redirect.outbound_route)

    def test_get_outbound_url_without_full_domain_present(self):
        redirect = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='/destination')
        self.assertEquals(redirect.get_outbound_url('http://www.example.com'), 'http://www.example.com/destination')

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

        redirect.inbound_route = '/<script>hello</script>'
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

        redirect.outbound_route = '/<script>hello</script>'
        self.assertRaises(ValidationError, redirect.clean_fields)

    def test_site_deletion_keeps_redirect(self):
        redirect = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='http://my.cool/destination')
        redirect.sites.add(self.site)
        Site.objects.all().delete()

        self.assertTrue(StaticRedirect.objects.filter(id=redirect.id).exists())
        self.assertEquals(redirect.sites.count(), 0)

    def test_redirect_deletion_keeps_site(self):
        redirect = StaticRedirect.objects.create(inbound_route='/origin', outbound_route='http://my.cool/destination')
        redirect.sites.add(self.site)
        site_count = Site.objects.count()
        StaticRedirect.objects.all().delete()

        self.assertEquals(Site.objects.count(), site_count)
