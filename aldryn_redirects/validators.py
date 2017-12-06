# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division
import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from six.moves.urllib.parse import urlparse


def validate_inbound_route(value):
    value = value.strip()
    parsed_value = urlparse(value)

    if parsed_value.scheme or parsed_value.netloc:
        raise ValidationError(_('Do not provide the domain. This will be done automatically based on current site.'))

    if parsed_value.query:
        raise ValidationError(_('Do not provide the query params. Use "Query params" below instead.'))

    if not(value.startswith('/')):
        raise ValidationError(_('Start this field with a slash.'))

    if value.endswith('/'):
        raise ValidationError(_('Do not append a trailing slash.'))

    if not re.match(r'^[a-zA-Z0-9\.\_\-\:\/\?\#\&\=\%]+$', value):
        raise ValidationError(_('Invalid URL provided (invalid characters found).'))

    return value


def validate_outbound_route(value):
    value = value.strip()

    if not re.match(r'^(http://|https://|/)', value):
        raise ValidationError(_('Provide this as either a full url (http://example.com/dest) or a full path (/dest).'))

    if not re.match(r'^[a-zA-Z0-9\.\_\-\:\/\?\#\&\=\%]+$', value):
        raise ValidationError(_('Invalid URL provided (invalid characters found).'))

    return value
