from __future__ import absolute_import, unicode_literals

import os

from django.http import HttpResponse, HttpResponseBadRequest
from django.template.response import SimpleTemplateResponse
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from debug_toolbar.decorators import require_show_toolbar
from debug_toolbar.toolbar import DebugToolbar

from .forms import ViewFileForm


@require_show_toolbar
def render_panel(request):
    """Render the contents of a panel"""
    toolbar = DebugToolbar.fetch(request.GET['store_id'])
    if toolbar is None:
        content = _("Data for this panel isn't available anymore. "
                    "Please reload the page and retry.")
        content = "<p>%s</p>" % escape(content)
    else:
        panel = toolbar.get_panel_by_id(request.GET['panel_id'])
        content = panel.content
    return HttpResponse(content)


@csrf_exempt
@require_show_toolbar
def render_file(request):
    """Render content of given file"""
    form = ViewFileForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest('Form errors')

    full_path = form.cleaned_data['full_path']

    with open(full_path, 'r') as fid:
        lines = fid.read().splitlines()

    context = {
        'hash': form.cleaned_data['hash'],
        'full_path': full_path,
        'filename': os.path.basename(full_path),
        'lines': lines,
        'line_no': form.cleaned_data['line_no'],
        'lines_length': len(str(len(lines))),
    }

    # Using SimpleTemplateResponse avoids running global context processors.
    return SimpleTemplateResponse('debug_toolbar/file.html', context)
