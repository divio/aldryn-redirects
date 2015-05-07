from aldryn_client import forms


class Form(forms.BaseForm):
    def to_settings(self, data, settings):
        settings['MIDDLEWARE_CLASSES'].insert(0, 'aldryn_redirects.middleware.RedirectFallbackMiddleware')
        return settings
