# coding: utf-8

from __future__ import absolute_import, unicode_literals

import django
from django.contrib.auth.models import User
from django.template import Context, RequestContext, Template

from ..base import BaseTestCase
from ..models import NonAsciiRepr


class TemplatesPanelTestCase(BaseTestCase):

    def setUp(self):
        super(TemplatesPanelTestCase, self).setUp()
        self.panel = self.toolbar.get_panel_by_id('TemplatesPanel')
        self.panel.enable_instrumentation()
        self.sql_panel = self.toolbar.get_panel_by_id('SQLPanel')
        self.sql_panel.enable_instrumentation()

    def tearDown(self):
        self.sql_panel.disable_instrumentation()
        self.panel.disable_instrumentation()
        super(TemplatesPanelTestCase, self).tearDown()

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
        self.assertEqual(len(self.sql_panel._queries), 0)

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
        self.assertIn('nôt åscíì', self.panel.content)

    def test_custom_context_processor(self):
        self.panel.process_request(self.request)
        t = Template("{{ content }}")
        c = RequestContext(self.request, processors=[context_processor])
        t.render(c)
        self.panel.process_response(self.request, self.response)
        self.assertIn('tests.panels.test_template.context_processor', self.panel.content)


def context_processor(request):
    return {'content': 'set by processor'}
