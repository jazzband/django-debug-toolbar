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
- List of signals, their args and receivers
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

   Note: The debug toolbar will only display itself if the mimetype of the
   response is either `text/html` or `application/xhtml+xml` and contains a
   closing `</body>` tag.

#. Make sure your IP is listed in the `INTERNAL_IPS` setting.  If you are
   working locally this will be:

	INTERNAL_IPS = ('127.0.0.1',)

   Note: This is required because of the built-in requirements of the
   `show_toolbar` method.  See below for how to define a method to determine
   your own logic for displaying the toolbar.

#. Add `debug_toolbar` to your `INSTALLED_APPS` setting so Django can find the
   template files associated with the Debug Toolbar.

   Alternatively, add the path to the debug toolbar templates
   (``'path/to/debug_toolbar/templates'`` to your ``TEMPLATE_DIRS`` setting.)

Configuration
=============

The debug toolbar has two settings that can be set in `settings.py`:

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
	    'debug_toolbar.panels.signals.SignalDebugPanel',
	    'debug_toolbar.panels.logger.LoggingPanel',
	)

   You can change the ordering of this tuple to customize the order of the
   panels you want to display, or add/remove panels.  If you have custom panels
   you can include them in this way -- just provide the full Python path to
   your panel.

#. Optional: There are a few configuration options to the debug toolbar that
   can be placed in a dictionary:

   * `INTERCEPT_REDIRECTS`: If set to True (default), the debug toolbar will
     show an intermediate page upon redirect so you can view any debug
     information prior to redirecting.  This page will provide a link to the
     redirect destination you can follow when ready.  If set to False, redirects
     will proceed as normal.

   * `SHOW_TOOLBAR_CALLBACK`: If not set or set to None, the debug_toolbar
     middleware will use its built-in show_toolbar method for determining whether
     the toolbar should show or not.  The default checks are that DEBUG must be
     set to True and the IP of the request must be in INTERNAL_IPS.  You can
     provide your own method for displaying the toolbar which contains your
     custom logic.  This method should return True or False.

   * `EXTRA_SIGNALS`: An array of custom signals that might be in your project,
     defined as the python path to the signal.

   * `HIDE_DJANGO_SQL`: If set to True (the default) then code in Django itself
     won't be show in SQL stacktraces.

   * `SHOW_TEMPLATE_CONTEXT`: If set to True (the default) then a template's
     context will be included with it in the Template debug panel.  Turning this
     off is useful when you have large template contexts, or you have template
     contexts with lazy datastructures that you don't want to be evaluated.

   Example configuration::

	def custom_show_toolbar(request):
	    return True # Always show toolbar, for example purposes only.

	DEBUG_TOOLBAR_CONFIG = {
	    'INTERCEPT_REDIRECTS': False,
	    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
	    'EXTRA_SIGNALS': ['myproject.signals.MySignal'],
	    'HIDE_DJANGO_SQL': False,
	}

TODOs and BUGS
==============
See: http://github.com/robhudson/django-debug-toolbar/issues
