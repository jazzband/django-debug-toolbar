from __future__ import absolute_import, unicode_literals

from os.path import normpath
from pprint import pformat

import django
from django import http
from django.conf import settings
from django.conf.urls import patterns, url
from django.db.models.query import QuerySet, RawQuerySet
from django.template.context import get_standard_processors
from django.test.signals import template_rendered
from django.utils.encoding import force_text
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from debug_toolbar.panels import Panel
from debug_toolbar.panels.sql.tracking import recording, SQLQueryTriggered

# Code taken and adapted from Simon Willison and Django Snippets:
# http://www.djangosnippets.org/snippets/766/

# Monkey-patch to enable the template_rendered signal. The receiver returns
# immediately when the panel is disabled to keep the overhead small.

from django.test.utils import instrumented_test_render
from django.template import Template

if Template._render != instrumented_test_render:
    Template.original_render = Template._render
    Template._render = instrumented_test_render


if django.VERSION[:2] < (1, 7):
    # Monkey-patch versions of Django where Template doesn't store origin.
    # See https://code.djangoproject.com/ticket/16096.

    old_template_init = Template.__init__

    def new_template_init(self, template_string, origin=None, name='<Unknown Template>'):
        old_template_init(self, template_string, origin, name)
        self.origin = origin

    Template.__init__ = new_template_init


class TemplatesPanel(Panel):
    """
    A panel that lists all templates used during processing of a response.
    """
    name = 'Templates'
    template = 'debug_toolbar/panels/templates.html'
    has_content = True

    def __init__(self, *args, **kwargs):
        super(TemplatesPanel, self).__init__(*args, **kwargs)
        self.templates = []
        template_rendered.connect(self._store_template_info)

    def _store_template_info(self, sender, **kwargs):
        if not self.enabled:
            return

        template, context = kwargs['template'], kwargs['context']

        # Skip templates that we are generating through the debug toolbar.
        if (isinstance(template.name, six.string_types) and
                template.name.startswith('debug_toolbar/')):
            return

        context_list = []
        for context_layer in context.dicts:
            temp_layer = {}
            if hasattr(context_layer, 'items'):
                for key, value in context_layer.items():
                    # Replace any request elements - they have a large
                    # unicode representation and the request data is
                    # already made available from the Request panel.
                    if isinstance(value, http.HttpRequest):
                        temp_layer[key] = '<<request>>'
                    # Replace the debugging sql_queries element. The SQL
                    # data is already made available from the SQL panel.
                    elif key == 'sql_queries' and isinstance(value, list):
                        temp_layer[key] = '<<sql_queries>>'
                    # Replace LANGUAGES, which is available in i18n context processor
                    elif key == 'LANGUAGES' and isinstance(value, tuple):
                        temp_layer[key] = '<<languages>>'
                    # QuerySet would trigger the database: user can run the query from SQL Panel
                    elif isinstance(value, (QuerySet, RawQuerySet)):
                        model_name = "%s.%s" % (
                            value.model._meta.app_label, value.model.__name__)
                        temp_layer[key] = '<<%s of %s>>' % (
                            value.__class__.__name__.lower(), model_name)
                    else:
                        try:
                            recording(False)
                            pformat(value)  # this MAY trigger a db query
                        except SQLQueryTriggered:
                            temp_layer[key] = '<<triggers database query>>'
                        except UnicodeEncodeError:
                            temp_layer[key] = '<<unicode encode error>>'
                        except Exception:
                            temp_layer[key] = '<<unhandled exception>>'
                        else:
                            temp_layer[key] = value
                        finally:
                            recording(True)
            try:
                context_list.append(pformat(temp_layer))
            except UnicodeEncodeError:
                pass

        kwargs['context'] = [force_text(item) for item in context_list]
        self.templates.append(kwargs)

    @classmethod
    def get_urls(cls):
        return patterns('debug_toolbar.panels.templates.views',         # noqa
            url(r'^template_source/$', 'template_source', name='template_source'),
        )

    def nav_title(self):
        return _('Templates')

    def title(self):
        num_templates = len(self.templates)
        return _('Templates (%(num_templates)s rendered)') % {'num_templates': num_templates}

    def process_response(self, request, response):
        context_processors = dict(
            [
                ("%s.%s" % (k.__module__, k.__name__),
                    pformat(k(request))) for k in get_standard_processors()
            ]
        )
        template_context = []
        for template_data in self.templates:
            info = {}
            # Clean up some info about templates
            template = template_data.get('template', None)
            if not hasattr(template, 'origin'):
                continue
            if template.origin and template.origin.name:
                template.origin_name = template.origin.name
            else:
                template.origin_name = 'No origin'
            info['template'] = template
            # Clean up context for better readability
            if self.toolbar.config['SHOW_TEMPLATE_CONTEXT']:
                context_list = template_data.get('context', [])
                info['context'] = '\n'.join(context_list)
            template_context.append(info)

        self.record_stats({
            'templates': template_context,
            'template_dirs': [normpath(x) for x in settings.TEMPLATE_DIRS],
            'context_processors': context_processors,
        })
