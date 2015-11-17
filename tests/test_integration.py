# coding: utf-8

from __future__ import absolute_import, unicode_literals

import os
import unittest
from xml.etree import ElementTree as ET

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings

from debug_toolbar.middleware import DebugToolbarMiddleware, show_toolbar

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
        panel = self.toolbar.get_panel_by_id('RequestPanel')
        panel.process_request(self.request)
        panel.process_response(self.request, self.response)
        panel.generate_stats(self.request, self.response)
        return panel.get_stats()

    def test_url_resolving_positional(self):
        stats = self._resolve_stats('/resolving1/a/b/')
        self.assertEqual(stats['view_urlname'], 'positional-resolving')
        self.assertEqual(stats['view_func'], 'tests.views.resolving_view')
        self.assertEqual(stats['view_args'], ('a', 'b'))
        self.assertEqual(stats['view_kwargs'], {})

    def test_url_resolving_named(self):
        stats = self._resolve_stats('/resolving2/a/b/')
        self.assertEqual(stats['view_args'], ())
        self.assertEqual(stats['view_kwargs'], {'arg1': 'a', 'arg2': 'b'})

    def test_url_resolving_mixed(self):
        stats = self._resolve_stats('/resolving3/a/')
        self.assertEqual(stats['view_args'], ('a',))
        self.assertEqual(stats['view_kwargs'], {'arg2': 'default'})

    def test_url_resolving_bad(self):
        stats = self._resolve_stats('/non-existing-url/')
        self.assertEqual(stats['view_urlname'], 'None')
        self.assertEqual(stats['view_args'], 'None')
        self.assertEqual(stats['view_kwargs'], 'None')
        self.assertEqual(stats['view_func'], '<no view>')

    # Django doesn't guarantee that process_request, process_view and
    # process_response always get called in this order.

    def test_middleware_view_only(self):
        DebugToolbarMiddleware().process_view(self.request, regular_view, ('title',), {})

    def test_middleware_response_only(self):
        DebugToolbarMiddleware().process_response(self.request, self.response)

    def test_middleware_response_insertion(self):
        resp = regular_view(self.request, "İ")
        DebugToolbarMiddleware().process_response(self.request, resp)
        # check toolbar insertion before "</body>"
        self.assertContains(resp, '</div>\n</body>')

    def test_cache_page(self):
        self.client.get('/cached_view/')
        self.assertEqual(
            len(self.toolbar.get_panel_by_id('CachePanel').calls), 3)
        self.client.get('/cached_view/')
        self.assertEqual(
            len(self.toolbar.get_panel_by_id('CachePanel').calls), 5)


@override_settings(DEBUG=True)
class DebugToolbarIntegrationTestCase(TestCase):

    def test_middleware(self):
        response = self.client.get('/execute_sql/')
        self.assertEqual(response.status_code, 200)

    @override_settings(DEFAULT_CHARSET='iso-8859-1')
    def test_non_utf8_charset(self):
        response = self.client.get('/regular/ASCII/')
        self.assertContains(response, 'ASCII')      # template
        self.assertContains(response, 'djDebug')    # toolbar

        response = self.client.get('/regular/LÀTÍN/')
        self.assertContains(response, 'LÀTÍN')      # template
        self.assertContains(response, 'djDebug')    # toolbar

    def test_xml_validation(self):
        response = self.client.get('/regular/XML/')
        ET.fromstring(response.content)     # shouldn't raise ParseError


@unittest.skipIf(webdriver is None, "selenium isn't installed")
@unittest.skipUnless('DJANGO_SELENIUM_TESTS' in os.environ, "selenium tests not requested")
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
        self.selenium.get(self.live_server_url + '/regular/basic/')
        version_panel = self.selenium.find_element_by_id('VersionsPanel')

        # Versions panel isn't loaded
        with self.assertRaises(NoSuchElementException):
            version_panel.find_element_by_tag_name('table')

        # Click to show the versions panel
        self.selenium.find_element_by_class_name('VersionsPanel').click()

        # Version panel loads
        table = WebDriverWait(self.selenium, timeout=10).until(
            lambda selenium: version_panel.find_element_by_tag_name('table'))
        self.assertIn("Name", table.text)
        self.assertIn("Version", table.text)

    @override_settings(DEBUG_TOOLBAR_CONFIG={'RESULTS_CACHE_SIZE': 0})
    def test_expired_store(self):
        self.selenium.get(self.live_server_url + '/regular/basic/')
        version_panel = self.selenium.find_element_by_id('VersionsPanel')

        # Click to show the version panel
        self.selenium.find_element_by_class_name('VersionsPanel').click()

        # Version panel doesn't loads
        error = WebDriverWait(self.selenium, timeout=10).until(
            lambda selenium: version_panel.find_element_by_tag_name('p'))
        self.assertIn("Data for this panel isn't available anymore.", error.text)

    @override_settings(TEMPLATE_LOADERS=[(
        'django.template.loaders.cached.Loader', (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ),
    )])
    def test_django_cached_template_loader(self):
        self.selenium.get(self.live_server_url + '/regular/basic/')
        version_panel = self.selenium.find_element_by_id('TemplatesPanel')

        # Click to show the versions panel
        self.selenium.find_element_by_class_name('TemplatesPanel').click()

        # Version panel loads
        trigger = WebDriverWait(self.selenium, timeout=10).until(
            lambda selenium: version_panel.find_element_by_css_selector(
                '.remoteCall'))
        trigger.click()

        # Verify the code is displayed
        WebDriverWait(self.selenium, timeout=10).until(
            lambda selenium: self.selenium.find_element_by_css_selector(
                '#djDebugWindow code'))
