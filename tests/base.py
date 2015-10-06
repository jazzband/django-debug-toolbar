from __future__ import absolute_import, unicode_literals

import threading

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from debug_toolbar.middleware import DebugToolbarMiddleware
from debug_toolbar.toolbar import DebugToolbar

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
