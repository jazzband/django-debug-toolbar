from __future__ import absolute_import, unicode_literals

from django.http import HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template import TemplateDoesNotExist
from django.template.engine import Engine
from django.utils.safestring import mark_safe

from debug_toolbar.decorators import require_show_toolbar

try:
    from django.template import Origin
except ImportError:
    Origin = None


@require_show_toolbar
def template_source(request):
    """
    Return the source of a template, syntax-highlighted by Pygments if
    it's available.
    """
    template_origin_name = request.GET.get('template_origin', None)
    if template_origin_name is None:
        return HttpResponseBadRequest('"template_origin" key is required')
    template_name = request.GET.get('template', template_origin_name)

    final_loaders = []
    loaders = Engine.get_default().template_loaders

    for loader in loaders:
        if loader is not None:
            # When the loader has loaders associated with it,
            # append those loaders to the list. This occurs with
            # django.template.loaders.cached.Loader
            if hasattr(loader, 'loaders'):
                final_loaders += loader.loaders
            else:
                final_loaders.append(loader)

    for loader in final_loaders:
        if Origin:  # django>=1.9
            origin = Origin(template_origin_name)
            try:
                source = loader.get_contents(origin)
                break
            except TemplateDoesNotExist:
                pass
        else:  # django<1.9
            try:
                source, _ = loader.load_template_source(template_name)
                break
            except TemplateDoesNotExist:
                pass
    else:
        source = "Template Does Not Exist: %s" % (template_origin_name,)

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
