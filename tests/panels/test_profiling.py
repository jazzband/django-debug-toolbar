from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import unittest

from ..base import BaseTestCase
from ..views import regular_view


@override_settings(DEBUG_TOOLBAR_PANELS=['debug_toolbar.panels.profiling.ProfilingPanel'])
class ProfilingPanelTestCase(BaseTestCase):

    def setUp(self):
        super(ProfilingPanelTestCase, self).setUp()
        self.panel = self.toolbar.get_panel_by_id('ProfilingPanel')

    # This test fails randomly for a reason I don't understand.

    @unittest.expectedFailure
    def test_regular_view(self):
        self.panel.process_view(self.request, regular_view, ('profiling',), {})
        self.panel.process_response(self.request, self.response)
        self.assertIn('func_list', self.panel.get_stats())
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
            if hasattr(transaction, 'atomic'):      # Django >= 1.6
                with transaction.atomic():
                    response = self.client.get('/new_user/')
            else:
                response = self.client.get('/new_user/')
        self.assertEqual(User.objects.count(), 1)
