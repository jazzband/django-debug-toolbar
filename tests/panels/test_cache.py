# coding: utf-8

from __future__ import absolute_import, unicode_literals

from django.core import cache

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
        # Verify that the cache has a valid clear method.
        cache.cache.clear()
        self.assertEqual(len(self.panel.calls), 4)

    def test_recording_caches(self):
        self.assertEqual(len(self.panel.calls), 0)
        default_cache = cache.caches[cache.DEFAULT_CACHE_ALIAS]
        second_cache = cache.caches['second']
        default_cache.set('foo', 'bar')
        second_cache.get('foo')
        self.assertEqual(len(self.panel.calls), 2)

    def test_insert_content(self):
        """
        Test that the panel only inserts content after generate_stats and
        not the process_response.
        """
        cache.cache.get('café')
        self.panel.process_response(self.request, self.response)
        # ensure the panel does not have content yet.
        self.assertNotIn('café', self.panel.content)
        self.panel.generate_stats(self.request, self.response)
        # ensure the panel renders correctly.
        self.assertIn('café', self.panel.content)
