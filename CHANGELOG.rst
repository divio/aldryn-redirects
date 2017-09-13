CHANGELOG
=========

1.2.1 (2017-09-13)
------------------

* Added import / export of redirect entries
* Minor Python 3 compatibility adjustments


1.2.0 (2017-06-08)
------------------

* Changed the redirect lookup to ignore GET parameters


1.1.0 (2017-03-21)
------------------

* Switch from `process_response` to `process_request` in middleware:
  Changes from a "fallback" middleware that only acted on 404s to an
  eager middleware, trying to redirect all requests (including such
  to / without language prefix)


1.0.0 (2016-02-23)
------------------

* Django 1.7/1.8/1.9 compatibility
* Switch from django-hvad to django-parler
* ui tweaks and fixes
