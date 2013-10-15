from __future__ import with_statement
import thread

import django
from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection
from django.http import HttpResponse
from django.test import TestCase, RequestFactory
from django.template import Template, Context
from django.utils import unittest

from debug_toolbar.middleware import DebugToolbarMiddleware
from debug_toolbar.panels.sql import SQLDebugPanel
from debug_toolbar.panels.request_vars import RequestVarsDebugPanel
from debug_toolbar.panels.template import TemplateDebugPanel
from debug_toolbar.toolbar.loader import DebugToolbar
from debug_toolbar.utils import get_name_from_obj
from debug_toolbar.utils.tracking import pre_dispatch, post_dispatch, callbacks
from views import streaming_http
from utils import get_request_generator

rf = RequestFactory()


class Settings(object):
    """Allows you to define settings that are required for this function to work"""

    NotDefined = object()

    def __init__(self, **overrides):
        self.overrides = overrides
        self._orig = {}

    def __enter__(self):
        for k, v in self.overrides.iteritems():
            self._orig[k] = getattr(settings, k, self.NotDefined)
            setattr(settings, k, v)

    def __exit__(self, exc_type, exc_value, traceback):
        for k, v in self._orig.iteritems():
            if v is self.NotDefined:
                delattr(settings, k)
            else:
                setattr(settings, k, v)


class BaseTestCase(TestCase):
    def setUp(self):
        request = rf.get('/')
        response = HttpResponse()
        toolbar = DebugToolbar(request)

        DebugToolbarMiddleware.debug_toolbars[thread.get_ident()] = toolbar

        self.request = request
        self.response = response
        self.toolbar = toolbar
        self.toolbar.stats = {}


class DebugToolbarTestCase(BaseTestCase):
    urls = 'tests.urls'

    def test_middleware(self):
        with Settings(INTERNAL_IPS=['127.0.0.1'], DEBUG=True):
            resp = self.client.get('/execute_sql/')
        self.assertEquals(resp.status_code, 200)

    def test_show_toolbar_DEBUG(self):
        request = rf.get('/')
        middleware = DebugToolbarMiddleware()

        with Settings(INTERNAL_IPS=['127.0.0.1'], DEBUG=True):
            self.assertTrue(middleware._show_toolbar(request))

        with Settings(INTERNAL_IPS=['127.0.0.1'], DEBUG=False):
            self.assertFalse(middleware._show_toolbar(request))

    def test_show_toolbar_TEST(self):
        request = rf.get('/')
        middleware = DebugToolbarMiddleware()

        with Settings(INTERNAL_IPS=['127.0.0.1'], TEST=True, DEBUG=True):
            self.assertFalse(middleware._show_toolbar(request))

        with Settings(INTERNAL_IPS=['127.0.0.1'], TEST=False, DEBUG=True):
            self.assertTrue(middleware._show_toolbar(request))

    def test_show_toolbar_INTERNAL_IPS(self):
        request = rf.get('/')

        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        middleware = DebugToolbarMiddleware()

        with Settings(INTERNAL_IPS=['127.0.0.1'], DEBUG=True):
            self.assertTrue(middleware._show_toolbar(request))

        with Settings(INTERNAL_IPS=[], DEBUG=True):
            self.assertFalse(middleware._show_toolbar(request))

    def test_request_urlconf_string(self):
        request = rf.get('/')
        request.urlconf = 'tests.urls'
        middleware = DebugToolbarMiddleware()

        with Settings(INTERNAL_IPS=['127.0.0.1'], DEBUG=True):
            middleware.process_request(request)

            self.assertFalse(isinstance(request.urlconf, basestring))

            self.assertTrue(hasattr(request.urlconf.urlpatterns[1], '_callback_str'))
            self.assertEquals(request.urlconf.urlpatterns[-1]._callback_str, 'tests.views.execute_sql')

    def test_request_urlconf_string_per_request(self):
        request = rf.get('/')
        request.urlconf = 'debug_toolbar.urls'
        middleware = DebugToolbarMiddleware()

        with Settings(INTERNAL_IPS=['127.0.0.1'], DEBUG=True):
            middleware.process_request(request)
            request.urlconf = 'tests.urls'
            middleware.process_request(request)

            self.assertFalse(isinstance(request.urlconf, basestring))

            self.assertTrue(hasattr(request.urlconf.urlpatterns[1], '_callback_str'))
            self.assertEquals(request.urlconf.urlpatterns[-1]._callback_str, 'tests.views.execute_sql')

    def test_request_urlconf_module(self):
        request = rf.get('/')
        request.urlconf = __import__('tests.urls').urls
        middleware = DebugToolbarMiddleware()

        with Settings(INTERNAL_IPS=['127.0.0.1'], DEBUG=True):
            middleware.process_request(request)

            self.assertFalse(isinstance(request.urlconf, basestring))

            self.assertTrue(hasattr(request.urlconf.urlpatterns[1], '_callback_str'))
            self.assertEquals(request.urlconf.urlpatterns[-1]._callback_str, 'tests.views.execute_sql')

    def test_tuple_urlconf(self):
        request = rf.get('/')
        urls = __import__('tests.urls').urls
        urls.urlpatterns = tuple(urls.urlpatterns)
        request.urlconf = urls
        middleware = DebugToolbarMiddleware()
        with Settings(INTERNAL_IPS=['127.0.0.1'], DEBUG=True):
            middleware.process_request(request)
            self.assertFalse(isinstance(request.urlconf, basestring))

    def _get_streaming_content(self, version):
        try:
            # Mocking DebugToolbar's render_toolbar method
            original_render_toolbar = DebugToolbar.render_toolbar
            DebugToolbar.render_toolbar = lambda self: '<TOOLBAR_HERE>'
            with Settings(INTERNAL_IPS=['127.0.0.1'], DEBUG=True):
                middleware = DebugToolbarMiddleware()
                request = rf.get('/streaming/')
                response = streaming_http(request, version=version)
                middleware.process_request(request)
                debug_toolbar_response = middleware.process_response(request, response)
                return debug_toolbar_response.streaming_content
        finally:
            DebugToolbar.render_toolbar = original_render_toolbar

    def _django_version_gte_15():
        (v, subv) = django.VERSION[:2]
        return (v > 1) or (v == 1 and subv >= 5)

    @unittest.skipUnless(_django_version_gte_15(),
                         'Test valid only with Django >= 1.5')
    def test_streaming_response_tag_found(self):
        actual_content = list(self._get_streaming_content(1))
        expected_content = list(get_request_generator(1))
        expected_content[-2] = '<TOOLBAR_HERE>%s' % expected_content[-2]
        self.assertEquals(actual_content, expected_content)

    @unittest.skipUnless(_django_version_gte_15(),
                         'Test valid only with Django >= 1.5')
    def test_streaming_response_tag_notfound_1(self):
        self.assertEquals(
            list(self._get_streaming_content(2)),
            list(get_request_generator(2)))

    @unittest.skipUnless(_django_version_gte_15(),
                         'Test valid only with Django >= 1.5')
    def test_streaming_response_tag_notfound_2(self):
        self.assertEquals(
            list(self._get_streaming_content(3)),
            list(get_request_generator(3)))

    def _resolve_stats(self, path):
        # takes stats from RequestVars panel
        self.request.path = path
        with Settings(DEBUG=True):
            panel = self.toolbar.get_panel(RequestVarsDebugPanel)
            panel.process_request(self.request)
            panel.process_response(self.request, self.response)
            return self.toolbar.stats['requestvars']

    def test_url_resolving_positional(self):
        stats = self._resolve_stats('/resolving1/a/b/')
        self.assertEquals(stats['view_urlname'], 'positional-resolving')  # Django >= 1.3
        self.assertEquals(stats['view_func'], 'tests.views.resolving_view')
        self.assertEquals(stats['view_args'], ('a', 'b'))
        self.assertEquals(stats['view_kwargs'], {})

    def test_url_resolving_named(self):
        stats = self._resolve_stats('/resolving2/a/b/')
        self.assertEquals(stats['view_args'], ())
        self.assertEquals(stats['view_kwargs'], {'arg1': 'a', 'arg2': 'b'})

    def test_url_resolving_mixed(self):
        stats = self._resolve_stats('/resolving3/a/')
        self.assertEquals(stats['view_args'], ('a',))
        self.assertEquals(stats['view_kwargs'], {'arg2': 'default'})

    def test_url_resolving_bad(self):
        stats = self._resolve_stats('/non-existing-url/')
        self.assertEquals(stats['view_urlname'], 'None')
        self.assertEquals(stats['view_args'], 'None')
        self.assertEquals(stats['view_kwargs'], 'None')
        self.assertEquals(stats['view_func'], '<no view>')


class DebugToolbarNameFromObjectTest(BaseTestCase):
    def test_func(self):
        def x():
            return 1
        res = get_name_from_obj(x)
        self.assertEquals(res, 'tests.tests.x')

    def test_lambda(self):
        res = get_name_from_obj(lambda: 1)
        self.assertEquals(res, 'tests.tests.<lambda>')

    def test_class(self):
        class A:
            pass
        res = get_name_from_obj(A)
        self.assertEquals(res, 'tests.tests.A')


class SQLPanelTestCase(BaseTestCase):
    def test_recording(self):
        panel = self.toolbar.get_panel(SQLDebugPanel)
        self.assertEquals(len(panel._queries), 0)

        list(User.objects.all())

        # ensure query was logged
        self.assertEquals(len(panel._queries), 1)
        query = panel._queries[0]
        self.assertEquals(query[0], 'default')
        self.assertTrue('sql' in query[1])
        self.assertTrue('duration' in query[1])
        self.assertTrue('stacktrace' in query[1])

        # ensure the stacktrace is populated
        self.assertTrue(len(query[1]['stacktrace']) > 0)

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
        self.assertEquals(len(panel._queries), 0)

        with Settings(DEBUG_TOOLBAR_CONFIG={'ENABLE_STACKTRACES': False}):
            list(User.objects.all())

        # ensure query was logged
        self.assertEquals(len(panel._queries), 1)
        query = panel._queries[0]
        self.assertEquals(query[0], 'default')
        self.assertTrue('sql' in query[1])
        self.assertTrue('duration' in query[1])
        self.assertTrue('stacktrace' in query[1])

        # ensure the stacktrace is empty
        self.assertEquals([], query[1]['stacktrace'])


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
        self.assertEquals(len(sql_panel._queries), 0)
        base_ctx_idx = 1 if django.VERSION[:2] >= (1, 5) else 0
        ctx = template_panel.templates[0]['context'][base_ctx_idx]
        self.assertIn('<<queryset of auth.User>>', ctx)
        self.assertIn('<<triggers database query>>', ctx)


def module_func(*args, **kwargs):
    """Used by dispatch tests"""
    return 'blah'


class TrackingTestCase(BaseTestCase):
    @classmethod
    def class_method(cls, *args, **kwargs):
        return 'blah'

    def class_func(self, *args, **kwargs):
        """Used by dispatch tests"""
        return 'blah'

    def test_pre_hook(self):
        foo = {}

        @pre_dispatch(module_func)
        def test(**kwargs):
            foo.update(kwargs)

        self.assertTrue(hasattr(module_func, '__wrapped__'))
        self.assertEquals(len(callbacks['before']), 1)

        module_func('hi', foo='bar')

        self.assertTrue('sender' in foo, foo)
        # best we can do
        self.assertEquals(foo['sender'].__name__, 'module_func')
        self.assertTrue('start' in foo, foo)
        self.assertTrue(foo['start'] > 0)
        self.assertTrue('stop' not in foo, foo)
        self.assertTrue('args' in foo, foo)
        self.assertTrue(len(foo['args']), 1)
        self.assertEquals(foo['args'][0], 'hi')
        self.assertTrue('kwargs' in foo, foo)
        self.assertTrue(len(foo['kwargs']), 1)
        self.assertTrue('foo' in foo['kwargs'])
        self.assertEquals(foo['kwargs']['foo'], 'bar')

        callbacks['before'] = {}

        @pre_dispatch(TrackingTestCase.class_func)
        def test(**kwargs):
            foo.update(kwargs)

        self.assertTrue(hasattr(TrackingTestCase.class_func, '__wrapped__'))
        self.assertEquals(len(callbacks['before']), 1)

        self.class_func('hello', foo='bar')

        self.assertTrue('sender' in foo, foo)
        # best we can do
        self.assertEquals(foo['sender'].__name__, 'class_func')
        self.assertTrue('start' in foo, foo)
        self.assertTrue(foo['start'] > 0)
        self.assertTrue('stop' not in foo, foo)
        self.assertTrue('args' in foo, foo)
        self.assertTrue(len(foo['args']), 2)
        self.assertEquals(foo['args'][1], 'hello')
        self.assertTrue('kwargs' in foo, foo)
        self.assertTrue(len(foo['kwargs']), 1)
        self.assertTrue('foo' in foo['kwargs'])
        self.assertEquals(foo['kwargs']['foo'], 'bar')

        callbacks['before'] = {}

        @pre_dispatch(TrackingTestCase.class_method)
        def test(**kwargs):
            foo.update(kwargs)

        self.assertTrue(hasattr(TrackingTestCase.class_method, '__wrapped__'))
        self.assertEquals(len(callbacks['before']), 1)

        TrackingTestCase.class_method()

        self.assertTrue('sender' in foo, foo)
        # best we can do
        self.assertEquals(foo['sender'].__name__, 'class_method')
        self.assertTrue('start' in foo, foo)
        self.assertTrue('stop' not in foo, foo)
        self.assertTrue('args' in foo, foo)

    def test_post_hook(self):
        foo = {}

        @post_dispatch(module_func)
        def test(**kwargs):
            foo.update(kwargs)

        self.assertTrue(hasattr(module_func, '__wrapped__'))
        self.assertEquals(len(callbacks['after']), 1)

        module_func('hi', foo='bar')

        self.assertTrue('sender' in foo, foo)
        # best we can do
        self.assertEquals(foo['sender'].__name__, 'module_func')
        self.assertTrue('start' in foo, foo)
        self.assertTrue(foo['start'] > 0)
        self.assertTrue('stop' in foo, foo)
        self.assertTrue(foo['stop'] > foo['start'])
        self.assertTrue('args' in foo, foo)
        self.assertTrue(len(foo['args']), 1)
        self.assertEquals(foo['args'][0], 'hi')
        self.assertTrue('kwargs' in foo, foo)
        self.assertTrue(len(foo['kwargs']), 1)
        self.assertTrue('foo' in foo['kwargs'])
        self.assertEquals(foo['kwargs']['foo'], 'bar')

        callbacks['after'] = {}

        @post_dispatch(TrackingTestCase.class_func)
        def test(**kwargs):
            foo.update(kwargs)

        self.assertTrue(hasattr(TrackingTestCase.class_func, '__wrapped__'))
        self.assertEquals(len(callbacks['after']), 1)

        self.class_func('hello', foo='bar')

        self.assertTrue('sender' in foo, foo)
        # best we can do
        self.assertEquals(foo['sender'].__name__, 'class_func')
        self.assertTrue('start' in foo, foo)
        self.assertTrue(foo['start'] > 0)
        self.assertTrue('stop' in foo, foo)
        self.assertTrue(foo['stop'] > foo['start'])
        self.assertTrue('args' in foo, foo)
        self.assertTrue(len(foo['args']), 2)
        self.assertEquals(foo['args'][1], 'hello')
        self.assertTrue('kwargs' in foo, foo)
        self.assertTrue(len(foo['kwargs']), 1)
        self.assertTrue('foo' in foo['kwargs'])
        self.assertEquals(foo['kwargs']['foo'], 'bar')
