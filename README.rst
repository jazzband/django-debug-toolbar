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
- Request timer

If you have ideas for other panels please let us know.

Installation
============

#. Add the `debug_toolbar` directory to your Python path.

#. Add the following middleware to your project's `settings.py` file:

	``'debug_toolbar.middleware.DebugToolbarMiddleware',``

   Tying into middleware allows each panel to be instantiated on request and
   rendering to happen on response.

#. Add a tuple called `DEBUG_TOOLBAR_PANELS` to your ``settings.py`` file that
   specifies the full Python path to the panel that you want included in the 
   Toolbar.  This setting looks very much like the `MIDDLEWARE_CLASSES` setting.
   For example::

	DEBUG_TOOLBAR_PANELS = (
	    'debug_toolbar.panels.version.VersionDebugPanel',
	    'debug_toolbar.panels.sql.SQLDebugPanel',
	    'debug_toolbar.panels.timer.TimerDebugPanel',
	)

   You can change the ordering of this tuple to customize the order of the
   panels you want to display.

#. Add `debug_toolbar` to your `INSTALLED_APPS` setting so Django can find the
   the template files associated with the Debug Toolbar.

TODO
====
- Add more panels
- Panel idea: Show some commonly used settings from settings.py
- Panel idea: Show GET and POST variables
- Panel idea: Show HTTP header information
- Panel idea: AJAX call to show cprofile data similar to the ?prof idea
- Get fancy with CSS and Javascript
