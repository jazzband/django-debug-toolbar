# coding: utf-8

from __future__ import absolute_import, unicode_literals

import django
from django.core import cache

from ..base import BaseTestCase
from debug_toolbar.compat import unittest


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
        # Verify that the cache has a valid clear method.
        cache.cache.clear()
        self.assertEqual(len(self.panel.calls), 4)

    @unittest.skipIf(django.VERSION < (1, 7), "Caches was added in Django 1.7")
    def test_recording_caches(self):
        self.assertEqual(len(self.panel.calls), 0)
        default_cache = cache.caches[cache.DEFAULT_CACHE_ALIAS]
        second_cache = cache.caches['second']
        default_cache.set('foo', 'bar')
        second_cache.get('foo')
        self.assertEqual(len(self.panel.calls), 2)

    @unittest.skipIf(django.VERSION > (1, 6), "get_cache was deprecated in Django 1.7")
    def test_recording_get_cache(self):
        self.assertEqual(len(self.panel.calls), 0)
        default_cache = cache.get_cache(cache.DEFAULT_CACHE_ALIAS)
        second_cache = cache.get_cache('second')
        default_cache.set('foo', 'bar')
        second_cache.get('foo')
        self.assertEqual(len(self.panel.calls), 2)
