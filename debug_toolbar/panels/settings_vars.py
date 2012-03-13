from django.conf import settings
from django.views.debug import get_safe_settings
from django.utils.translation import ugettext_lazy as _
from debug_toolbar.panels import DebugPanel


class SettingsVarsDebugPanel(DebugPanel):
    """
    A panel to display all variables in django.conf.settings
    """
    name = 'SettingsVars'
    template = 'debug_toolbar/panels/settings_vars.html'
    has_content = True

    def nav_title(self):
        return _('Settings')

    def title(self):
        return _('Settings from <code>%s</code>') % settings.SETTINGS_MODULE

    def url(self):
        return ''

    def process_response(self, request, response):
        self.record_stats({
            'settings': get_safe_settings(),
        })
