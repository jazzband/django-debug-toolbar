from django.conf import settings
from django.views.debug import get_safe_settings

class DebugSettings(object):

    def module_name(self):
        return settings.SETTINGS_MODULE

    def available_settings(self):
        return get_safe_settings()
