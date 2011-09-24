from os.path import normpath
from pprint import pformat

from django import http
from django.conf import settings
from django.db.models.query import QuerySet
from django.template.context import get_standard_processors
from django.test.signals import template_rendered
from django.utils.translation import ugettext_lazy as _
from debug_toolbar.panels import DebugPanel

# Code taken and adapted from Simon Willison and Django Snippets:
# http://www.djangosnippets.org/snippets/766/

# Monkeypatch instrumented test renderer from django.test.utils - we could use
# django.test.utils.setup_test_environment for this but that would also set up
# e-mail interception, which we don't want
from django.test.utils import instrumented_test_render
from django.template import Template

if not hasattr(Template, '_render'): # Django < 1.2
    if Template.render != instrumented_test_render:
        Template.original_render = Template.render
        Template.render = instrumented_test_render
else:
    if Template._render != instrumented_test_render:
        Template.original_render = Template._render
        Template._render = instrumented_test_render


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
    template = 'debug_toolbar/panels/templates.html'
    has_content = True
    
    def __init__(self, *args, **kwargs):
        super(TemplateDebugPanel, self).__init__(*args, **kwargs)
        self.templates = []
        template_rendered.connect(self._store_template_info)
    
    def _store_template_info(self, sender, **kwargs):
        context_data = kwargs['context']
        
        context_list = []
        for context_layer in context_data.dicts:
            temp_layer = {}
            if hasattr(context_layer, 'items'):
                for key, value in context_layer.items():
                    # Replace any request elements - they have a large
                    # unicode representation and the request data is
                    # already made available from the Request Vars panel.
                    if isinstance(value, http.HttpRequest):
                        temp_layer[key] = '<<request>>'
                    # Replace the debugging sql_queries element. The SQL
                    # data is already made available from the SQL panel.
                    elif key == 'sql_queries' and isinstance(value, list):
                        temp_layer[key] = '<<sql_queries>>'
                    # Replace LANGUAGES, which is available in i18n context processor
                    elif key == 'LANGUAGES' and isinstance(value, tuple):
                        temp_layer[key] = '<<languages>>'
                    # Replace any query object. The representation
                    # executes the query.
                    elif isinstance(value, QuerySet):
                        temp_layer[key] = '<<query>>'
                    else:
                        temp_layer[key] = value
            try:
                context_list.append(pformat(temp_layer))
            except UnicodeEncodeError:
                pass
        kwargs['context'] = context_list
        self.templates.append(kwargs)
    
    def nav_title(self):
        return _('Templates')
    
    def title(self):
        num_templates = len([t for t in self.templates
            if not (t['template'].name and t['template'].name.startswith('debug_toolbar/'))])
        return _('Templates (%(num_templates)s rendered)') % {'num_templates': num_templates}
    
    def url(self):
        return ''
    
    def process_request(self, request):
        self.request = request
    
    def process_response(self, request, response):
        context_processors = dict(
            [
                ("%s.%s" % (k.__module__, k.__name__),
                    pformat(k(self.request))) for k in get_standard_processors()
            ]
        )
        template_context = []
        for template_data in self.templates:
            info = {}
            # Clean up some info about templates
            template = template_data.get('template', None)
            # Skip templates that we are generating through the debug toolbar.
            if template.name and template.name.startswith('debug_toolbar/'):
                continue
            if not hasattr(template, 'origin'):
                continue
            if template.origin and template.origin.name:
                template.origin_name = template.origin.name
            else:
                template.origin_name = 'No origin'
            info['template'] = template
            # Clean up context for better readability
            if getattr(settings, 'DEBUG_TOOLBAR_CONFIG', {}).get('SHOW_TEMPLATE_CONTEXT', True):
                context_list = template_data.get('context', [])
                info['context'] = '\n'.join(context_list)
            template_context.append(info)
        
        self.record_stats({
            'templates': template_context,
            'template_dirs': [normpath(x) for x in settings.TEMPLATE_DIRS],
            'context_processors': context_processors,
        })
