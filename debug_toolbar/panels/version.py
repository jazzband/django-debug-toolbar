import sys

import django
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

import debug_toolbar
from debug_toolbar.panels import DebugPanel


class VersionDebugPanel(DebugPanel):
    """
    Panel that displays the Django version.
    """
    name = 'Version'
    has_content = True

    def nav_title(self):
        return _('Versions')

    def nav_subtitle(self):
        return 'Django %s' % django.get_version()

    def url(self):
        return ''
    
    def title(self):
        return 'Versions'

    def content(self):
        versions = {
            'Django': django.get_version(),
            'Django Debug Toolbar': debug_toolbar.__version__,
        }
        return render_to_string('debug_toolbar/panels/versions.html', {
            'versions': versions,
            'paths': sys.path,
        })
