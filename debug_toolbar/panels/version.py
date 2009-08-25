import django
from django.utils.translation import ugettext_lazy as _
from debug_toolbar.panels import DebugPanel

class VersionDebugPanel(DebugPanel):
    """
    Panel that displays the Django version.
    """
    name = 'Version'

    def nav_title(self):
        return _('Django Version')

    def nav_subtitle(self):
        return django.get_version()

    def url(self):
        return ''

    def content(self):
        return ''
