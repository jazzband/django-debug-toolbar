import django
from debug_toolbar.panels import DebugPanel

class VersionDebugPanel(DebugPanel):
    """
    Panel that displays the Django version.
    """
    def title(self):
        return 'Version'

    def url(self):
        return ''

    def content(self):
        return django.get_version()
