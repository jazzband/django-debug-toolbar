from unittest.mock import patch

from django.test import RequestFactory, override_settings
from django.urls import resolve, reverse

from debug_toolbar.panels.history.panel import CLEANSED_SUBSTITUTE

from ..base import BaseTestCase, IntegrationTestCase

rf = RequestFactory()


class HistoryPanelTestCase(BaseTestCase):
    panel_id = "HistoryPanel"

    def test_disabled(self):
        config = {"DISABLE_PANELS": {"debug_toolbar.panels.history.HistoryPanel"}}
        self.assertTrue(self.panel.enabled)
        with self.settings(DEBUG_TOOLBAR_CONFIG=config):
            self.assertFalse(self.panel.enabled)

    def test_post_cleansing(self):
        self.request = rf.post("/", data={"foo": "bar"})
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        self.assertIn(CLEANSED_SUBSTITUTE, self.panel.get_stats()["post"])

    def test_urls(self):
        self.assertEqual(
            reverse("djdt:history_sidebar"), "/__debug__/history_sidebar/",
        )
        self.assertEqual(
            resolve("/__debug__/history_sidebar/").url_name, "history_sidebar",
        )

    @override_settings(DEBUG_TOOLBAR_CONFIG={"HISTORY_POST_TRUNCATE_LENGTH": 11})
    def test_truncate_length_setting(self):
        self.toolbar.store()
        self.request = rf.post("/", data={"foo": "bar"})
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        self.assertIn("foo…", self.panel.content)
        self.assertNotIn(CLEANSED_SUBSTITUTE, self.panel.content)


class HistoryViewsTestCase(IntegrationTestCase):
    @override_settings(DEBUG=True)
    def test_history_sidebar_invalid(self):
        response = self.client.post(reverse("djdt:history_sidebar"))
        self.assertEqual(response.status_code, 400)

        data = {
            "store_id": "foo",
            "hash": "invalid",
        }
        response = self.client.post(reverse("djdt:history_sidebar"), data=data)
        self.assertEqual(response.status_code, 400)

    @override_settings(DEBUG=True)
    @patch("debug_toolbar.panels.history.views.DebugToolbar.fetch")
    def test_history_sidebar_hash(self, fetch):
        """Validate the hashing mechanism."""
        fetch.return_value.panels = []
        data = {
            "store_id": "foo",
            "hash": "3280d66a3cca10098a44907c5a1fd255265eed31",
        }
        response = self.client.post(reverse("djdt:history_sidebar"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {})
