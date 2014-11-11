# coding: utf-8

from __future__ import absolute_import, unicode_literals

import django
from django.core import cache
from django.utils.unittest import skipIf

from ..base import BaseTestCase


class CachePanelTestCase(BaseTestCase):

    def setUp(self):
        super(CachePanelTestCase, self).setUp()
        self.panel = self.toolbar.get_panel_by_id('CachePanel')
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

    @skipIf(django.VERSION < (1, 7), "Caches was added in Django 1.7")
    def test_recording_caches(self):
        self.assertEqual(len(self.panel.calls), 0)
        cache.cache.set('foo', 'bar')
        cache.caches[cache.DEFAULT_CACHE_ALIAS].get('foo')
        self.assertEqual(len(self.panel.calls), 2)
