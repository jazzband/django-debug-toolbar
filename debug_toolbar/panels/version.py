import django
from debug_toolbar.panels import DebugPanel

class VersionDebugPanel(DebugPanel):
    """
    Panel that displays the Django version.
    """
    name = 'Version'

    def nav_title(self):
        return 'Django Version'

    def nav_subtitle(self):
        return django.get_version()

    def url(self):
        return ''

    def content(self):
        return ''
