from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from debug_toolbar.panels import DebugPanel
from debug_toolbar.utils import get_name_from_obj

from django.core.urlresolvers import resolve
from django.http import Http404

class RequestVarsDebugPanel(DebugPanel):
    """
    A panel to display request variables (POST/GET, session, cookies).
    """
    name = 'RequestVars'
    has_content = True

    def __init__(self, *args, **kwargs):
        DebugPanel.__init__(self, *args, **kwargs)

    def nav_title(self):
        return _('Request Vars')

    def title(self):
        return _('Request Vars')

    def url(self):
        return ''

    def process_request(self, request):
        self.request = request

    def content(self):
        context = self.context.copy()

        context.update({
            'get': [(k, self.request.GET.getlist(k)) for k in self.request.GET],
            'post': [(k, self.request.POST.getlist(k)) for k in self.request.POST],
            'cookies': [(k, self.request.COOKIES.get(k)) for k in self.request.COOKIES],
        })

        context['view_func'] = '<no view>'
        context['view_args'] = 'None'
        context['view_kwargs'] = 'None'
        context['view_urlname'] = 'None'

        try:
            match = resolve(self.request.path)
            func, args, kwargs = match
            context['view_func'] = get_name_from_obj(func)
            context['view_args'] = args
            context['view_kwargs'] = kwargs
            if hasattr(match, 'url_name'):  # Django 1.3
                context['view_urlname'] = match.url_name
        except Http404:
            pass

        if hasattr(self.request, 'session'):
            context.update({
                'session': [(k, self.request.session.get(k)) for k in self.request.session.iterkeys()]
            })

        return render_to_string('debug_toolbar/panels/request_vars.html', context)
