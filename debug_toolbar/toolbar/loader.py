"""
The main DebugToolbar class that loads and renders the Toolbar.
"""
class DebugToolbar(object):

    def __init__(self):
        self.panels = []
        self.panel_list = []
        self.content_list = []
    
    def load_panels(self):
        """
        Populate debug panel lists from settings.DEBUG_TOOLBAR_PANELS.
        """
        from django.conf import settings
        from django.core import exceptions

        for panel_path in settings.DEBUG_TOOLBAR_PANELS:
            try:
                dot = panel_path.rindex('.')
            except ValueError:
                raise exceptions.ImproperlyConfigured, '%s isn\'t a debug panel module' % panel_path
            panel_module, panel_classname = panel_path[:dot], panel_path[dot+1:]
            try:
                mod = __import__(panel_module, {}, {}, [''])
            except ImportError, e:
                raise exceptions.ImproperlyConfigured, 'Error importing debug panel %s: "%s"' % (panel_module, e)
            try:
                panel_class = getattr(mod, panel_classname)
            except AttributeError:
                raise exceptions.ImproperlyConfigured, 'Toolbar Panel module "%s" does not define a "%s" class' % (panel_module, panel_classname)

            try:
                panel_instance = panel_class()
            except:
                continue # Some problem loading panel

            self.panels.append(panel_instance)

    def render_panels(self):
        """
        Renders each panel.
        """
        for panel in self.panels:
            div_id = 'djDebug%sPanel' % (panel.title().replace(' ', ''))
            self.panel_list.append('<li><a title="%(title)s" href="%(url)s">%(title)s</a></li>' % ({
                'title': panel.title(),
                'url': panel.url() or '#',
            }))
            self.content_list.append('<div id="%(div_id)s" class="panelContent"><h1>%(title)s</h1>%(content)s</div>' % ({
                'div_id': div_id,
                'title': panel.title(),
                'content': panel.content(),
            }))

    def render_toolbar(self):
        """
        Renders the overall Toolbar with panels inside.
        """
        self.render_panels()
        template = """
            <div id="djDebugToolbar">
                <ul id="djDebugPanelList">
                    %(panels)s
                </ul>
                %(contents)s
            </div>
        """
        context = {
            'panels': ''.join(self.panel_list),
            'contents': ''.join(self.content_list),
        }
        return template % context
