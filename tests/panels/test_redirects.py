from __future__ import absolute_import, unicode_literals

import django
from django.conf import settings
from django.http import HttpResponse
from django.test.utils import override_settings
from django.utils import unittest

from ..base import BaseTestCase


@override_settings(DEBUG_TOOLBAR_CONFIG={'INTERCEPT_REDIRECTS': True})
class RedirectsPanelTestCase(BaseTestCase):

    def setUp(self):
        super(RedirectsPanelTestCase, self).setUp()
        self.panel = self.toolbar.get_panel_by_id('RedirectsPanel')

    def test_regular_response(self):
        response = self.panel.process_response(self.request, self.response)
        self.assertTrue(response is self.response)

    def test_not_a_redirect(self):
        redirect = HttpResponse(status=304)     # not modified
        response = self.panel.process_response(self.request, redirect)
        self.assertTrue(response is redirect)

    def test_redirect(self):
        redirect = HttpResponse(status=302)
        redirect['Location'] = 'http://somewhere/else/'
        response = self.panel.process_response(self.request, redirect)
        self.assertFalse(response is redirect)
        self.assertContains(response, '302 FOUND')
        self.assertContains(response, 'http://somewhere/else/')

    def test_redirect_with_broken_context_processor(self):
        context_processors = settings.TEMPLATE_CONTEXT_PROCESSORS + (
            'tests.context_processors.broken',
        )

        with self.settings(TEMPLATE_CONTEXT_PROCESSORS=context_processors):
            redirect = HttpResponse(status=302)
            redirect['Location'] = 'http://somewhere/else/'
            response = self.panel.process_response(self.request, redirect)
            self.assertFalse(response is redirect)
            self.assertContains(response, '302 FOUND')
            self.assertContains(response, 'http://somewhere/else/')

    def test_unknown_status_code(self):
        redirect = HttpResponse(status=369)
        redirect['Location'] = 'http://somewhere/else/'
        response = self.panel.process_response(self.request, redirect)
        self.assertContains(response, '369 UNKNOWN STATUS CODE')

    @unittest.skipIf(django.VERSION[:2] < (1, 6), "reason isn't supported")
    def test_unknown_status_code_with_reason(self):
        redirect = HttpResponse(status=369, reason='Look Ma!')
        redirect['Location'] = 'http://somewhere/else/'
        response = self.panel.process_response(self.request, redirect)
        self.assertContains(response, '369 Look Ma!')
