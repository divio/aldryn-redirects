from django.contrib import admin
from django import forms
from parler.admin import TranslatableAdmin
from aldryn_translation_tools.admin import AllTranslationsMixin

from django.contrib.sites.models import Site
from .models import Redirect


class RedirectAdmin(AllTranslationsMixin, TranslatableAdmin):
    list_display = ('old_path',)
    list_filter = ('site',)
    search_fields = ('old_path', 'new_path')
    radio_fields = {'site': admin.VERTICAL}

    def get_form(self, request, obj=None, **kwargs):
        form = super(RedirectAdmin,self).get_form(request, obj=None, **kwargs)
        site_field = form.base_fields['site']

        # the add and change links don't work anyway with admin.VERTICAL radio
        # fields
        site_field.widget.can_add_related = False
        site_field.widget.can_change_related = False

        # if there is only one site, select it by default
        if site_field.queryset.all().count() == 1:
            site_field.initial = site_field.queryset.get()
        return form


admin.site.register(Redirect, RedirectAdmin)
