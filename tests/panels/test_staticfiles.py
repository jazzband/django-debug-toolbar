# coding: utf-8

from __future__ import absolute_import, unicode_literals

from django.contrib.staticfiles import finders

from ..base import BaseTestCase


class StaticFilesPanelTestCase(BaseTestCase):

    def setUp(self):
        super(StaticFilesPanelTestCase, self).setUp()
        self.panel = self.toolbar.get_panel_by_id('StaticFilesPanel')

    def test_default_case(self):
        self.panel.process_request(self.request)
        self.panel.process_response(self.request, self.response)
        self.assertIn('django.contrib.staticfiles.finders.'
                      'AppDirectoriesFinder', self.panel.content)
        self.assertIn('django.contrib.staticfiles.finders.'
                      'FileSystemFinder (2 files)', self.panel.content)
        self.assertEqual(self.panel.num_used, 0)
        self.assertNotEqual(self.panel.num_found, 0)
        self.assertEqual(self.panel.get_staticfiles_apps(),
                         ['django.contrib.admin', 'debug_toolbar'])
        self.assertEqual(self.panel.get_staticfiles_dirs(),
                         finders.FileSystemFinder().locations)
