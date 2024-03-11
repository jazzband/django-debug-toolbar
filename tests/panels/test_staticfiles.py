from django.conf import settings
from django.contrib.staticfiles import finders

from ..base import BaseTestCase


class StaticFilesPanelTestCase(BaseTestCase):
    panel_id = "StaticFilesPanel"

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
        self.assertEqual(self.panel.num_used, 0)
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
