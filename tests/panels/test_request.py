# coding: utf-8

from __future__ import absolute_import, unicode_literals

from django.utils import six

from ..base import BaseTestCase


class RequestPanelTestCase(BaseTestCase):

    def setUp(self):
        super(RequestPanelTestCase, self).setUp()
        self.panel = self.toolbar.get_panel_by_id('RequestPanel')

    def test_non_ascii_session(self):
        self.request.session = {'où': 'où'}
        if not six.PY3:
            self.request.session['là'.encode('utf-8')] = 'là'.encode('utf-8')
        self.panel.process_request(self.request)
        self.panel.process_response(self.request, self.response)
        self.panel.generate_stats(self.request, self.response)
        content = self.panel.content
        if six.PY3:
            self.assertIn('où', content)
        else:
            self.assertIn('o\\xf9', content)
            self.assertIn('l\\xc3\\xa0', content)

    def test_object_with_non_ascii_repr_in_request_params(self):
        self.request.path = '/non_ascii_request/'
        self.panel.process_request(self.request)
        self.panel.process_response(self.request, self.response)
        self.panel.generate_stats(self.request, self.response)
        self.assertIn('nôt åscíì', self.panel.content)

    def test_insert_content(self):
        """
        Test that the panel only inserts content after generate_stats and
        not the process_response.
        """
        self.request.path = '/non_ascii_request/'
        self.panel.process_response(self.request, self.response)
        # ensure the panel does not have content yet.
        self.assertNotIn('nôt åscíì', self.panel.content)
        self.panel.generate_stats(self.request, self.response)
        # ensure the panel renders correctly.
        self.assertIn('nôt åscíì', self.panel.content)
