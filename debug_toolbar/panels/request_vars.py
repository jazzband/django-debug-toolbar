from django.template.loader import render_to_string
from debug_toolbar.panels import DebugPanel

class RequestVarsDebugPanel(DebugPanel):
    """
    A panel to display request variables (POST/GET, session, cookies).
    """
    name = 'RequestVars'
    has_content = True

    def title(self):
        return 'Request Vars'

    def url(self):
        return ''

    def process_request(self, request):
        self.request = request

    def content(self):
        context = {
            'get': [(k, self.request.GET.getlist(k)) for k in self.request.GET.iterkeys()],
            'post': [(k, self.request.POST.getlist(k)) for k in self.request.POST.iterkeys()],
            'session': [(k, self.request.session.get(k)) for k in self.request.session.iterkeys()],
            'cookies': [(k, self.request.COOKIES.get(k)) for k in self.request.COOKIES.iterkeys()],
        }
        return render_to_string('debug_toolbar/panels/request_vars.html', context)