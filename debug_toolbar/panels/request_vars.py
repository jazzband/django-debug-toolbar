from django.core.urlresolvers import resolve
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from debug_toolbar.panels import DebugPanel
from debug_toolbar.utils import get_name_from_obj


class RequestVarsDebugPanel(DebugPanel):
    """
    A panel to display request variables (POST/GET, session, cookies).
    """
    name = 'RequestVars'
    template = 'debug_toolbar/panels/request_vars.html'
    has_content = True

    def nav_title(self):
        return _('Request Vars')

    def title(self):
        return _('Request Vars')

    def url(self):
        return ''

    def process_request(self, request):
        self.request = request

    def process_response(self, request, response):
        self.record_stats({
            'get': [(k, self.request.GET.getlist(k)) for k in self.request.GET],
            'post': [(k, self.request.POST.getlist(k)) for k in self.request.POST],
            'cookies': [(k, self.request.COOKIES.get(k)) for k in self.request.COOKIES],
        })
        view_info = {
             'view_func': _('<no view>'),
             'view_args': 'None',
             'view_kwargs': 'None',
             'view_urlname': 'None',
         }
        try:
            match = resolve(self.request.path)
            func, args, kwargs = match
            view_info['view_func'] = get_name_from_obj(func)
            view_info['view_args'] = args
            view_info['view_kwargs'] = kwargs
            view_info['view_urlname'] = getattr(match, 'url_name',
                                                _('<unavailable>'))
        except Http404:
            pass
        self.record_stats(view_info)

        if hasattr(self.request, 'session'):
            self.record_stats({
                'session': [(k, self.request.session.get(k))
                            for k in self.request.session.iterkeys()]
                })
