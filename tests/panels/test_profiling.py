from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.test.utils import override_settings

from ..base import BaseTestCase
from ..views import regular_view


@override_settings(DEBUG_TOOLBAR_PANELS=['debug_toolbar.panels.profiling.ProfilingPanel'])
class ProfilingPanelTestCase(BaseTestCase):

    def setUp(self):
        super(ProfilingPanelTestCase, self).setUp()
        self.panel = self.toolbar.get_panel_by_id('ProfilingPanel')

    def test_regular_view(self):
        self.panel.process_view(self.request, regular_view, ('profiling',), {})
        self.panel.process_response(self.request, self.response)
        self.panel.generate_stats(self.request, self.response)
        self.assertIn('func_list', self.panel.get_stats())
        self.assertIn('regular_view', self.panel.content)

    def test_insert_content(self):
        """
        Test that the panel only inserts content after generate_stats and
        not the process_response.
        """
        self.panel.process_view(self.request, regular_view, ('profiling',), {})
        self.panel.process_response(self.request, self.response)
        # ensure the panel does not have content yet.
        self.assertNotIn('regular_view', self.panel.content)
        self.panel.generate_stats(self.request, self.response)
        # ensure the panel renders correctly.
        self.assertIn('regular_view', self.panel.content)


@override_settings(DEBUG=True,
                   DEBUG_TOOLBAR_PANELS=['debug_toolbar.panels.profiling.ProfilingPanel'])
class ProfilingPanelIntegrationTestCase(TestCase):

    def test_view_executed_once(self):
        self.assertEqual(User.objects.count(), 0)

        response = self.client.get('/new_user/')
        self.assertContains(response, 'Profiling')
        self.assertEqual(User.objects.count(), 1)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                response = self.client.get('/new_user/')
        self.assertEqual(User.objects.count(), 1)
