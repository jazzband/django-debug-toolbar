import os
import unittest

import django
from django.conf import settings
from django.contrib.staticfiles import finders
from django.test.utils import override_settings

from debug_toolbar.panels.staticfiles import StaticFilesPanel

from ..base import BaseTestCase

PATH_DOES_NOT_EXIST = os.path.join(settings.BASE_DIR, "tests", "invalid_static")


class StaticFilesPanelTestCase(BaseTestCase):
    panel_id = StaticFilesPanel.panel_id

    def test_default_case(self):
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        content = self.panel.content
        self.assertIn(
            "django.contrib.staticfiles.finders.AppDirectoriesFinder", content
        )
        self.assertIn(
            "django.contrib.staticfiles.finders.FileSystemFinder (2 files)", content
        )
        self.assertEqual(self.panel.get_stats()["num_used"], 0)
        self.assertNotEqual(self.panel.num_found, 0)
        expected_apps = ["django.contrib.admin", "debug_toolbar"]
        if settings.USE_GIS:
            expected_apps = ["django.contrib.gis"] + expected_apps
        self.assertEqual(self.panel.get_staticfiles_apps(), expected_apps)
        self.assertEqual(
            self.panel.get_staticfiles_dirs(), finders.FileSystemFinder().locations
        )

    def test_insert_content(self):
        """
        Test that the panel only inserts content after generate_stats and
        not the process_request.
        """
        response = self.panel.process_request(self.request)
        # ensure the panel does not have content yet.
        self.assertNotIn(
            "django.contrib.staticfiles.finders.AppDirectoriesFinder",
            self.panel.content,
        )
        self.panel.generate_stats(self.request, response)
        # ensure the panel renders correctly.
        content = self.panel.content
        self.assertIn(
            "django.contrib.staticfiles.finders.AppDirectoriesFinder", content
        )
        self.assertValidHTML(content)

    @unittest.skipIf(django.VERSION >= (4,), "Django>=4 handles missing dirs itself.")
    @override_settings(
        STATICFILES_DIRS=[PATH_DOES_NOT_EXIST] + settings.STATICFILES_DIRS,
        STATIC_ROOT=PATH_DOES_NOT_EXIST,
    )
    def test_finder_directory_does_not_exist(self):
        """Misconfigure the static files settings and verify the toolbar runs.

        The test case is that the STATIC_ROOT is in STATICFILES_DIRS and that
        the directory of STATIC_ROOT does not exist.
        """
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        content = self.panel.content
        self.assertIn(
            "django.contrib.staticfiles.finders.AppDirectoriesFinder", content
        )
        self.assertNotIn(
            "django.contrib.staticfiles.finders.FileSystemFinder (2 files)", content
        )
        self.assertEqual(self.panel.get_stats()["num_used"], 0)
        self.assertNotEqual(self.panel.get_stats()["num_found"], 0)
        expected_apps = ["django.contrib.admin", "debug_toolbar"]
        if settings.USE_GIS:
            expected_apps = ["django.contrib.gis"] + expected_apps
        self.assertEqual(self.panel.get_staticfiles_apps(), expected_apps)
        self.assertEqual(
            self.panel.get_staticfiles_dirs(), finders.FileSystemFinder().locations
        )
