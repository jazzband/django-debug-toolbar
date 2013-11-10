from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.test.utils import override_settings


@override_settings(DEBUG=True,
                   DEBUG_TOOLBAR_PANELS=['debug_toolbar.panels.profiling.ProfilingDebugPanel'])
class ProfilingPanelIntegrationTestCase(TestCase):

    urls = 'tests.urls'

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
