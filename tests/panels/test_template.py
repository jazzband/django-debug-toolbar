# coding: utf-8

from __future__ import unicode_literals

import django
from django.contrib.auth.models import User
from django.template import Template, Context

from debug_toolbar.panels.template import TemplateDebugPanel
from debug_toolbar.panels.sql import SQLDebugPanel

from ..base import BaseTestCase
from ..models import NonAsciiRepr


class TemplateDebugPanelTestCase(BaseTestCase):

    def setUp(self):
        super(TemplateDebugPanelTestCase, self).setUp()
        self.panel = self.toolbar.get_panel(TemplateDebugPanel)

    def test_queryset_hook(self):
        t = Template("No context variables here!")
        c = Context({
            'queryset': User.objects.all(),
            'deep_queryset': {
                'queryset': User.objects.all(),
            }
        })
        t.render(c)

        # ensure the query was NOT logged
        sql_panel = self.toolbar.get_panel(SQLDebugPanel)
        self.assertEqual(len(sql_panel._queries), 0)

        base_ctx_idx = 1 if django.VERSION[:2] >= (1, 5) else 0
        ctx = self.panel.templates[0]['context'][base_ctx_idx]
        self.assertIn('<<queryset of auth.User>>', ctx)
        self.assertIn('<<triggers database query>>', ctx)

    def test_object_with_non_ascii_repr_in_context(self):
        self.panel.process_request(self.request)
        t = Template("{{ object }}")
        c = Context({'object': NonAsciiRepr()})
        t.render(c)
        self.panel.process_response(self.request, self.response)
        self.assertIn('nôt åscíì', self.panel.content())
