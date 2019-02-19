# coding: utf-8

from __future__ import absolute_import, unicode_literals

from django.core import cache

from ..base import BaseTestCase


class CachePanelTestCase(BaseTestCase):
    panel_id = "CachePanel"

    def test_recording(self):
        self.assertEqual(len(self.panel.calls), 0)
        cache.cache.set("foo", "bar")
        cache.cache.get("foo")
        cache.cache.delete("foo")
        # Verify that the cache has a valid clear method.
        cache.cache.clear()
        self.assertEqual(len(self.panel.calls), 4)

    def test_recording_caches(self):
        self.assertEqual(len(self.panel.calls), 0)
        default_cache = cache.caches[cache.DEFAULT_CACHE_ALIAS]
        second_cache = cache.caches["second"]
        default_cache.set("foo", "bar")
        second_cache.get("foo")
        self.assertEqual(len(self.panel.calls), 2)

    def test_insert_content(self):
        """
        Test that the panel only inserts content after generate_stats and
        not the process_response.
        """
        cache.cache.get("café")
        self.panel.process_response(self.request, self.response)
        # ensure the panel does not have content yet.
        self.assertNotIn("café", self.panel.content)
        self.panel.generate_stats(self.request, self.response)
        # ensure the panel renders correctly.
        self.assertIn("café", self.panel.content)
        self.assertValidHTML(self.panel.content)

    def test_generate_server_timing(self):
        self.assertEqual(len(self.panel.calls), 0)
        cache.cache.set("foo", "bar")
        cache.cache.get("foo")
        cache.cache.delete("foo")

        self.assertEqual(len(self.panel.calls), 3)

        self.panel.generate_stats(self.request, self.response)
        self.panel.generate_server_timing(self.request, self.response)

        stats = self.panel.get_stats()

        expected_data = {
            "total_time": {
                "title": "Cache {} Calls".format(stats["total_calls"]),
                "value": stats["total_time"],
            }
        }

        self.assertEqual(self.panel.get_server_timing_stats(), expected_data)
