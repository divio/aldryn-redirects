#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

HELPER_SETTINGS = {
    'MIDDLEWARE': [
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
        }],
        2: [{
            'code': 'pt-br',
            'name': 'Brazilian Portugues',
        }],
    },
    'LANGUAGE_CODE': 'en',
    'LANGUAGES': [
        ('en', 'English'),
        ('pt-br', 'Brazilian Portugues'),
    ],
}


def run():
    from djangocms_helper import runner
    runner.cms('aldryn_redirects')


if __name__ == '__main__':
    run()
