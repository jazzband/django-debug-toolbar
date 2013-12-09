# coding: utf-8

from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.contrib.staticfiles.templatetags import staticfiles
from django.template import Context, RequestContext, Template

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
                      'FileSystemFinder (1 file)', self.panel.content)
        self.assertEqual(self.panel.num_used, 0)
        self.assertNotEqual(self.panel.num_found, 0)
        self.assertEqual(self.panel.get_staticfiles_apps(),
                         ['django.contrib.admin', 'debug_toolbar'])
        self.assertEqual(self.panel.get_staticfiles_dirs(),
                         settings.STATICFILES_DIRS)
