====================
Django Debug Toolbar
====================

The Django Debug Toolbar is a configurable set of panels that display various
debug information about the current request/response and when clicked, display 
more details about the panel's content.

Currently, the following panels have been written and are working:

- Django version
- Request timer
- A list of settings in settings.py
- Common HTTP headers
- GET/POST/cookie/session variable display
- Templates and context used, and their template paths
- SQL queries including time to execute and links to EXPLAIN each query
- Cache stats
- Logging output via Python's built-in logging module

If you have ideas for other panels please let us know.

Installation
============

#. Add the `debug_toolbar` directory to your Python path.

#. Add the following middleware to your project's `settings.py` file:

	``'debug_toolbar.middleware.DebugToolbarMiddleware',``

   Tying into middleware allows each panel to be instantiated on request and
   rendering to happen on response.

   The order of MIDDLEWARE_CLASSES is important: the Debug Toolbar middleware 
   must come after any other middleware that encodes the response's content 
   (such as GZipMiddleware).

#. Make sure your IP is listed in the `INTERNAL_IPS` setting.  If you are
   working locally this will be:

	INTERNAL_IPS = ('127.0.0.1',)

#. Add `debug_toolbar` to your `INSTALLED_APPS` setting so Django can find the
   the template files associated with the Debug Toolbar.
   
   Alternatively, add the path to the debug toolbar templates
   (``'path/to/debug_toolbar/templates'`` to your ``TEMPLATE_DIRS`` setting.)

#. Optional: Add a tuple called `DEBUG_TOOLBAR_PANELS` to your ``settings.py`` 
   file that specifies the full Python path to the panel that you want included 
   in the Toolbar.  This setting looks very much like the `MIDDLEWARE_CLASSES` 
   setting.  For example::

	DEBUG_TOOLBAR_PANELS = (
	    'debug_toolbar.panels.version.VersionDebugPanel',
	    'debug_toolbar.panels.timer.TimerDebugPanel',
	    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
	    'debug_toolbar.panels.headers.HeaderDebugPanel',
	    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
	    'debug_toolbar.panels.template.TemplateDebugPanel',
	    'debug_toolbar.panels.sql.SQLDebugPanel',
	    'debug_toolbar.panels.cache.CacheDebugPanel',
	    'debug_toolbar.panels.logger.LoggingPanel',
	)

   You can change the ordering of this tuple to customize the order of the
   panels you want to display.  And you can include panels that you have created
   or that are specific to your project.

TODO
====
- Panel idea: AJAX call to show cprofile data similar to the ?prof idea
- CSS Stylings
- Restructure panels to popular context that pushes up to the toolbar
- Make the trigger whether to display the toolbar configurable with options such
  as if: DEBUG is true, IP is in INTERNAL_IPS, authenticated user is_superuser,
  etc.
