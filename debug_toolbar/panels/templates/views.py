from __future__ import absolute_import, unicode_literals

from django.http import HttpResponseBadRequest
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist
from django.template.loader import find_template_loader
from django.utils.safestring import mark_safe


def template_source(request):
    """
    Return the source of a template, syntax-highlighted by Pygments if
    it's available.
    """
    template_name = request.GET.get('template', None)
    if template_name is None:
        return HttpResponseBadRequest('"template" key is required')

    loaders = []
    for loader_name in settings.TEMPLATE_LOADERS:
        loader = find_template_loader(loader_name)
        if loader is not None:
            loaders.append(loader)
    for loader in loaders:
        try:
            source, display_name = loader.load_template_source(template_name)
            break
        except TemplateDoesNotExist:
            source = "Template Does Not Exist: %s" % (template_name,)

    try:
        from pygments import highlight
        from pygments.lexers import HtmlDjangoLexer
        from pygments.formatters import HtmlFormatter

        source = highlight(source, HtmlDjangoLexer(), HtmlFormatter())
        source = mark_safe(source)
        source.pygmentized = True
    except ImportError:
        pass

    # Using render_to_response avoids running global context processors.
    return render_to_response('debug_toolbar/panels/template_source.html', {
        'source': source,
        'template_name': template_name
    })
