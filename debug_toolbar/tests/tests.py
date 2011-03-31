from debug_toolbar.middleware import DebugToolbarMiddleware
from debug_toolbar.panels.sql import SQLDebugPanel
from debug_toolbar.toolbar.loader import DebugToolbar
from debug_toolbar.utils.tracking import pre_dispatch, post_dispatch, callbacks

from django.contrib.auth.models import User
from django.test import TestCase

from dingus import Dingus
import thread

class BaseTestCase(TestCase):
    def setUp(self):
        request = Dingus('request')
        toolbar = DebugToolbar(request)
        DebugToolbarMiddleware.debug_toolbars[thread.get_ident()] = toolbar
        self.toolbar = toolbar

class DebugToolbarTestCase(BaseTestCase):
    urls = 'debug_toolbar.tests.urls'
    
    def test_middleware(self):
        resp = self.client.get('/execute_sql/')
        self.assertEquals(resp.status_code, 200)

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
        self.assertGreater(foo['start'], 0)
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
        self.assertGreater(foo['start'], 0)
        self.assertTrue('stop' not in foo, foo)
        self.assertTrue('args' in foo, foo)
        self.assertTrue(len(foo['args']), 2)
        self.assertEquals(foo['args'][1], 'hello')
        self.assertTrue('kwargs' in foo, foo)
        self.assertTrue(len(foo['kwargs']), 1)
        self.assertTrue('foo' in foo['kwargs'])
        self.assertEquals(foo['kwargs']['foo'], 'bar')

        # callbacks['before'] = {}
        #     
        #         @pre_dispatch(TrackingTestCase.class_method)
        #         def test(**kwargs):
        #             foo.update(kwargs)
        #     
        #         self.assertTrue(hasattr(TrackingTestCase.class_method, '__wrapped__'))
        #         self.assertEquals(len(callbacks['before']), 1)
        # 
        #         TrackingTestCase.class_method()
        # 
        #         self.assertTrue('sender' in foo, foo)
        #         # best we can do
        #         self.assertEquals(foo['sender'].__name__, 'class_method')
        #         self.assertTrue('start' in foo, foo)
        #         self.assertTrue('stop' not in foo, foo)
        #         self.assertTrue('args' in foo, foo)

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
        self.assertGreater(foo['start'], 0)
        self.assertTrue('stop' in foo, foo)
        self.assertGreater(foo['stop'], foo['start'])
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
        self.assertGreater(foo['start'], 0)
        self.assertTrue('stop' in foo, foo)
        self.assertGreater(foo['stop'], foo['start'])
        self.assertTrue('args' in foo, foo)
        self.assertTrue(len(foo['args']), 2)
        self.assertEquals(foo['args'][1], 'hello')
        self.assertTrue('kwargs' in foo, foo)
        self.assertTrue(len(foo['kwargs']), 1)
        self.assertTrue('foo' in foo['kwargs'])
        self.assertEquals(foo['kwargs']['foo'], 'bar')