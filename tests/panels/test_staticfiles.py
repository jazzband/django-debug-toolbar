from django.conf import settings
from django.contrib.staticfiles import finders
from django.shortcuts import render
from django.test import AsyncRequestFactory

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

    async def test_store_staticfiles_with_async_context(self):
        async def get_response(request):
            # template contains one static file
            return render(request, "staticfiles/async_static.html")

        self._get_response = get_response
        async_request = AsyncRequestFactory().get("/")
        response = await self.panel.process_request(async_request)
        self.panel.generate_stats(self.request, response)
        self.assertNotEqual(self.panel.num_used, 0)

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
