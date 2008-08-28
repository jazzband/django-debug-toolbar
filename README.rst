====================
Django Debug Toolbar
====================

The Django Debug Toolbar is a configurable set of panels that display various
debug information about the current request/response.  It is a small toolbar
that, when activated, situates itself in the top-right location of the browser
window.  When particular panels are clicked, more details about that panel's
content are displayed.

Currently, the following panels have been written and are working:

- Django version
- SQL queries including time to execute

If you have ideas for other panels please let us know.

Installation
============

#. Add the `debug_toolbar` directory to your Python path.

#. Add the following middleware to your project's `settings.py` file:

	``'debug_toolbar.middleware.DebugToolbarMiddleware',``

#. Add a tuple called `DEBUG_TOOLBAR_PANELS` to your ``settings.py`` file that
   specifies the full Python path to the panel that you want included in the 
   Toolbar.  This setting looks very much like the `MIDDLEWARE_CLASSES` setting.
   For example::

	DEBUG_TOOLBAR_PANELS = (
	    'debug_toolbar.panels.version.VersionDebugPanel',
	    'debug_toolbar.panels.sql.SQLDebugPanel',
	)

TODO
====
- Add more panels
- Get fancy with CSS and Javascript
