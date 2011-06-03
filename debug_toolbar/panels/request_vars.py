from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from debug_toolbar.panels import DebugPanel

class RequestVarsDebugPanel(DebugPanel):
    """
    A panel to display request variables (POST/GET, session, cookies).
    """
    name = 'RequestVars'
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

    def content(self):
        context = self.context.copy()

        if self.view_func is not None:
            module = self.view_func.__module__
            name = getattr(self.view_func, '__name__', None) or self.view_func.__class__.__name__
            view_func = '%s.%s' % (module, name)
        else:
            view_func = '<no view>'

        context.update({
            'get': [(k, self.request.GET.getlist(k)) for k in self.request.GET],
            'post': [(k, self.request.POST.getlist(k)) for k in self.request.POST],
            'cookies': [(k, self.request.COOKIES.get(k)) for k in self.request.COOKIES],
            'view_func': view_func,
            'view_args': self.view_args,
            'view_kwargs': self.view_kwargs
        })
        if hasattr(self.request, 'session'):
            context.update({
                'session': [(k, self.request.session.get(k)) for k in self.request.session.iterkeys()]
            })

        return render_to_string('debug_toolbar/panels/request_vars.html', context)
