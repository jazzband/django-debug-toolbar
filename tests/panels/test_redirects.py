from __future__ import absolute_import, unicode_literals

import copy

from django.conf import settings
from django.http import HttpResponse

from ..base import BaseTestCase


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
        self.assertContains(response, '302 Found')
        self.assertContains(response, 'http://somewhere/else/')

    def test_redirect_with_broken_context_processor(self):
        TEMPLATES = copy.deepcopy(settings.TEMPLATES)
        TEMPLATES[1]['OPTIONS']['context_processors'] = ['tests.context_processors.broken']

        with self.settings(TEMPLATES=TEMPLATES):
            redirect = HttpResponse(status=302)
            redirect['Location'] = 'http://somewhere/else/'
            response = self.panel.process_response(self.request, redirect)
            self.assertFalse(response is redirect)
            self.assertContains(response, '302 Found')
            self.assertContains(response, 'http://somewhere/else/')

    def test_unknown_status_code(self):
        redirect = HttpResponse(status=369)
        redirect['Location'] = 'http://somewhere/else/'
        response = self.panel.process_response(self.request, redirect)
        self.assertContains(response, '369 Unknown Status Code')

    def test_unknown_status_code_with_reason(self):
        redirect = HttpResponse(status=369, reason='Look Ma!')
        redirect['Location'] = 'http://somewhere/else/'
        response = self.panel.process_response(self.request, redirect)
        self.assertContains(response, '369 Look Ma!')

    def test_insert_content(self):
        """
        Test that the panel only inserts content after generate_stats and
        not the process_response.
        """
        redirect = HttpResponse(status=304)
        response = self.panel.process_response(self.request, redirect)
        self.assertIsNotNone(response)
        response = self.panel.generate_stats(self.request, redirect)
        self.assertIsNone(response)
