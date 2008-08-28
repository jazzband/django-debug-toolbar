"""Base DebugPanel class"""

class DebugPanel(object):
    """
    Base class for debug panels.
    """
    def title(self):
        raise NotImplementedError

    def url(self):
        raise NotImplementedError

    def content(self):
        raise NotImplementedError
