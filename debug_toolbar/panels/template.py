from os.path import normpath
from pprint import pformat

from django import http
from django.conf import settings
from django.template.context import get_standard_processors
from django.template.loader import render_to_string
from django.test.signals import template_rendered
from django.utils.translation import ugettext_lazy as _
from debug_toolbar.panels import DebugPanel

def render_decorator(r):
    """
    Decorate a Template's render function, r, to emit the signals
    needed by DjDT.
    """
    
    def render(self, context):
        template_rendered.send(
            sender=self, template=self, context=context)
        return r(self, context)

    render.decorated = True
    
    return render

# MONSTER monkey-patch
template_source_loaders = None
def find_template_and_decorate(name, dirs=None):
    # Calculate template_source_loaders the first time the function is executed
    # because putting this logic in the module-level namespace may cause
    # circular import errors. See Django ticket #1292.

    from django.template.loader import find_template_loader, make_origin
    from django.template import TemplateDoesNotExist
    global template_source_loaders
    if template_source_loaders is None:
        loaders = []
        for loader_name in settings.TEMPLATE_LOADERS:
            loader = find_template_loader(loader_name)
            if loader is not None:
                loaders.append(loader)
        template_source_loaders = tuple(loaders)
    for loader in template_source_loaders:
        try:
            source, display_name = loader(name, dirs)

            # see if this template has a render method, and if so
            # decorate it to emit signals when rendering happens
            if hasattr(source, 'render'):
                if not hasattr(source.render, 'decorated'):

                    # this class has not been decorated yet...
                    source.__class__.render = render_decorator(
                        source.__class__.render)
                
            return (source, make_origin(display_name, loader, name, dirs))
        except TemplateDoesNotExist:
            pass
    raise TemplateDoesNotExist(name)

import django.template.loader
django.template.loader.find_template = find_template_and_decorate

class TemplateDebugPanel(DebugPanel):
    """
    A panel that lists all templates used during processing of a response.
    """
    name = 'Template'
    has_content = True

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.templates = []
        template_rendered.connect(self._store_template_info)

    def _store_template_info(self, sender, **kwargs):
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

    def content(self):
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
            if hasattr(template, 'name') and template.name.startswith('debug_toolbar/'):
                continue
            if hasattr(template, 'origin') and template.origin.name:
                template.origin_name = template.origin.name
            else:
                template.origin_name = 'No origin'
            info['template'] = template
            # Clean up context for better readability
            if getattr(settings, 'DEBUG_TOOLBAR_CONFIG', {}).get('SHOW_TEMPLATE_CONTEXT', True):
                context_data = template_data.get('context', None)

                context_list = []
                for context_layer in context_data.dicts:
                    if hasattr(context_layer, 'items'):
                        for key, value in context_layer.items():
                            # Replace any request elements - they have a large
                            # unicode representation and the request data is
                            # already made available from the Request Vars panel.
                            if isinstance(value, http.HttpRequest):
                                context_layer[key] = '<<request>>'
                            # Replace the debugging sql_queries element. The SQL
                            # data is already made available from the SQL panel.
                            elif key == 'sql_queries' and isinstance(value, list):
                                context_layer[key] = '<<sql_queries>>'
                            # Replace LANGUAGES, which is available in i18n context processor
                            elif key == 'LANGUAGES' and isinstance(value, tuple):
                                context_layer[key] = '<<languages>>'
                    try:
                        context_list.append(pformat(context_layer))
                    except UnicodeEncodeError:
                        pass
                info['context'] = '\n'.join(context_list)
            template_context.append(info)

        context = self.context.copy()
        context.update({
            'templates': template_context,
            'template_dirs': [normpath(x) for x in settings.TEMPLATE_DIRS],
            'context_processors': context_processors,
        })

        return render_to_string('debug_toolbar/panels/templates.html', context)
