"""Base DebugPanel class"""

class DebugPanel(object):
    """
    Base class for debug panels.
    """
    # name = Base
    has_content = False # If content returns something, set to true in subclass
    
    def __init__(self, request):
        self.request = request

    def dom_id(self):
        return 'djDebug%sPanel' % (self.name.replace(' ', ''))

    def title(self):
        raise NotImplementedError

    def url(self):
        raise NotImplementedError

    def content(self):
        # TODO: This is a bit flaky in that panel.content() returns a string 
        # that gets inserted into the toolbar HTML template.
        raise NotImplementedError
