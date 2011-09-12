from django.conf import settings
from django.template.loader import render_to_string
from django.views.debug import get_safe_settings
from django.utils.translation import ugettext_lazy as _
from debug_toolbar.middleware import DebugToolbarMiddleware
from debug_toolbar.panels import DebugPanel


class SettingsVarsDebugPanel(DebugPanel):
    """
    A panel to display all variables in django.conf.settings
    """
    name = 'SettingsVars'
    has_content = True
    
    def nav_title(self):
        return _('Settings')
    
    def title(self):
        return _('Settings from <code>%s</code>') % settings.SETTINGS_MODULE
    
    def url(self):
        return ''
    
    def process_response(self, request, response):
        self.stats = {
            'settings': get_safe_settings(),
        }
        toolbar = DebugToolbarMiddleware.get_current()
        toolbar.stats['settings_vars'] = self.stats
    
    def content(self):
        context = self.context.copy()
        context.update(self.stats)
        return render_to_string('debug_toolbar/panels/settings_vars.html', context)
