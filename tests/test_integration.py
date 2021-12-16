import os
import re
import unittest

import html5lib
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import signing
from django.core.cache import cache
from django.db import connection
from django.http import HttpResponse
from django.template.loader import get_template
from django.test import RequestFactory
from django.test.utils import override_settings

from debug_toolbar.forms import SignedDataForm
from debug_toolbar.middleware import DebugToolbarMiddleware, show_toolbar
from debug_toolbar.panels import Panel
from debug_toolbar.toolbar import DebugToolbar

from .base import BaseTestCase, IntegrationTestCase
from .views import regular_view

try:
    from selenium import webdriver
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.wait import WebDriverWait
except ImportError:
    webdriver = None


rf = RequestFactory()


class BuggyPanel(Panel):
    def title(self):
        return "BuggyPanel"

    @property
    def content(self):
        raise Exception


@override_settings(DEBUG=True)
class DebugToolbarTestCase(BaseTestCase):
    def test_show_toolbar(self):
        self.assertTrue(show_toolbar(self.request))

    def test_show_toolbar_DEBUG(self):
        with self.settings(DEBUG=False):
            self.assertFalse(show_toolbar(self.request))

    def test_show_toolbar_INTERNAL_IPS(self):
        with self.settings(INTERNAL_IPS=[]):
            self.assertFalse(show_toolbar(self.request))

    def _resolve_stats(self, path):
        # takes stats from Request panel
        self.request.path = path
        panel = self.toolbar.get_panel_by_id("RequestPanel")
        response = panel.process_request(self.request)
        panel.generate_stats(self.request, response)
        return panel.get_stats()

    def test_url_resolving_positional(self):
        stats = self._resolve_stats("/resolving1/a/b/")
        self.assertEqual(stats["view_urlname"], "positional-resolving")
        self.assertEqual(stats["view_func"], "tests.views.resolving_view")
        self.assertEqual(stats["view_args"], ("a", "b"))
        self.assertEqual(stats["view_kwargs"], {})

    def test_url_resolving_named(self):
        stats = self._resolve_stats("/resolving2/a/b/")
        self.assertEqual(stats["view_args"], ())
        self.assertEqual(stats["view_kwargs"], {"arg1": "a", "arg2": "b"})

    def test_url_resolving_mixed(self):
        stats = self._resolve_stats("/resolving3/a/")
        self.assertEqual(stats["view_args"], ("a",))
        self.assertEqual(stats["view_kwargs"], {"arg2": "default"})

    def test_url_resolving_bad(self):
        stats = self._resolve_stats("/non-existing-url/")
        self.assertEqual(stats["view_urlname"], "None")
        self.assertEqual(stats["view_args"], "None")
        self.assertEqual(stats["view_kwargs"], "None")
        self.assertEqual(stats["view_func"], "<no view>")

    def test_middleware_response_insertion(self):
        def get_response(request):
            return regular_view(request, "İ")

        response = DebugToolbarMiddleware(get_response)(self.request)
        # check toolbar insertion before "</body>"
        self.assertContains(response, "</div>\n</body>")

    def test_cache_page(self):
        # Clear the cache before testing the views. Other tests that use cached_view
        # may run earlier and cause fewer cache calls.
        cache.clear()
        self.client.get("/cached_view/")
        self.assertEqual(len(self.toolbar.get_panel_by_id("CachePanel").calls), 3)
        self.client.get("/cached_view/")
        self.assertEqual(len(self.toolbar.get_panel_by_id("CachePanel").calls), 5)

    @override_settings(ROOT_URLCONF="tests.urls_use_package_urls")
    def test_include_package_urls(self):
        """Test urlsconf that uses the debug_toolbar.urls in the include call"""
        # Clear the cache before testing the views. Other tests that use cached_view
        # may run earlier and cause fewer cache calls.
        cache.clear()
        self.client.get("/cached_view/")
        self.assertEqual(len(self.toolbar.get_panel_by_id("CachePanel").calls), 3)
        self.client.get("/cached_view/")
        self.assertEqual(len(self.toolbar.get_panel_by_id("CachePanel").calls), 5)

    def test_low_level_cache_view(self):
        """Test cases when low level caching API is used within a request."""
        self.client.get("/cached_low_level_view/")
        self.assertEqual(len(self.toolbar.get_panel_by_id("CachePanel").calls), 2)
        self.client.get("/cached_low_level_view/")
        self.assertEqual(len(self.toolbar.get_panel_by_id("CachePanel").calls), 3)

    def test_cache_disable_instrumentation(self):
        """
        Verify that middleware cache usages before and after
        DebugToolbarMiddleware are not counted.
        """
        self.assertIsNone(cache.set("UseCacheAfterToolbar.before", None))
        self.assertIsNone(cache.set("UseCacheAfterToolbar.after", None))
        self.client.get("/execute_sql/")
        self.assertEqual(cache.get("UseCacheAfterToolbar.before"), 1)
        self.assertEqual(cache.get("UseCacheAfterToolbar.after"), 1)
        self.assertEqual(len(self.toolbar.get_panel_by_id("CachePanel").calls), 0)

    def test_is_toolbar_request(self):
        self.request.path = "/__debug__/render_panel/"
        self.assertTrue(self.toolbar.is_toolbar_request(self.request))

        self.request.path = "/invalid/__debug__/render_panel/"
        self.assertFalse(self.toolbar.is_toolbar_request(self.request))

        self.request.path = "/render_panel/"
        self.assertFalse(self.toolbar.is_toolbar_request(self.request))

    @override_settings(ROOT_URLCONF="tests.urls_invalid")
    def test_is_toolbar_request_without_djdt_urls(self):
        """Test cases when the toolbar urls aren't configured."""
        self.request.path = "/__debug__/render_panel/"
        self.assertFalse(self.toolbar.is_toolbar_request(self.request))

        self.request.path = "/render_panel/"
        self.assertFalse(self.toolbar.is_toolbar_request(self.request))

    @override_settings(ROOT_URLCONF="tests.urls_invalid")
    def test_is_toolbar_request_override_request_urlconf(self):
        """Test cases when the toolbar URL is configured on the request."""
        self.request.path = "/__debug__/render_panel/"
        self.assertFalse(self.toolbar.is_toolbar_request(self.request))

        # Verify overriding the urlconf on the request is valid.
        self.request.urlconf = "tests.urls"
        self.request.path = "/__debug__/render_panel/"
        self.assertTrue(self.toolbar.is_toolbar_request(self.request))


@override_settings(DEBUG=True)
class DebugToolbarIntegrationTestCase(IntegrationTestCase):
    def test_middleware(self):
        response = self.client.get("/execute_sql/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "djDebug")

    @override_settings(DEFAULT_CHARSET="iso-8859-1")
    def test_non_utf8_charset(self):
        response = self.client.get("/regular/ASCII/")
        self.assertContains(response, "ASCII")  # template
        self.assertContains(response, "djDebug")  # toolbar

        response = self.client.get("/regular/LÀTÍN/")
        self.assertContains(response, "LÀTÍN")  # template
        self.assertContains(response, "djDebug")  # toolbar

    def test_html5_validation(self):
        response = self.client.get("/regular/HTML5/")
        parser = html5lib.HTMLParser()
        content = response.content
        parser.parse(content)
        if parser.errors:
            default_msg = ["Content is invalid HTML:"]
            lines = content.split(b"\n")
            for position, errorcode, datavars in parser.errors:
                default_msg.append("  %s" % html5lib.constants.E[errorcode] % datavars)
                default_msg.append("    %r" % lines[position[0] - 1])
            msg = self._formatMessage(None, "\n".join(default_msg))
            raise self.failureException(msg)

    def test_render_panel_checks_show_toolbar(self):
        def get_response(request):
            return HttpResponse()

        toolbar = DebugToolbar(rf.get("/"), get_response)
        toolbar.store()
        url = "/__debug__/render_panel/"
        data = {"store_id": toolbar.store_id, "panel_id": "VersionsPanel"}

        response = self.client.get(url, data)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        with self.settings(INTERNAL_IPS=[]):
            response = self.client.get(url, data)
            self.assertEqual(response.status_code, 404)
            response = self.client.get(
                url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
            )
            self.assertEqual(response.status_code, 404)

    def test_middleware_render_toolbar_json(self):
        """Verify the toolbar is rendered and data is stored for a json request."""
        self.assertEqual(len(DebugToolbar._store), 0)

        data = {"foo": "bar"}
        response = self.client.get("/json_view/", data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), '{"foo": "bar"}')
        # Check the history panel's stats to verify the toolbar rendered properly.
        self.assertEqual(len(DebugToolbar._store), 1)
        toolbar = list(DebugToolbar._store.values())[0]
        self.assertEqual(
            toolbar.get_panel_by_id("HistoryPanel").get_stats()["data"],
            {"foo": ["bar"]},
        )

    def test_template_source_checks_show_toolbar(self):
        template = get_template("basic.html")
        url = "/__debug__/template_source/"
        data = {
            "template": template.template.name,
            "template_origin": signing.dumps(template.template.origin.name),
        }

        response = self.client.get(url, data)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        with self.settings(INTERNAL_IPS=[]):
            response = self.client.get(url, data)
            self.assertEqual(response.status_code, 404)
            response = self.client.get(
                url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
            )
            self.assertEqual(response.status_code, 404)

    def test_sql_select_checks_show_toolbar(self):
        url = "/__debug__/sql_select/"
        data = {
            "signed": SignedDataForm.sign(
                {
                    "sql": "SELECT * FROM auth_user",
                    "raw_sql": "SELECT * FROM auth_user",
                    "params": "{}",
                    "alias": "default",
                    "duration": "0",
                }
            )
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        with self.settings(INTERNAL_IPS=[]):
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 404)
            response = self.client.post(
                url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
            )
            self.assertEqual(response.status_code, 404)

    def test_sql_explain_checks_show_toolbar(self):
        url = "/__debug__/sql_explain/"
        data = {
            "signed": SignedDataForm.sign(
                {
                    "sql": "SELECT * FROM auth_user",
                    "raw_sql": "SELECT * FROM auth_user",
                    "params": "{}",
                    "alias": "default",
                    "duration": "0",
                }
            )
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        with self.settings(INTERNAL_IPS=[]):
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 404)
            response = self.client.post(
                url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
            )
            self.assertEqual(response.status_code, 404)

    @unittest.skipUnless(
        connection.vendor == "postgresql", "Test valid only on PostgreSQL"
    )
    def test_sql_explain_postgres_json_field(self):
        url = "/__debug__/sql_explain/"
        base_query = (
            'SELECT * FROM "tests_postgresjson" WHERE "tests_postgresjson"."field" @>'
        )
        query = base_query + """ '{"foo": "bar"}'"""
        data = {
            "signed": SignedDataForm.sign(
                {
                    "sql": query,
                    "raw_sql": base_query + " %s",
                    "params": '["{\\"foo\\": \\"bar\\"}"]',
                    "alias": "default",
                    "duration": "0",
                }
            )
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        with self.settings(INTERNAL_IPS=[]):
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 404)
            response = self.client.post(
                url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
            )
            self.assertEqual(response.status_code, 404)

    def test_sql_profile_checks_show_toolbar(self):
        url = "/__debug__/sql_profile/"
        data = {
            "signed": SignedDataForm.sign(
                {
                    "sql": "SELECT * FROM auth_user",
                    "raw_sql": "SELECT * FROM auth_user",
                    "params": "{}",
                    "alias": "default",
                    "duration": "0",
                }
            )
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        with self.settings(INTERNAL_IPS=[]):
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 404)
            response = self.client.post(
                url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
            )
            self.assertEqual(response.status_code, 404)

    @override_settings(DEBUG_TOOLBAR_CONFIG={"RENDER_PANELS": True})
    def test_render_panels_in_request(self):
        """
        Test that panels are are rendered during the request with
        RENDER_PANELS=TRUE
        """
        url = "/regular/basic/"
        response = self.client.get(url)
        self.assertIn(b'id="djDebug"', response.content)
        # Verify the store id is not included.
        self.assertNotIn(b"data-store-id", response.content)
        # Verify the history panel was disabled
        self.assertIn(
            b'<input type="checkbox" data-cookie="djdtHistoryPanel" '
            b'title="Enable for next and successive requests">',
            response.content,
        )
        # Verify the a panel was rendered
        self.assertIn(b"Response headers", response.content)

    @override_settings(DEBUG_TOOLBAR_CONFIG={"RENDER_PANELS": False})
    def test_load_panels(self):
        """
        Test that panels are not rendered during the request with
        RENDER_PANELS=False
        """
        url = "/execute_sql/"
        response = self.client.get(url)
        self.assertIn(b'id="djDebug"', response.content)
        # Verify the store id is included.
        self.assertIn(b"data-store-id", response.content)
        # Verify the history panel was not disabled
        self.assertNotIn(
            b'<input type="checkbox" data-cookie="djdtHistoryPanel" '
            b'title="Enable for next and successive requests">',
            response.content,
        )
        # Verify the a panel was not rendered
        self.assertNotIn(b"Response headers", response.content)

    def test_view_returns_template_response(self):
        response = self.client.get("/template_response/basic/")
        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG_TOOLBAR_CONFIG={"DISABLE_PANELS": set()})
    def test_intcercept_redirects(self):
        response = self.client.get("/redirect/")
        self.assertEqual(response.status_code, 200)
        # Link to LOCATION header.
        self.assertIn(b'href="/regular/redirect/"', response.content)

    def test_server_timing_headers(self):
        response = self.client.get("/execute_sql/")
        server_timing = response["Server-Timing"]
        expected_partials = [
            r'TimerPanel_utime;dur=(\d)*(\.(\d)*)?;desc="User CPU time", ',
            r'TimerPanel_stime;dur=(\d)*(\.(\d)*)?;desc="System CPU time", ',
            r'TimerPanel_total;dur=(\d)*(\.(\d)*)?;desc="Total CPU time", ',
            r'TimerPanel_total_time;dur=(\d)*(\.(\d)*)?;desc="Elapsed time", ',
            r'SQLPanel_sql_time;dur=(\d)*(\.(\d)*)?;desc="SQL 1 queries", ',
            r'CachePanel_total_time;dur=0;desc="Cache 0 Calls"',
        ]
        for expected in expected_partials:
            self.assertTrue(re.compile(expected).search(server_timing))

    def test_auth_login_view_without_redirect(self):
        response = self.client.get("/login_without_redirect/")
        self.assertEqual(response.status_code, 200)
        parser = html5lib.HTMLParser()
        doc = parser.parse(response.content)
        el = doc.find(".//*[@id='djDebug']")
        store_id = el.attrib["data-store-id"]
        response = self.client.get(
            "/__debug__/render_panel/",
            {"store_id": store_id, "panel_id": "TemplatesPanel"},
        )
        self.assertEqual(response.status_code, 200)
        # The key None (without quotes) exists in the list of template
        # variables.
        self.assertIn("None: &#x27;&#x27;", response.json()["content"])


@unittest.skipIf(webdriver is None, "selenium isn't installed")
@unittest.skipUnless(
    "DJANGO_SELENIUM_TESTS" in os.environ, "selenium tests not requested"
)
@override_settings(DEBUG=True)
class DebugToolbarLiveTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.headless = bool(os.environ.get("CI"))
        cls.selenium = webdriver.Firefox(options=options)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def get(self, url):
        self.selenium.get(self.live_server_url + url)

    @property
    def wait(self):
        return WebDriverWait(self.selenium, timeout=3)

    def test_basic(self):
        self.get("/regular/basic/")
        version_panel = self.selenium.find_element_by_id("VersionsPanel")

        # Versions panel isn't loaded
        with self.assertRaises(NoSuchElementException):
            version_panel.find_element_by_tag_name("table")

        # Click to show the versions panel
        self.selenium.find_element_by_class_name("VersionsPanel").click()

        # Version panel loads
        table = self.wait.until(
            lambda selenium: version_panel.find_element_by_tag_name("table")
        )
        self.assertIn("Name", table.text)
        self.assertIn("Version", table.text)

    @override_settings(
        DEBUG_TOOLBAR_CONFIG={
            "DISABLE_PANELS": {"debug_toolbar.panels.redirects.RedirectsPanel"}
        }
    )
    def test_basic_jinja(self):
        self.get("/regular_jinja/basic")
        template_panel = self.selenium.find_element_by_id("TemplatesPanel")

        # Click to show the template panel
        self.selenium.find_element_by_class_name("TemplatesPanel").click()

        self.assertIn("Templates (2 rendered)", template_panel.text)
        self.assertIn("base.html", template_panel.text)
        self.assertIn("jinja2/basic.jinja", template_panel.text)

    @override_settings(
        DEBUG_TOOLBAR_CONFIG={
            "DISABLE_PANELS": {"debug_toolbar.panels.redirects.RedirectsPanel"}
        }
    )
    def test_rerender_on_history_switch(self):
        self.get("/regular_jinja/basic")
        # Make a new request so the history panel has more than one option.
        self.get("/execute_sql/")
        template_panel = self.selenium.find_element_by_id("HistoryPanel")
        # Record the current side panel of buttons for later comparison.
        previous_button_panel = self.selenium.find_element_by_id(
            "djDebugPanelList"
        ).text

        # Click to show the history panel
        self.selenium.find_element_by_class_name("HistoryPanel").click()
        # Click to switch back to the jinja page view snapshot
        list(template_panel.find_elements_by_css_selector("button"))[-1].click()

        current_button_panel = self.selenium.find_element_by_id("djDebugPanelList").text
        # Verify the button side panels have updated.
        self.assertNotEqual(previous_button_panel, current_button_panel)
        self.assertNotIn("1 query", current_button_panel)
        self.assertIn("1 query", previous_button_panel)

    @override_settings(DEBUG_TOOLBAR_CONFIG={"RESULTS_CACHE_SIZE": 0})
    def test_expired_store(self):
        self.get("/regular/basic/")
        version_panel = self.selenium.find_element_by_id("VersionsPanel")

        # Click to show the version panel
        self.selenium.find_element_by_class_name("VersionsPanel").click()

        # Version panel doesn't loads
        error = self.wait.until(
            lambda selenium: version_panel.find_element_by_tag_name("p")
        )
        self.assertIn("Data for this panel isn't available anymore.", error.text)

    @override_settings(
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "OPTIONS": {
                    "loaders": [
                        (
                            "django.template.loaders.cached.Loader",
                            (
                                "django.template.loaders.filesystem.Loader",
                                "django.template.loaders.app_directories.Loader",
                            ),
                        )
                    ]
                },
            }
        ],
    )
    def test_django_cached_template_loader(self):
        self.get("/regular/basic/")
        version_panel = self.selenium.find_element_by_id("TemplatesPanel")

        # Click to show the templates panel
        self.selenium.find_element_by_class_name("TemplatesPanel").click()

        # Templates panel loads
        trigger = self.wait.until(
            lambda selenium: version_panel.find_element_by_css_selector(".remoteCall")
        )
        trigger.click()

        # Verify the code is displayed
        self.wait.until(
            lambda selenium: self.selenium.find_element_by_css_selector(
                "#djDebugWindow code"
            )
        )

    def test_sql_action_and_go_back(self):
        self.get("/execute_sql/")
        sql_panel = self.selenium.find_element_by_id("SQLPanel")
        debug_window = self.selenium.find_element_by_id("djDebugWindow")

        # Click to show the SQL panel
        self.selenium.find_element_by_class_name("SQLPanel").click()

        # SQL panel loads
        button = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".remoteCall"))
        )
        button.click()

        # SQL selected window loads
        self.wait.until(EC.visibility_of(debug_window))
        self.assertIn("SQL selected", debug_window.text)

        # Close the SQL selected window
        debug_window.find_element_by_class_name("djDebugClose").click()
        self.wait.until(EC.invisibility_of_element(debug_window))

        # SQL panel is still visible
        self.assertTrue(sql_panel.is_displayed())

    @override_settings(DEBUG_TOOLBAR_PANELS=["tests.test_integration.BuggyPanel"])
    def test_displays_server_error(self):
        self.get("/regular/basic/")
        debug_window = self.selenium.find_element_by_id("djDebugWindow")
        self.selenium.find_element_by_class_name("BuggyPanel").click()
        self.wait.until(EC.visibility_of(debug_window))
        self.assertEqual(debug_window.text, "»\n500: Internal Server Error")
