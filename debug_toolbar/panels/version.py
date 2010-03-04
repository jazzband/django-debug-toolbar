from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from debug_toolbar.panels import DebugPanel
from debug_toolbar.debug.version import DebugVersions

class VersionDebugPanel(DebugPanel):
    """
    Panel that displays the Django version.
    """
    name = 'Version'
    has_content = True

    def __init__(self, context={}):
        super(VersionDebugPanel, self).__init__(context)
        self.debug_version = DebugVersions()

    def nav_title(self):
        return _('Versions')

    def nav_subtitle(self):
        return 'Django %s' % self.debug_version.django_version()

    def url(self):
        return ''

    def title(self):
        return _('Versions')

    def content(self):
        context = self.context.copy()
        context.update({
            'versions': self.debug_version.get_versions(),
            'paths': self.debug_version.get_paths(),
        })
        return render_to_string('debug_toolbar/panels/versions.html', context)
