# coding: utf-8

from __future__ import unicode_literals

from xml.etree import ElementTree as ET

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from django.utils import six

from debug_toolbar.middleware import DebugToolbarMiddleware, show_toolbar
from debug_toolbar.panels.request_vars import RequestVarsDebugPanel

from .base import BaseTestCase


rf = RequestFactory()


@override_settings(DEBUG=True)
class DebugToolbarTestCase(BaseTestCase):

    urls = 'tests.urls'

    def test_show_toolbar(self):
        self.assertTrue(show_toolbar(self.request))

    def test_show_toolbar_DEBUG(self):
        with self.settings(DEBUG=False):
            self.assertFalse(show_toolbar(self.request))

    def test_show_toolbar_INTERNAL_IPS(self):
        with self.settings(INTERNAL_IPS=[]):
            self.assertFalse(show_toolbar(self.request))

    def test_request_urlconf_string(self):
        request = rf.get('/')
        request.urlconf = 'tests.urls'
        middleware = DebugToolbarMiddleware()

        middleware.process_request(request)

        self.assertFalse(isinstance(request.urlconf, six.string_types))

        patterns = request.urlconf.urlpatterns
        self.assertTrue(hasattr(patterns[1], '_callback_str'))
        self.assertEqual(patterns[-1]._callback_str, 'tests.views.execute_sql')

    def test_request_urlconf_string_per_request(self):
        request = rf.get('/')
        request.urlconf = 'debug_toolbar.urls'
        middleware = DebugToolbarMiddleware()

        middleware.process_request(request)
        request.urlconf = 'tests.urls'
        middleware.process_request(request)

        self.assertFalse(isinstance(request.urlconf, six.string_types))

        patterns = request.urlconf.urlpatterns
        self.assertTrue(hasattr(patterns[1], '_callback_str'))
        self.assertEqual(patterns[-1]._callback_str, 'tests.views.execute_sql')

    def test_request_urlconf_module(self):
        request = rf.get('/')
        request.urlconf = __import__('tests.urls').urls
        middleware = DebugToolbarMiddleware()

        middleware.process_request(request)

        self.assertFalse(isinstance(request.urlconf, six.string_types))

        patterns = request.urlconf.urlpatterns
        self.assertTrue(hasattr(patterns[1], '_callback_str'))
        self.assertEqual(patterns[-1]._callback_str, 'tests.views.execute_sql')

    def test_tuple_urlconf(self):
        request = rf.get('/')
        urls = __import__('tests.urls').urls
        urls.urlpatterns = tuple(urls.urlpatterns)
        request.urlconf = urls
        middleware = DebugToolbarMiddleware()

        middleware.process_request(request)

        self.assertFalse(isinstance(request.urlconf, six.string_types))

    def _resolve_stats(self, path):
        # takes stats from RequestVars panel
        self.request.path = path
        panel = self.toolbar.get_panel(RequestVarsDebugPanel)
        panel.process_request(self.request)
        panel.process_response(self.request, self.response)
        return self.toolbar.stats['requestvars']

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


@override_settings(DEBUG=True)
class DebugToolbarIntegrationTestCase(TestCase):

    urls = 'tests.urls'

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

    def test_non_ascii_bytes_in_db_params(self):
        response = self.client.get('/non_ascii_bytes_in_db_params/')
        if six.PY3:
            self.assertContains(response, 'djàngó')
        else:
            self.assertContains(response, 'dj\\xe0ng\\xf3')

    def test_non_ascii_session(self):
        response = self.client.get('/set_session/')
        if six.PY3:
            self.assertContains(response, 'où')
        else:
            self.assertContains(response, 'o\\xf9')
            self.assertContains(response, 'l\\xc3\\xa0')

    def test_object_with_non_ascii_repr_in_context(self):
        response = self.client.get('/non_ascii_context/')
        self.assertContains(response, 'nôt åscíì')

    def test_object_with_non_ascii_repr_in_request_vars(self):
        response = self.client.get('/non_ascii_request/')
        self.assertContains(response, 'nôt åscíì')

    def test_xml_validation(self):
        response = self.client.get('/regular/XML/')
        ET.fromstring(response.content)     # shouldn't raise ParseError

    def test_view_executed_once(self):
        with self.settings(
                DEBUG_TOOLBAR_PANELS=['debug_toolbar.panels.profiling.ProfilingDebugPanel']):

            self.assertEqual(User.objects.count(), 0)

            response = self.client.get('/new_user/')
            self.assertContains(response, 'Profiling')
            self.assertEqual(User.objects.count(), 1)

            with self.assertRaises(IntegrityError):
                if hasattr(transaction, 'atomic'):      # Django >= 1.6
                    with transaction.atomic():
                        response = self.client.get('/new_user/')
                else:
                    response = self.client.get('/new_user/')
            self.assertEqual(User.objects.count(), 1)
