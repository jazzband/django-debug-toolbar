from django.template.loader import render_to_string
from debug_toolbar.panels import DebugPanel

class HttpVarsDebugPanel(DebugPanel):
    """
    A panel to display HTTP variables (POST/GET).
    """
    name = 'HttpVars'

    def title(self):
        return 'POST/GET'

    def url(self):
        return ''

    def content(self):
        context = {
            'get': [(k, self.request.GET.getlist(k)) for k in self.request.GET.iterkeys()],
            'post': [(k, self.request.POST.getlist(k)) for k in self.request.POST.iterkeys()]
        }
        return render_to_string('debug_toolbar/panels/http_vars.html', context)