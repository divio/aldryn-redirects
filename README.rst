**Deprecated**

This project is no longer supported.

Divio will undertake no further development or maintenance of this project. If you are interested in continuing to develop it, use the fork functionality from GitHub. We are not able to transfer ownership of the repository to another party.

Please have a look at alternatives such as Djangos `redirects app <https://docs.djangoproject.com/en/dev/ref/contrib/redirects/>`_.

################
Aldryn Redirects
################

This is a modified version of Django's ``django.contrib.redirects`` app that
supports language-dependent target URLs, using ``django-parler``.

This is useful for cases in which another middleware strips the language
prefix from the URL, like django CMS. It allows to define different urls to
redirect to, depending on the user's language.

************
Installation
************

Aldryn Platform Users
#####################

To install the addon on Aldryn, all you need to do is follow this
`installation link <https://control.aldryn.com/control/?select_project_for_addon=aldryn-redirects>`_
on the Aldryn Marketplace and follow the instructions.

Manually you can:

#. Choose a site you want to install the Addon to from the dashboard.
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
