################
Aldryn Redirects
################

This is a modified version of django's ``django.contrib.redirects`` app that
supports language dependant target URLs, using ``django-parler``.

This is useful for cases in which another middleware strips the language
prefix from the URL, like django CMS. It allows to define different urls to
redirect to, depending on the users language.

************
Installation
************

Aldryn Platform Users
#####################

To install the addon on Aldryn, all you need to do is follow this
`installation link <https://control.aldryn.com/control/?select_project_for_addon=aldryn-redirects>`_
on the Aldryn Marketplace and follow the instructions.

Manually you can:

#. Choose a site you want to install the add-on to from the dashboard.
#. Go to Apps > Install App
#. Click Install next to the Aldryn Redirects app.
#. Redeploy the site.


Manual Installation
###################


```bash
pip install aldryn-redirects
```

Follow the `setup instructions for django-parler <http://django-parler.readthedocs.org/>`_.

```python

# settings.py

INSTALLED_APPS += [
    'parler',
    'aldryn_redirects'
]

# add the middleware somewhere near the top of MIDDLEWARE_CLASSES

MIDDLEWARE_CLASSES.insert(
    0, 'aldryn_redirects.middleware.RedirectFallbackMiddleware')
```
