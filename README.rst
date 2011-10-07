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
- Logging output via Python's built-in logging, or via the `logbook <http://logbook.pocoo.org>`_ module

There is also one Django management command currently:

- `debugsqlshell`: Outputs the SQL that gets executed as you work in the Python
  interactive shell.  (See example below)

If you have ideas for other panels please let us know.

* Note: The Debug Toolbar only works on Django 1.1 and newer.

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

   Note: Be aware of middleware ordering and other middleware that may
   intercept requests and return responses.  Putting the debug toolbar
   middleware *after* the Flatpage middleware, for example, means the
   toolbar will not show up on flatpages.

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
     set to True or the IP of the request must be in INTERNAL_IPS.  You can
     provide your own method for displaying the toolbar which contains your
     custom logic.  This method should return True or False.

   * `EXTRA_SIGNALS`: An array of custom signals that might be in your project,
     defined as the python path to the signal.

   * `HIDE_DJANGO_SQL`: If set to True (the default) then code in Django itself
     won't be shown in SQL stacktraces.

   * `SHOW_TEMPLATE_CONTEXT`: If set to True (the default) then a template's
     context will be included with it in the Template debug panel.  Turning this
     off is useful when you have large template contexts, or you have template
     contexts with lazy datastructures that you don't want to be evaluated.

   * `TAG`: If set, this will be the tag to which debug_toolbar will attach the 
     debug toolbar. Defaults to 'body'.

   * `ENABLE_STACKTRACES`: If set, this will show stacktraces for SQL queries.
     Enabling stacktraces can increase the CPU time used when executing
     queries. Defaults to True.

   Example configuration::

	def custom_show_toolbar(request):
	    return True # Always show toolbar, for example purposes only.

	DEBUG_TOOLBAR_CONFIG = {
	    'INTERCEPT_REDIRECTS': False,
	    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
	    'EXTRA_SIGNALS': ['myproject.signals.MySignal'],
	    'HIDE_DJANGO_SQL': False,
	    'TAG': 'div',
	    'ENABLE_STACKTRACES' : True,
	}

`debugsqlshell`
===============
The following is sample output from running the `debugsqlshell` management
command.  Each ORM call that results in a database query will be beautifully
output in the shell::

    $ ./manage.py debugsqlshell
    Python 2.6.1 (r261:67515, Jul  7 2009, 23:51:51) 
    [GCC 4.2.1 (Apple Inc. build 5646)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    (InteractiveConsole)
    >>> from page.models import Page
    >>> ### Lookup and use resulting in an extra query...
    >>> p = Page.objects.get(pk=1)
    SELECT "page_page"."id",
           "page_page"."number",
           "page_page"."template_id",
           "page_page"."description"
    FROM "page_page"
    WHERE "page_page"."id" = 1
    
    >>> print p.template.name
    SELECT "page_template"."id",
           "page_template"."name",
           "page_template"."description"
    FROM "page_template"
    WHERE "page_template"."id" = 1
    
    Home
    >>> ### Using select_related to avoid 2nd database call...
    >>> p = Page.objects.select_related('template').get(pk=1)
    SELECT "page_page"."id",
           "page_page"."number",
           "page_page"."template_id",
           "page_page"."description",
           "page_template"."id",
           "page_template"."name",
           "page_template"."description"
    FROM "page_page"
    INNER JOIN "page_template" ON ("page_page"."template_id" = "page_template"."id")
    WHERE "page_page"."id" = 1
    
    >>> print p.template.name
    Home

Running the Tests
=================

The Debug Toolbar includes a limited (and growing) test suite. If you commit code, please consider
adding proper coverage (especially if it has a chance for a regression) in the test suite.

::

    python setup.py test


3rd Party Panels
================

A list of 3rd party panels can be found on the Django Debug Toolbar Github wiki:
https://github.com/django-debug-toolbar/django-debug-toolbar/wiki/3rd-Party-Panels

TODOs and BUGS
==============
See: https://github.com/django-debug-toolbar/django-debug-toolbar/issues
