"""Base DebugPanel class"""

class DebugPanel(object):
    """
    Base class for debug panels.
    """
    def dom_id(self):
        return 'djDebug%sPanel' % (self.title().replace(' ', ''))

    def title(self):
        raise NotImplementedError

    def url(self):
        raise NotImplementedError

    def content(self):
        raise NotImplementedError
