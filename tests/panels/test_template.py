from __future__ import unicode_literals

import django
from django.contrib.auth.models import User
from django.template import Template, Context

from debug_toolbar.panels.template import TemplateDebugPanel
from debug_toolbar.panels.sql import SQLDebugPanel

from ..base import BaseTestCase


class TemplateDebugPanelTestCase(BaseTestCase):

    def test_queryset_hook(self):
        template_panel = self.toolbar.get_panel(TemplateDebugPanel)
        sql_panel = self.toolbar.get_panel(SQLDebugPanel)
        t = Template("No context variables here!")
        c = Context({
            'queryset': User.objects.all(),
            'deep_queryset': {
                'queryset': User.objects.all(),
            }
        })
        t.render(c)
        # ensure the query was NOT logged
        self.assertEqual(len(sql_panel._queries), 0)
        base_ctx_idx = 1 if django.VERSION[:2] >= (1, 5) else 0
        ctx = template_panel.templates[0]['context'][base_ctx_idx]
        self.assertIn('<<queryset of auth.User>>', ctx)
        self.assertIn('<<triggers database query>>', ctx)
