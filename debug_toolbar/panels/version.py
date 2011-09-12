import sys

import django
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from debug_toolbar.middleware import DebugToolbarMiddleware
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
        return _('Versions')
    
    def process_response(self, request, response):
        versions = {}
        versions['Python'] = '%d.%d.%d' % sys.version_info[:3]
        for app in settings.INSTALLED_APPS + ['django']:
            name = app.split('.')[-1].replace('_', ' ').capitalize()
            __import__(app)
            app = sys.modules[app]
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
            versions[name] = version
        
        self.stats = {
            'versions': versions,
            'paths': sys.path,
        }
        
        toolbar = DebugToolbarMiddleware.get_current()
        toolbar.stats['version'] = self.stats
    
    def content(self):
        context = self.context.copy()
        context.update(self.stats)
        return render_to_string('debug_toolbar/panels/versions.html', context)
