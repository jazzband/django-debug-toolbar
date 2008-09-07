import django
from debug_toolbar.panels import DebugPanel

class VersionDebugPanel(DebugPanel):
    """
    Panel that displays the Django version.
    """
    name = 'Version'
    
    def title(self):
        return 'Version: %s' % (django.get_version())

    def url(self):
        return ''

    def content(self):
        return ''
