import sys
from django import get_version
from django.conf import settings

class DebugVersions(object):

    def django_version(self):
        return get_version()

    def get_versions(self):
        versions = {}
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
        return versions

    def get_paths(self):
        return sys.path
