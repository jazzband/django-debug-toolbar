from debug_toolbar.middleware import DebugToolbarMiddleware
from debug_toolbar.panels.sql import SQLDebugPanel
from debug_toolbar.toolbar.loader import DebugToolbar

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
        