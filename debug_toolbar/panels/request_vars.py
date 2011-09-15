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
    
    def __init__(self, *args, **kwargs):
        DebugPanel.__init__(self, *args, **kwargs)
        self.view_func = None
        self.view_args = None
        self.view_kwargs = None
    
    def nav_title(self):
        return _('Request Vars')
    
    def title(self):
        return _('Request Vars')
    
    def url(self):
        return ''
    
    def process_request(self, request):
        self.request = request
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        self.view_func = view_func
        self.view_args = view_args
        self.view_kwargs = view_kwargs
    
    def process_response(self, request, response):
        self.record_stats({
            'get': [(k, self.request.GET.getlist(k)) for k in self.request.GET],
            'post': [(k, self.request.POST.getlist(k)) for k in self.request.POST],
            'cookies': [(k, self.request.COOKIES.get(k)) for k in self.request.COOKIES],
        })
        
        if hasattr(self, 'view_func'):
            if self.view_func is not None:
                name = get_name_from_obj(self.view_func)
            else:
                name = '<no view>'
            
            self.record_stats({
                'view_func': name,
                'view_args': self.view_args,
                'view_kwargs': self.view_kwargs
            })
        
        if hasattr(self.request, 'session'):
            self.record_stats({
                'session': [(k, self.request.session.get(k)) for k in self.request.session.iterkeys()]
            })
