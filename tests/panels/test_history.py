import html

from django.test import RequestFactory, override_settings
from django.urls import resolve, reverse

from debug_toolbar.forms import SignedDataForm
from debug_toolbar.store import store

from ..base import BaseTestCase, IntegrationTestCase

rf = RequestFactory()


class HistoryPanelTestCase(BaseTestCase):
    panel_id = "HistoryPanel"

    def test_disabled(self):
        config = {"DISABLE_PANELS": {"debug_toolbar.panels.history.HistoryPanel"}}
        self.assertTrue(self.panel.enabled)
        with self.settings(DEBUG_TOOLBAR_CONFIG=config):
            self.assertFalse(self.panel.enabled)

    def test_post(self):
        self.request = rf.post("/", data={"foo": "bar"})
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        data = self.panel.get_stats()["data"]
        self.assertEqual(data["foo"], "bar")

    def test_post_json(self):
        for data, expected_stats_data in (
            ({"foo": "bar"}, {"foo": "bar"}),
            ("", {}),  # Empty JSON
            ("'", {}),  # Invalid JSON
        ):
            with self.subTest(data=data):
                self.request = rf.post(
                    "/",
                    data=data,
                    content_type="application/json",
                    CONTENT_TYPE="application/json",  # Force django test client to add the content-type even if no data
                )
                response = self.panel.process_request(self.request)
                self.panel.generate_stats(self.request, response)
                data = self.panel.get_stats()["data"]
                self.assertDictEqual(data, expected_stats_data)

    def test_urls(self):
        self.assertEqual(
            reverse("djdt:history_sidebar"),
            "/__debug__/history_sidebar/",
        )
        self.assertEqual(
            resolve("/__debug__/history_sidebar/").url_name,
            "history_sidebar",
        )
        self.assertEqual(
            reverse("djdt:history_refresh"),
            "/__debug__/history_refresh/",
        )
        self.assertEqual(
            resolve("/__debug__/history_refresh/").url_name,
            "history_refresh",
        )


@override_settings(DEBUG=True)
class HistoryViewsTestCase(IntegrationTestCase):
    PANEL_KEYS = {
        "VersionsPanel",
        "TimerPanel",
        "SettingsPanel",
        "HeadersPanel",
        "RequestPanel",
        "SQLPanel",
        "StaticFilesPanel",
        "TemplatesPanel",
        "CachePanel",
        "SignalsPanel",
        "LoggingPanel",
        "ProfilingPanel",
    }

    def test_history_panel_integration_content(self):
        """Verify the history panel's content renders properly.."""
        self.assertEqual(len(store.all()), 0)

        data = {"foo": "bar"}
        self.client.get("/json_view/", data, content_type="application/json")

        # Check the history panel's stats to verify the toolbar rendered properly.
        self.assertEqual(len(store.all()), 1)
        toolbar = list(store.all())[0][1]
        content = toolbar.get_panel_by_id("HistoryPanel").content
        self.assertIn("bar", content)

    def test_history_sidebar_invalid(self):
        response = self.client.get(reverse("djdt:history_sidebar"))
        self.assertEqual(response.status_code, 400)

        self.client.get("/json_view/")
        store_id = list(store.all())[0][0]
        data = {"signed": SignedDataForm.sign({"store_id": store_id}) + "invalid"}
        response = self.client.get(reverse("djdt:history_sidebar"), data=data)
        self.assertEqual(response.status_code, 400)

    def test_history_sidebar_hash(self):
        """Validate the hashing mechanism."""
        self.client.get("/json_view/")
        store_id = list(store.all())[0][0]
        data = {"signed": SignedDataForm.sign({"store_id": store_id})}
        response = self.client.get(reverse("djdt:history_sidebar"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.json()),
            self.PANEL_KEYS,
        )

    @override_settings(
        DEBUG_TOOLBAR_CONFIG={"RESULTS_CACHE_SIZE": 1, "RENDER_PANELS": False}
    )
    def test_history_sidebar_expired_store_id(self):
        """Validate the history sidebar view."""
        self.client.get("/json_view/")
        store_id = list(store.all())[0][0]
        data = {"signed": SignedDataForm.sign({"store_id": store_id})}
        response = self.client.get(reverse("djdt:history_sidebar"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.json()),
            self.PANEL_KEYS,
        )
        self.client.get("/json_view/")

        # Querying previous store_id should still work
        data = {"signed": SignedDataForm.sign({"store_id": store_id})}
        response = self.client.get(reverse("djdt:history_sidebar"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.json()),
            self.PANEL_KEYS,
        )

        # Querying with latest store_id
        latest_store_id = list(store.all())[-1][0]
        self.assertNotEqual(latest_store_id, store_id)
        data = {"signed": SignedDataForm.sign({"store_id": latest_store_id})}
        response = self.client.get(reverse("djdt:history_sidebar"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.json()),
            self.PANEL_KEYS,
        )

    def test_history_refresh_invalid_signature(self):
        response = self.client.get(reverse("djdt:history_refresh"))
        self.assertEqual(response.status_code, 400)

        data = {"signed": "eyJzdG9yZV9pZCI6ImZvbyIsImhhc2giOiI4YWFiMzIzZGZhODIyMW"}
        response = self.client.get(reverse("djdt:history_refresh"), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(b"Invalid signature", response.content)

    def test_history_refresh(self):
        """Verify refresh history response has request variables."""
        self.client.get("/json_view/", {"foo": "bar"}, content_type="application/json")
        data = {"signed": SignedDataForm.sign({"store_id": "foo"})}
        response = self.client.get(reverse("djdt:history_refresh"), data=data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["requests"]), 1)

        store_id = list(store.all())[0][0]
        signature = SignedDataForm.sign({"store_id": store_id})
        self.assertIn(html.escape(signature), data["requests"][0]["content"])

        for val in ["foo", "bar"]:
            self.assertIn(val, data["requests"][0]["content"])
