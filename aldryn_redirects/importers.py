from collections import defaultdict

from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .models import Redirect, StaticRedirect
from .utils import get_query_params_dict, remove_query_params


class FlattenErrorMixin(object):

    def flatten_error(self, e):
        result = []
        for key, values in e.message_dict.items():
            for value in values:
                result.append('{}: {}'.format(key, value))

        return '\n'.join(result)


class RedirectImporter(FlattenErrorMixin, object):

    def __init__(self):
        self.sites_per_domain = {site.domain: site for site in Site.objects.all()}

    def get_existing_redirects(self, site, paths):
        redirects = (
            Redirect
            .objects
            .filter(site=site, old_path__in=paths)
            .prefetch_related('translations')
        )
        existing_redirects = defaultdict(dict)

        for redirect in redirects:
            translations = redirect.translations.all()
            redirect._languages = [trans.language_code for trans in translations]
            existing_redirects[redirect.old_path] = redirect
        return existing_redirects

    def import_from_dataset(self, dataset):
        imported_redirects = defaultdict(lambda: defaultdict(dict))

        for row in dataset:
            domain, old_path, new_path, language = row[:4]
            imported_redirects[domain][old_path][language] = new_path

        sites = Site.objects.filter(domain__in=imported_redirects)
        create_redirect = Redirect.objects.create

        for site in sites.iterator():
            _redirects = imported_redirects[site.domain]
            existing_redirects = self.get_existing_redirects(site, list(_redirects.keys()))

            for path in _redirects:
                if path not in existing_redirects:
                    # creates redirect master object
                    redirect = create_redirect(site=site, old_path=path)
                    redirect._languages = []
                    existing_redirects[path] = redirect
                else:
                    redirect = existing_redirects[path]

                for language, new_path in _redirects[path].items():
                    if language not in redirect._languages:
                        redirect._languages.append(language)
                        redirect.translations.create(language_code=language, new_path=new_path)

    def validate_row(self, row):
        if len(row) < 4:
            raise ValidationError(_(
                'malformed row. Row must contain site (required), '
                'old_path (required), new_path (optional) and language_code (required).'
            ))

        domain, old_path, new_path, language = [x.strip() for x in row[:4]]

        if domain not in self.sites_per_domain.keys():
            raise ValidationError(_('domain not found.'))

        redirect = Redirect(site=self.sites_per_domain[domain], old_path=old_path)
        try:
            redirect.full_clean(validate_unique=False)
        except ValidationError as e:
            raise ValidationError(self.flatten_error(e))

        redirect_translation = redirect.translations.model(master=redirect, language_code=language, new_path=new_path)
        try:
            redirect_translation.full_clean(validate_unique=False)
        except ValidationError as e:
            raise ValidationError(self.flatten_error(e))


class StaticRedirectImporter(FlattenErrorMixin, object):

    def __init__(self):
        self.sites_per_domain = {site.domain: site for site in Site.objects.all()}

    def import_from_dataset(self, dataset):
        for row in dataset:
            domain, inbound_route, outbound_route = row[:3]
            site = self.sites_per_domain[domain]

            query_params = get_query_params_dict(inbound_route)
            if query_params:
                inbound_route = remove_query_params(inbound_route)

            existing_redirect_updated = False
            dupe = StaticRedirect.objects.filter(inbound_route=inbound_route, outbound_route=outbound_route).first()
            if dupe:
                dupe_query_params = dupe.query_params.as_dict()
                if dupe_query_params == query_params:
                    dupe.sites.add(site)
                    existing_redirect_updated = True

            if not existing_redirect_updated:
                redirect = StaticRedirect.objects.create(inbound_route=inbound_route, outbound_route=outbound_route)
                redirect.sites.add(site)
                for key, value in query_params.items():
                    redirect.query_params.create(key=key, value=value)

    def validate_row(self, row):
        if len(row) < 3:
            raise ValidationError(_(
                'malformed row. Row must contain site (required), '
                'redirect_from (required) and redirect_to (required).'
            ))

        domain, inbound_route, outbound_route = [x.strip() for x in row[:3]]

        query_params = get_query_params_dict(inbound_route)
        if query_params:
            inbound_route = remove_query_params(inbound_route)

        if domain not in self.sites_per_domain.keys():
            raise ValidationError(_('domain not found.'))

        redirect = StaticRedirect(inbound_route=inbound_route, outbound_route=outbound_route)
        try:
            redirect.full_clean()
        except ValidationError as e:
            raise ValidationError(self.flatten_error(e))

        for dupe in StaticRedirect.objects.filter(inbound_route=inbound_route, outbound_route=outbound_route):
            dupe_query_params = dupe.query_params.as_dict()
            if (dupe_query_params == query_params) and (dupe.sites.filter(domain=domain).exists()):
                admin_url = dupe.get_admin_change_url()
                raise ValidationError(
                    _('Rule duplicated with <a href="{}" target="_blank">this one</a>').format(admin_url)
                )
