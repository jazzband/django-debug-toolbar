# coding: utf-8

from __future__ import unicode_literals

from django.core import cache

from debug_toolbar.panels.cache import CacheDebugPanel

from ..base import BaseTestCase


class CachePanelTestCase(BaseTestCase):

    def setUp(self):
        super(CachePanelTestCase, self).setUp()
        self.panel = self.toolbar.get_panel(CacheDebugPanel)
        self.panel.enable_instrumentation()

    def tearDown(self):
        self.panel.disable_instrumentation()
        super(CachePanelTestCase, self).tearDown()

    def test_recording(self):
        self.assertEqual(len(self.panel.calls), 0)
        cache.cache.set('foo', 'bar')
        cache.cache.get('foo')
        cache.cache.delete('foo')
        self.assertEqual(len(self.panel.calls), 3)
