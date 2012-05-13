import sys

import django
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict
from django.utils.importlib import import_module

from debug_toolbar.panels import DebugPanel


class VersionDebugPanel(DebugPanel):
    """
    Panel that displays the Django version.
    """
    name = 'Version'
    template = 'debug_toolbar/panels/versions.html'
    has_content = True

    def nav_title(self):
        return _('Versions')

    def nav_subtitle(self):
        return 'Django %s' % django.get_version()

    def url(self):
        return ''

    def title(self):
        return _('Versions')

    def process_response(self, request, response):
        versions = [('Python', '%d.%d.%d' % sys.version_info[:3])]
        for app in list(settings.INSTALLED_APPS) + ['django']:
            name = app.split('.')[-1].replace('_', ' ').capitalize()
            app = import_module(app)
            if hasattr(app, 'get_version'):
                get_version = app.get_version
                if callable(get_version):
                    version = get_version()
                else:
                    version = get_version
            elif hasattr(app, 'VERSION'):
                version = app.VERSION
            elif hasattr(app, '__version__'):
                version = app.__version__
            else:
                continue
            if isinstance(version, (list, tuple)):
                version = '.'.join(str(o) for o in version)
            versions.append((name, version))
            versions = sorted(versions, key=lambda version: version[0])

        self.record_stats({
            'versions': SortedDict(versions),
            'paths': sys.path,
        })
