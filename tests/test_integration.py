# coding: utf-8

from __future__ import absolute_import, unicode_literals

import os
from xml.etree import ElementTree as ET

try:
    from selenium import webdriver
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.support.wait import WebDriverWait
except ImportError:
    webdriver = None

from django.test import LiveServerTestCase, RequestFactory, TestCase
from django.test.utils import override_settings
from django.utils.unittest import skipIf, skipUnless

from debug_toolbar.middleware import DebugToolbarMiddleware, show_toolbar

from . import update_toolbar_config
from .base import BaseTestCase
from .views import regular_view


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

    # The below test_should_render_panels_*() methods test the return values of
    # DebugToolbar.should_render_panels() under various conditions.  The method
    # should never raise an Exception, and should return a bool that depends on
    # settings.DEBUG_TOOLBAR_CONFIG['RENDER_PANELS'] and request.META.

    def test_should_render_panels(self):
        """
        Tests that, with the installed settings, the return value of
        DebugToolbar.should_render_panels() is a bool, and that the method does
        not raise an Exception.
        """
        self.assertTrue(isinstance(self.toolbar.should_render_panels(), bool))

    def test_should_render_panels_RENDER_PANELS_None_wsgi_multiprocess_None(self):
        """
        Tests the return value of DebugToolbar.should_render_panels() when
        settings.DEBUG_TOOLBAR_CONFIG['RENDER_PANELS'] is None and
        'wsgi.multiprocess' is not in request.META. The method should correctly
        handle the absence of that key and should never raise a KeyError, and
        should return True.
        """
        self.toolbar.config['RENDER_PANELS'] = None
        self.toolbar.request.META.pop('wsgi.multiprocess', None)
        self.assertTrue(self.toolbar.should_render_panels())

    # End of test_should_render_panels_*() methods.

    def _resolve_stats(self, path):
        # takes stats from Request panel
        self.request.path = path
        panel = self.toolbar.get_panel_by_id('RequestPanel')
        panel.process_request(self.request)
        panel.process_response(self.request, self.response)
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


@skipIf(webdriver is None, "selenium isn't installed")
@skipUnless('DJANGO_SELENIUM_TESTS' in os.environ, "selenium tests not requested")
@override_settings(DEBUG=True)
class DebugToolbarLiveTestCase(LiveServerTestCase):

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

    @override_settings(DEBUG_TOOLBAR_CONFIG={'RESULTS_STORE_SIZE': 0})
    def test_expired_store(self):
        self.selenium.get(self.live_server_url + '/regular/basic/')
        version_panel = self.selenium.find_element_by_id('VersionsPanel')

        # Click to show the version panel
        self.selenium.find_element_by_class_name('VersionsPanel').click()

        # Version panel doesn't loads
        error = WebDriverWait(self.selenium, timeout=10).until(
            lambda selenium: version_panel.find_element_by_tag_name('p'))
        self.assertIn("Data for this panel isn't available anymore.", error.text)
