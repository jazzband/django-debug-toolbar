"""Base DebugPanel class"""

class DebugPanel(object):
    """
    Base class for debug panels.
    """
    # name = Base
    has_content = False # If content returns something, set to true in subclass

    # Panel methods
    def __init__(self):
        pass

    def dom_id(self):
        return 'djDebug%sPanel' % (self.name.replace(' ', ''))

    def title(self):
        raise NotImplementedError

    def url(self):
        raise NotImplementedError

    def content(self):
        raise NotImplementedError

    # Standard middleware methods
    def process_request(self, request):
        pass

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_response(self, request, response):
        pass

