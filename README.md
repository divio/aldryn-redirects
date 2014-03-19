# Aldryn Redirects

This is a modified version of django's ``django.contrib.redirects`` app that
supports language dependant target URLs, using ``django-hvad``.

This is useful for cases in which another middleware strips the language
prefix from the URL, like django CMS.

## Installation:

```bash
pip install django-hvad aldryn-redirects
```


```python

# settings.py

INSTALLED_APPS += [
    'hvad',
    'aldryn_redirects'
]

MIDDLEWARE_CLASSES += [
    'aldryn_redirects.middleware.RedirectFallbackMiddleware'
]
```
