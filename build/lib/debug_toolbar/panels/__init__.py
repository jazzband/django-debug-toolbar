from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from debug_toolbar.middleware import DebugToolbarMiddleware


class DebugPanel(object):
    """
    Base class for debug panels.
    """
    # name = 'Base'
    # template = 'debug_toolbar/panels/base.html'
    has_content = False # If content returns something, set to true in subclass
    
    # We'll maintain a local context instance so we can expose our template
    # context variables to panels which need them:
    context = {}
    
    # Panel methods
    def __init__(self, context={}):
        self.context.update(context)
        self.slug = slugify(self.name)
    
    def dom_id(self):
        return 'djDebug%sPanel' % (self.name.replace(' ', ''))
    
    def nav_title(self):
        """Title showing in toolbar"""
        raise NotImplementedError
    
    def nav_subtitle(self):
        """Subtitle showing until title in toolbar"""
        return ''
    
    def title(self):
        """Title showing in panel"""
        raise NotImplementedError
    
    def url(self):
        raise NotImplementedError
    
    def content(self):
        if self.has_content:
            context = self.context.copy()
            context.update(self.get_stats())
            return render_to_string(self.template, context)
    
    def record_stats(self, stats):
        toolbar = DebugToolbarMiddleware.get_current()
        panel_stats = toolbar.stats.get(self.slug)
        if panel_stats:
            panel_stats.update(stats)
        else:
            toolbar.stats[self.slug] = stats
    
    def get_stats(self):
        toolbar = DebugToolbarMiddleware.get_current()
        return toolbar.stats.get(self.slug, {})
    
    # Standard middleware methods
    def process_request(self, request):
        pass
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        pass
    
    def process_response(self, request, response):
        pass
