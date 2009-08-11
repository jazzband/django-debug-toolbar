import django
from debug_toolbar.panels import DebugPanel

class VersionDebugPanel(DebugPanel):
    """
    Panel that displays the Django version.
    """
    name = 'Version'

    def title(self):
        return 'Django Version'

    def subtitle(self):
        return django.get_version()

    def url(self):
        return ''

    def content(self):
        return ''
