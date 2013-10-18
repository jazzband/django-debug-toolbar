# coding: utf-8

from __future__ import unicode_literals

import logging
import threading
from xml.etree import ElementTree as ET

import django
from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection
from django.http import HttpResponse
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from django.template import Template, Context
from django.utils import six
from django.utils import unittest

from debug_toolbar.middleware import DebugToolbarMiddleware
from debug_toolbar.panels.logger import (LoggingPanel,
    MESSAGE_IF_STRING_REPRESENTATION_INVALID)
from debug_toolbar.panels.sql import SQLDebugPanel
from debug_toolbar.panels.request_vars import RequestVarsDebugPanel
from debug_toolbar.panels.template import TemplateDebugPanel
from debug_toolbar.toolbar.loader import DebugToolbar
from debug_toolbar.utils import get_name_from_obj


rf = RequestFactory()


class BaseTestCase(TestCase):

    def setUp(self):
        request = rf.get('/')
        response = HttpResponse()
        toolbar = DebugToolbar(request)

        DebugToolbarMiddleware.debug_toolbars[threading.current_thread().ident] = toolbar

        self.request = request
        self.response = response
        self.toolbar = toolbar
        self.toolbar.stats = {}


class DebugToolbarTestCase(BaseTestCase):

    urls = 'tests.urls'

    def test_middleware(self):
        with self.settings(INTERNAL_IPS=['127.0.0.1'], DEBUG=True):
            resp = self.client.get('/execute_sql/')
        self.assertEqual(resp.status_code, 200)

    def test_show_toolbar_DEBUG(self):
        request = rf.get('/')
        middleware = DebugToolbarMiddleware()

        with self.settings(INTERNAL_IPS=['127.0.0.1'], DEBUG=True):
            self.assertTrue(middleware._show_toolbar(request))

        with self.settings(INTERNAL_IPS=['127.0.0.1'], DEBUG=False):
            self.assertFalse(middleware._show_toolbar(request))

    def test_show_toolbar_TEST(self):
        request = rf.get('/')
        middleware = DebugToolbarMiddleware()

        with self.settings(INTERNAL_IPS=['127.0.0.1'], TEST=True, DEBUG=True):
            self.assertFalse(middleware._show_toolbar(request))

        with self.settings(INTERNAL_IPS=['127.0.0.1'], TEST=False, DEBUG=True):
            self.assertTrue(middleware._show_toolbar(request))

    def test_show_toolbar_INTERNAL_IPS(self):
        request = rf.get('/')

        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        middleware = DebugToolbarMiddleware()

        with self.settings(INTERNAL_IPS=['127.0.0.1'], DEBUG=True):
            self.assertTrue(middleware._show_toolbar(request))

        with self.settings(INTERNAL_IPS=[], DEBUG=True):
            self.assertFalse(middleware._show_toolbar(request))

    def test_request_urlconf_string(self):
        request = rf.get('/')
        request.urlconf = 'tests.urls'
        middleware = DebugToolbarMiddleware()

        with self.settings(INTERNAL_IPS=['127.0.0.1'], DEBUG=True):
            middleware.process_request(request)

            self.assertFalse(isinstance(request.urlconf, six.string_types))

            self.assertTrue(hasattr(request.urlconf.urlpatterns[1], '_callback_str'))
            self.assertEqual(request.urlconf.urlpatterns[-1]._callback_str, 'tests.views.execute_sql')

    def test_request_urlconf_string_per_request(self):
        request = rf.get('/')
        request.urlconf = 'debug_toolbar.urls'
        middleware = DebugToolbarMiddleware()

        with self.settings(INTERNAL_IPS=['127.0.0.1'], DEBUG=True):
            middleware.process_request(request)
            request.urlconf = 'tests.urls'
            middleware.process_request(request)

            self.assertFalse(isinstance(request.urlconf, six.string_types))

            self.assertTrue(hasattr(request.urlconf.urlpatterns[1], '_callback_str'))
            self.assertEqual(request.urlconf.urlpatterns[-1]._callback_str, 'tests.views.execute_sql')

    def test_request_urlconf_module(self):
        request = rf.get('/')
        request.urlconf = __import__('tests.urls').urls
        middleware = DebugToolbarMiddleware()

        with self.settings(INTERNAL_IPS=['127.0.0.1'], DEBUG=True):
            middleware.process_request(request)

            self.assertFalse(isinstance(request.urlconf, six.string_types))

            self.assertTrue(hasattr(request.urlconf.urlpatterns[1], '_callback_str'))
            self.assertEqual(request.urlconf.urlpatterns[-1]._callback_str, 'tests.views.execute_sql')

    def test_tuple_urlconf(self):
        request = rf.get('/')
        urls = __import__('tests.urls').urls
        urls.urlpatterns = tuple(urls.urlpatterns)
        request.urlconf = urls
        middleware = DebugToolbarMiddleware()
        with self.settings(INTERNAL_IPS=['127.0.0.1'], DEBUG=True):
            middleware.process_request(request)
            self.assertFalse(isinstance(request.urlconf, six.string_types))

    def _resolve_stats(self, path):
        # takes stats from RequestVars panel
        self.request.path = path
        with self.settings(DEBUG=True):
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


@override_settings(DEBUG=True, INTERNAL_IPS=['127.0.0.1'])
class DebugToolbarIntegrationTestCase(TestCase):

    urls = 'tests.urls'

    @override_settings(DEFAULT_CHARSET='iso-8859-1')
    def test_non_utf8_charset(self):
        response = self.client.get('/regular/ASCII/')
        self.assertContains(response, 'ASCII')      # template
        self.assertContains(response, 'djDebug')    # toolbar

        response = self.client.get('/regular/LÀTÍN/')
        self.assertContains(response, 'LÀTÍN')      # template
        self.assertContains(response, 'djDebug')    # toolbar

    def test_non_ascii_session(self):
        response = self.client.get('/set_session/')
        self.assertContains(response, 'où')
        if not six.PY3:
            self.assertContains(response, 'là')

    def test_xml_validation(self):
        response = self.client.get('/regular/XML/')
        ET.fromstring(response.content)     # shouldn't raise ParseError


class DebugToolbarNameFromObjectTest(BaseTestCase):

    def test_func(self):
        def x():
            return 1
        res = get_name_from_obj(x)
        self.assertEqual(res, 'tests.tests.x')

    def test_lambda(self):
        res = get_name_from_obj(lambda: 1)
        self.assertEqual(res, 'tests.tests.<lambda>')

    def test_class(self):
        class A:
            pass
        res = get_name_from_obj(A)
        self.assertEqual(res, 'tests.tests.A')


class SQLPanelTestCase(BaseTestCase):

    def test_recording(self):
        panel = self.toolbar.get_panel(SQLDebugPanel)
        self.assertEqual(len(panel._queries), 0)

        list(User.objects.all())

        # ensure query was logged
        self.assertEqual(len(panel._queries), 1)
        query = panel._queries[0]
        self.assertEqual(query[0], 'default')
        self.assertTrue('sql' in query[1])
        self.assertTrue('duration' in query[1])
        self.assertTrue('stacktrace' in query[1])

        # ensure the stacktrace is populated
        self.assertTrue(len(query[1]['stacktrace']) > 0)

    def test_non_ascii_query(self):
        panel = self.toolbar.get_panel(SQLDebugPanel)
        self.assertEqual(len(panel._queries), 0)

        # non-ASCII query
        list(User.objects.extra(where=["username = 'café'"]))
        self.assertEqual(len(panel._queries), 1)

        # non-ASCII parameters
        list(User.objects.filter(username='café'))
        self.assertEqual(len(panel._queries), 2)

    @unittest.skipUnless(connection.vendor=='postgresql',
                         'Test valid only on PostgreSQL')
    def test_erroneous_query(self):
        """
        Test that an error in the query isn't swallowed by the middleware.
        """
        from django.db import connection
        from django.db.utils import DatabaseError
        try:
            connection.cursor().execute("erroneous query")
        except DatabaseError as e:
            self.assertTrue('erroneous query' in str(e))

    def test_disable_stacktraces(self):
        panel = self.toolbar.get_panel(SQLDebugPanel)
        self.assertEqual(len(panel._queries), 0)

        with self.settings(DEBUG_TOOLBAR_CONFIG={'ENABLE_STACKTRACES': False}):
            list(User.objects.all())

        # ensure query was logged
        self.assertEqual(len(panel._queries), 1)
        query = panel._queries[0]
        self.assertEqual(query[0], 'default')
        self.assertTrue('sql' in query[1])
        self.assertTrue('duration' in query[1])
        self.assertTrue('stacktrace' in query[1])

        # ensure the stacktrace is empty
        self.assertEqual([], query[1]['stacktrace'])


class TemplatePanelTestCase(BaseTestCase):

    def test_queryset_hook(self):
        template_panel = self.toolbar.get_panel(TemplateDebugPanel)
        sql_panel = self.toolbar.get_panel(SQLDebugPanel)
        t = Template("No context variables here!")
        c = Context({
            'queryset': User.objects.all(),
            'deep_queryset': {
                'queryset': User.objects.all(),
            }
        })
        t.render(c)
        # ensure the query was NOT logged
        self.assertEqual(len(sql_panel._queries), 0)
        base_ctx_idx = 1 if django.VERSION[:2] >= (1, 5) else 0
        ctx = template_panel.templates[0]['context'][base_ctx_idx]
        self.assertIn('<<queryset of auth.User>>', ctx)
        self.assertIn('<<triggers database query>>', ctx)


class LoggingPanelTestCase(BaseTestCase):
    def test_happy_case(self):
        logger = logging.getLogger(__name__)
        logger.info('Nothing to see here, move along!')

        logging_panel = self.toolbar.get_panel(LoggingPanel)
        logging_panel.process_response(None, None)
        records = logging_panel.get_stats()['records']

        self.assertEqual(1, len(records))
        self.assertEqual('Nothing to see here, move along!',
                         records[0]['message'])

    def test_formatting(self):
        logger = logging.getLogger(__name__)
        logger.info('There are %d %s', 5, 'apples')

        logging_panel = self.toolbar.get_panel(LoggingPanel)
        logging_panel.process_response(None, None)
        records = logging_panel.get_stats()['records']

        self.assertEqual(1, len(records))
        self.assertEqual('There are 5 apples',
                         records[0]['message'])

    def test_failing_formatting(self):
        class BadClass(object):
            def __str__(self):
                raise Exception('Please not stringify me!')

        logger = logging.getLogger(__name__)

        # should not raise exception, but fail silently
        logger.debug('This class is misbehaving: %s', BadClass())

        logging_panel = self.toolbar.get_panel(LoggingPanel)
        logging_panel.process_response(None, None)
        records = logging_panel.get_stats()['records']

        self.assertEqual(1, len(records))
        self.assertEqual(MESSAGE_IF_STRING_REPRESENTATION_INVALID,
                         records[0]['message'])
