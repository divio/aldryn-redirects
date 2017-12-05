from __future__ import unicode_literals

from tablib import Dataset

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.translation import ugettext, ungettext

from parler.admin import TranslatableAdmin

from aldryn_translation_tools.admin import AllTranslationsMixin

from .forms import RedirectsImportForm
from .models import Redirect, StaticRedirect, StaticRedirectInboundRouteQueryParam


class RedirectAdmin(AllTranslationsMixin, TranslatableAdmin):
    list_display = ('old_path',)
    list_filter = ('site',)
    search_fields = ('old_path', 'translations__new_path')
    radio_fields = {'site': admin.VERTICAL}
    export_filename = 'redirects-%Y-%m-%d.csv'
    export_headers = ['Domain', 'Old', 'New', 'Language']

    def get_urls(self):
        from django.conf.urls import url

        def pattern(regex, fn, name):
            args = [regex, self.admin_site.admin_view(fn)]
            url_name = "%s_%s_%s" % (self.opts.app_label, self.opts.model_name, name)
            return url(*args, name=url_name)

        url_patterns = [
            pattern(r'export/$', self.export_view, 'export'),
            pattern(r'import/$', self.import_view, 'import'),
        ]
        return url_patterns + super(RedirectAdmin, self).get_urls()

    def get_form(self, request, obj=None, **kwargs):
        form = super(RedirectAdmin, self).get_form(request, obj=None, **kwargs)
        site_field = form.base_fields['site']

        # the add and change links don't work anyway with admin.VERTICAL radio
        # fields
        site_field.widget.can_add_related = False
        site_field.widget.can_change_related = False

        # if there is only one site, select it by default
        if site_field.queryset.all().count() == 1:
            site_field.initial = site_field.queryset.get()
        return form

    def export_view(self, request):
        dataset = Dataset(headers=self.export_headers)
        filename = timezone.now().date().strftime(self.export_filename)
        redirects = self.get_queryset(request).prefetch_related('translations')

        for r in redirects:
            rows = []
            for translation in r.translations.all():
                rows.append([
                    r.site.domain,
                    r.old_path,
                    translation.new_path,
                    translation.language_code,
                ])
            dataset.extend(rows)

        response = HttpResponse(dataset.csv, content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)
        return response

    def import_view(self, request):
        form = RedirectsImportForm(
            data=request.POST or None,
            files=request.FILES or None,
        )
        opts = self.model._meta

        if form.is_valid():
            url_name = "%s_%s_%s" % (self.opts.app_label, self.opts.model_name, 'changelist')
            success_url = 'admin:{}'.format(url_name)
            new_redirects = form.do_import()
            message = ungettext(
                'Imported %(count)d new redirect',
                'Imported %(count)d new redirects',
                new_redirects
            ) % {'count': new_redirects}
            self.message_user(request, message)
            return redirect(success_url)

        context = {
            'adminform': form,
            'has_change_permission': True,
            'media': self.media + form.media,
            'opts': opts,
            'root_path': reverse('admin:index'),
            'current_app': self.admin_site.name,
            'app_label': opts.app_label,
            'title': ugettext('Import redirects'),
            'original': ugettext('Import redirects'),
            'errors': form.errors,
        }
        return render(request, 'admin/aldryn_redirects/redirect/import_form.html', context)


class StaticRedirectInboundRouteQueryParamInline(admin.TabularInline):
    model = StaticRedirectInboundRouteQueryParam
    verbose_name = 'Query Param'
    verbose_name_plural = 'Query Params'
    extra = 1


class StaticRedirectAdmin(admin.ModelAdmin):
    inlines = [StaticRedirectInboundRouteQueryParamInline, ]
    filter_horizontal = ('sites', )


admin.site.register(Redirect, RedirectAdmin)
admin.site.register(StaticRedirect, StaticRedirectAdmin)
