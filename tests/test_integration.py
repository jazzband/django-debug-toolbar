# coding: utf-8

from __future__ import absolute_import, unicode_literals

import os
import unittest

import html5lib
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import signing
from django.core.checks import Warning, run_checks
from django.template.loader import get_template
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.test.utils import override_settings

from debug_toolbar.middleware import DebugToolbarMiddleware, show_toolbar
from debug_toolbar.toolbar import DebugToolbar

from .base import BaseTestCase
from .views import regular_view

try:
    from selenium import webdriver
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.support.wait import WebDriverWait
except ImportError:
    webdriver = None


rf = RequestFactory()


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
        panel.process_request(self.request)
        panel.process_response(self.request, self.response)
        panel.generate_stats(self.request, self.response)
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

    # Django doesn't guarantee that process_request, process_view and
    # process_response always get called in this order.

    def test_middleware_view_only(self):
        DebugToolbarMiddleware().process_view(
            self.request, regular_view, ("title",), {}
        )

    def test_middleware_response_only(self):
        DebugToolbarMiddleware().process_response(self.request, self.response)

    def test_middleware_response_insertion(self):
        resp = regular_view(self.request, "İ")
        DebugToolbarMiddleware().process_response(self.request, resp)
        # check toolbar insertion before "</body>"
        self.assertContains(resp, "</div>\n</body>")

    def test_cache_page(self):
        self.client.get("/cached_view/")
        self.assertEqual(len(self.toolbar.get_panel_by_id("CachePanel").calls), 3)
        self.client.get("/cached_view/")
        self.assertEqual(len(self.toolbar.get_panel_by_id("CachePanel").calls), 5)


@override_settings(DEBUG=True)
class DebugToolbarIntegrationTestCase(TestCase):
    def test_middleware(self):
        response = self.client.get("/execute_sql/")
        self.assertEqual(response.status_code, 200)

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
        toolbar = DebugToolbar(None)
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
            "sql": "SELECT * FROM auth_user",
            "raw_sql": "SELECT * FROM auth_user",
            "params": "{}",
            "alias": "default",
            "duration": "0",
            "hash": "6e12daa636b8c9a8be993307135458f90a877606",
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
            "sql": "SELECT * FROM auth_user",
            "raw_sql": "SELECT * FROM auth_user",
            "params": "{}",
            "alias": "default",
            "duration": "0",
            "hash": "6e12daa636b8c9a8be993307135458f90a877606",
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
            "sql": "SELECT * FROM auth_user",
            "raw_sql": "SELECT * FROM auth_user",
            "params": "{}",
            "alias": "default",
            "duration": "0",
            "hash": "6e12daa636b8c9a8be993307135458f90a877606",
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
    def test_data_store_id_not_rendered_when_none(self):
        url = "/regular/basic/"
        response = self.client.get(url)
        self.assertIn(b'id="djDebug"', response.content)
        self.assertNotIn(b"data-store-id", response.content)

    def test_view_returns_template_response(self):
        response = self.client.get("/template_response/basic/")
        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG_TOOLBAR_CONFIG={"DISABLE_PANELS": set()})
    def test_incercept_redirects(self):
        response = self.client.get("/redirect/")
        self.assertEqual(response.status_code, 200)
        # Link to LOCATION header.
        self.assertIn(b'href="/regular/redirect/"', response.content)


@unittest.skipIf(webdriver is None, "selenium isn't installed")
@unittest.skipUnless(
    "DJANGO_SELENIUM_TESTS" in os.environ, "selenium tests not requested"
)
@override_settings(DEBUG=True)
class DebugToolbarLiveTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(DebugToolbarLiveTestCase, cls).setUpClass()
        cls.selenium = webdriver.Firefox()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(DebugToolbarLiveTestCase, cls).tearDownClass()

    def test_basic(self):
        self.selenium.get(self.live_server_url + "/regular/basic/")
        version_panel = self.selenium.find_element_by_id("VersionsPanel")

        # Versions panel isn't loaded
        with self.assertRaises(NoSuchElementException):
            version_panel.find_element_by_tag_name("table")

        # Click to show the versions panel
        self.selenium.find_element_by_class_name("VersionsPanel").click()

        # Version panel loads
        table = WebDriverWait(self.selenium, timeout=10).until(
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
        self.selenium.get(self.live_server_url + "/regular_jinja/basic")
        template_panel = self.selenium.find_element_by_id("TemplatesPanel")

        # Click to show the template panel
        self.selenium.find_element_by_class_name("TemplatesPanel").click()

        self.assertIn("Templates (1 rendered)", template_panel.text)
        self.assertIn("jinja2/basic.jinja", template_panel.text)

    @override_settings(DEBUG_TOOLBAR_CONFIG={"RESULTS_CACHE_SIZE": 0})
    def test_expired_store(self):
        self.selenium.get(self.live_server_url + "/regular/basic/")
        version_panel = self.selenium.find_element_by_id("VersionsPanel")

        # Click to show the version panel
        self.selenium.find_element_by_class_name("VersionsPanel").click()

        # Version panel doesn't loads
        error = WebDriverWait(self.selenium, timeout=10).until(
            lambda selenium: version_panel.find_element_by_tag_name("p")
        )
        self.assertIn("Data for this panel isn't available anymore.", error.text)

    @override_settings(
        DEBUG=True,
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
        self.selenium.get(self.live_server_url + "/regular/basic/")
        version_panel = self.selenium.find_element_by_id("TemplatesPanel")

        # Click to show the versions panel
        self.selenium.find_element_by_class_name("TemplatesPanel").click()

        # Version panel loads
        trigger = WebDriverWait(self.selenium, timeout=10).until(
            lambda selenium: version_panel.find_element_by_css_selector(".remoteCall")
        )
        trigger.click()

        # Verify the code is displayed
        WebDriverWait(self.selenium, timeout=10).until(
            lambda selenium: self.selenium.find_element_by_css_selector(
                "#djDebugWindow code"
            )
        )


@override_settings(DEBUG=True)
class DebugToolbarSystemChecksTestCase(SimpleTestCase):
    @override_settings(
        MIDDLEWARE=[
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.middleware.gzip.GZipMiddleware",
            "debug_toolbar.middleware.DebugToolbarMiddleware",
        ]
    )
    def test_check_good_configuration(self):
        messages = run_checks()
        self.assertEqual(messages, [])

    @override_settings(
        MIDDLEWARE=[
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ]
    )
    def test_check_missing_middleware_error(self):
        messages = run_checks()
        self.assertEqual(
            messages,
            [
                Warning(
                    "debug_toolbar.middleware.DebugToolbarMiddleware is "
                    "missing from MIDDLEWARE.",
                    hint="Add debug_toolbar.middleware.DebugToolbarMiddleware "
                    "to MIDDLEWARE.",
                    id="debug_toolbar.W001",
                )
            ],
        )

    @override_settings(
        MIDDLEWARE=[
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "debug_toolbar.middleware.DebugToolbarMiddleware",
            "django.middleware.gzip.GZipMiddleware",
        ]
    )
    def test_check_gzip_middleware_error(self):
        messages = run_checks()
        self.assertEqual(
            messages,
            [
                Warning(
                    "debug_toolbar.middleware.DebugToolbarMiddleware occurs "
                    "before django.middleware.gzip.GZipMiddleware in "
                    "MIDDLEWARE.",
                    hint="Move debug_toolbar.middleware.DebugToolbarMiddleware "
                    "to after django.middleware.gzip.GZipMiddleware in "
                    "MIDDLEWARE.",
                    id="debug_toolbar.W003",
                )
            ],
        )
