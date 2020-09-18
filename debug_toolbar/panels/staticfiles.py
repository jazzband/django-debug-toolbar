from collections import OrderedDict
from os.path import join, normpath

from django.conf import settings
from django.contrib.staticfiles import finders, storage
from django.core.checks import Warning
from django.core.files.storage import get_storage_class
from django.utils.functional import LazyObject
from django.utils.translation import gettext_lazy as _, ngettext as __

from debug_toolbar import panels
from debug_toolbar.utils import ThreadCollector

try:
    import threading
except ImportError:
    threading = None


class StaticFile:
    """
    Representing the different properties of a static file.
    """

    def __init__(self, path):
        self.path = path

    def __str__(self):
        return self.path

    def real_path(self):
        return finders.find(self.path)

    def url(self):
        return storage.staticfiles_storage.url(self.path)


class FileCollector(ThreadCollector):
    def collect(self, path, thread=None):
        # handle the case of {% static "admin/" %}
        if path.endswith("/"):
            return
        super().collect(StaticFile(path), thread)


collector = FileCollector()


class DebugConfiguredStorage(LazyObject):
    """
    A staticfiles storage class to be used for collecting which paths
    are resolved by using the {% static %} template tag (which uses the
    `url` method).
    """

    def _setup(self):

        configured_storage_cls = get_storage_class(settings.STATICFILES_STORAGE)

        class DebugStaticFilesStorage(configured_storage_cls):
            def __init__(self, collector, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.collector = collector

            def url(self, path):
                self.collector.collect(path)
                return super().url(path)

        self._wrapped = DebugStaticFilesStorage(collector)


_original_storage = storage.staticfiles_storage


class StaticFilesPanel(panels.Panel):
    """
    A panel to display the found staticfiles.
    """

    name = "Static files"
    template = "debug_toolbar/panels/staticfiles.html"

    @property
    def title(self):
        return _("Static files (%(num_found)s found, %(num_used)s used)") % {
            "num_found": self.num_found,
            "num_used": self.num_used,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_found = 0
        self._paths = {}

    def enable_instrumentation(self):
        storage.staticfiles_storage = DebugConfiguredStorage()

    def disable_instrumentation(self):
        storage.staticfiles_storage = _original_storage

    @property
    def num_used(self):
        stats = self.get_stats()
        return stats and stats["num_used"]

    nav_title = _("Static files")

    @property
    def nav_subtitle(self):
        num_used = self.num_used
        return __("%(num_used)s file used", "%(num_used)s files used", num_used) % {
            "num_used": num_used
        }

    def process_request(self, request):
        collector.clear_collection()
        return super().process_request(request)

    def generate_stats(self, request, response):
        used_paths = collector.get_collection()
        self._paths[threading.currentThread()] = used_paths

        self.record_stats(
            {
                "num_found": self.num_found,
                "num_used": len(used_paths),
                "staticfiles": used_paths,
                "staticfiles_apps": self.get_staticfiles_apps(),
                "staticfiles_dirs": self.get_staticfiles_dirs(),
                "staticfiles_finders": self.get_staticfiles_finders(),
            }
        )

    def get_staticfiles_finders(self):
        """
        Returns a sorted mapping between the finder path and the list
        of relative and file system paths which that finder was able
        to find.
        """
        finders_mapping = OrderedDict()
        for finder in finders.get_finders():
            try:
                for path, finder_storage in finder.list([]):
                    if getattr(finder_storage, "prefix", None):
                        prefixed_path = join(finder_storage.prefix, path)
                    else:
                        prefixed_path = path
                    finder_cls = finder.__class__
                    finder_path = ".".join([finder_cls.__module__, finder_cls.__name__])
                    real_path = finder_storage.path(path)
                    payload = (prefixed_path, real_path)
                    finders_mapping.setdefault(finder_path, []).append(payload)
                    self.num_found += 1
            except OSError:
                # This error should be captured and presented as a part of run_checks.
                pass
        return finders_mapping

    def get_staticfiles_dirs(self):
        """
        Returns a list of paths to inspect for additional static files
        """
        dirs = []
        for finder in finders.get_finders():
            if isinstance(finder, finders.FileSystemFinder):
                dirs.extend(finder.locations)
        return [(prefix, normpath(dir)) for prefix, dir in dirs]

    def get_staticfiles_apps(self):
        """
        Returns a list of app paths that have a static directory
        """
        apps = []
        for finder in finders.get_finders():
            if isinstance(finder, finders.AppDirectoriesFinder):
                for app in finder.apps:
                    if app not in apps:
                        apps.append(app)
        return apps

    @classmethod
    def run_checks(cls):
        """
        Check that the integration is configured correctly for the panel.

        Specifically look for static files that haven't been collected yet.

        Return a list of :class: `django.core.checks.CheckMessage` instances.
        """
        errors = []
        for finder in finders.get_finders():
            try:
                for path, finder_storage in finder.list([]):
                    finder_storage.path(path)
            except OSError:
                errors.append(
                    Warning(
                        "debug_toolbar requires the STATICFILES_DIRS directories to exist.",
                        hint="Running manage.py collectstatic may help uncover the issue.",
                        id="debug_toolbar.staticfiles.W001",
                    )
                )
        return errors
