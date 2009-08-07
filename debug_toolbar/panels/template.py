from os.path import normpath
from pprint import pformat

from django.conf import settings
from django.core.signals import request_started
from django.dispatch import Signal
from django.template.context import get_standard_processors
from django.template.loader import render_to_string
from django.test.signals import template_rendered
from debug_toolbar.panels import DebugPanel

# Code taken and adapted from Simon Willison and Django Snippets:
# http://www.djangosnippets.org/snippets/766/

# Monkeypatch instrumented test renderer from django.test.utils - we could use
# django.test.utils.setup_test_environment for this but that would also set up
# e-mail interception, which we don't want
from django.test.utils import instrumented_test_render
from django.template import Template
if Template.render != instrumented_test_render:
    Template.original_render = Template.render
    Template.render = instrumented_test_render
# MONSTER monkey-patch
old_template_init = Template.__init__
def new_template_init(self, template_string, origin=None, name='<Unknown Template>'):
    old_template_init(self, template_string, origin, name)
    self.origin = origin
Template.__init__ = new_template_init

class TemplateDebugPanel(DebugPanel):
    """
    A panel that lists all templates used during processing of a response.
    """
    name = 'Template'
    has_content = True

    def __init__(self):
        self.templates = []
        template_rendered.connect(self._storeTemplateInfo)

    def _storeTemplateInfo(self, sender, **kwargs):
        self.templates.append(kwargs)

    def title(self):
        return 'Templates'

    def url(self):
        return ''

    def process_request(self, request):
        self.request = request

    def content(self):
        context_processors = dict(
            [
                ("%s.%s" % (k.__module__, k.__name__),
                    pformat(k(self.request))) for k in get_standard_processors()
            ]
        )
        template_context = []
        for i, d in enumerate(self.templates):
            info = {}
            # Clean up some info about templates
            t = d.get('template', None)
            # Skip templates that we are generating through the debug toolbar.
            if t.name.startswith('debug_toolbar/'):
                continue
            if t.origin and t.origin.name:
                t.origin_name = t.origin.name
            else:
                t.origin_name = 'No origin'
            info['template'] = t
            # Clean up context for better readability
            c = d.get('context', None)
            
            d_list = []
            for _d in c.dicts:
                try:
                    d_list.append(pformat(d))
                except UnicodeEncodeError:
                    pass
            info['context'] = '\n'.join(d_list)
            template_context.append(info)
        context = {
            'templates': template_context,
            'template_dirs': [normpath(x) for x in settings.TEMPLATE_DIRS],
            'context_processors': context_processors,
        }
        return render_to_string('debug_toolbar/panels/templates.html', context)
