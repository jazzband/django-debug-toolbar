from django.template.loader import render_to_string
from debug_toolbar.panels import DebugPanel
from django.conf import settings
from django.views.debug import get_safe_settings

class SettingsVarsDebugPanel(DebugPanel):
    """
    A panel to display all variables in django.conf.settings
    """
    name = 'SettingsVars'
    has_content = True

    def title(self):
        return 'Settings Vars'

    def url(self):
        return ''

    def content(self):
        import logging
        settings_dict = get_safe_settings()
        context = {
            'settings': settings_dict,
        }
        return render_to_string('debug_toolbar/panels/settings_vars.html', context)