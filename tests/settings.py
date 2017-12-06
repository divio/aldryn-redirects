#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

HELPER_SETTINGS = {
    'MIDDLEWARE_CLASSES': [
        'aldryn_redirects.middleware.RedirectFallbackMiddleware',
    ],
    'INSTALLED_APPS': [
    ],
    'ALLOWED_HOSTS': [
        'localhost'
    ],
    'CMS_LANGUAGES': {
        1: [{
            'code': 'en',
            'name': 'English',
        }]
    },
    'LANGUAGE_CODE': 'en',
    'DATA_UPLOAD_MAX_NUMBER_FIELDS': 10000,
}


def run():
    from djangocms_helper import runner
    runner.cms('aldryn_redirects')


if __name__ == '__main__':
    run()
