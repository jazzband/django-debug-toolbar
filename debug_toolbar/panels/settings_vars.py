from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from debug_toolbar.panels import DebugPanel
from debug_toolbar.debug.settings_vars import DebugSettings

class SettingsVarsDebugPanel(DebugPanel):
    """
    A panel to display all variables in django.conf.settings
    """
    name = 'SettingsVars'
    has_content = True

    def __init__(self, context={}):
        super(SettingsVarsDebugPanel, self).__init__(context)
        self.settings = DebugSettings()

    def nav_title(self):
        return _('Settings')

    def title(self):
        return _('Settings from <code>%s</code>') % self.settings.module_name()

    def url(self):
        return ''

    def content(self):
        context = self.context.copy()
        context.update({
            'settings': self.settings.available_settings(),
        })
        return render_to_string('debug_toolbar/panels/settings_vars.html', context)
