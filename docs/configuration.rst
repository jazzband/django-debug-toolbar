Configuration
=============

The debug toolbar has two settings that can be set in ``settings.py``.

#. Optional: Add a tuple called ``DEBUG_TOOLBAR_PANELS`` to your ``settings.py``
   file that specifies the full Python path to the panel that you want included
   in the Toolbar. This setting looks very much like the ``MIDDLEWARE_CLASSES``
   setting. For example::

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
   panels you want to display, or add/remove panels. If you have custom panels
   you can include them in this way -- just provide the full Python path to
   your panel.

#. Optional: There are a few configuration options to the debug toolbar that
   can be placed in a dictionary called ``DEBUG_TOOLBAR_CONFIG``:

   * ``INTERCEPT_REDIRECTS``

     If set to True, the debug toolbar will show an intermediate page upon
     redirect so you can view any debug information prior to redirecting. This
     page will provide a link to the redirect destination you can follow when
     ready. If set to False (default), redirects will proceed as normal.

   * ``SHOW_TOOLBAR_CALLBACK``

     If not set or set to None, the debug_toolbar
     middleware will use its built-in show_toolbar method for determining whether
     the toolbar should show or not. The default checks are that DEBUG must be
     set to True and the IP of the request must be in INTERNAL_IPS. You can
     provide your own method for displaying the toolbar which contains your
     custom logic. This method should return True or False.

   * ``EXTRA_SIGNALS``

     An array of custom signals that might be in your project,
     defined as the python path to the signal.

   * ``HIDE_DJANGO_SQL``

     If set to True (the default) then code in Django itself
     won't be shown in SQL stacktraces.

   * ``SHOW_TEMPLATE_CONTEXT``

     If set to True (the default) then a template's
     context will be included with it in the Template debug panel. Turning this
     off is useful when you have large template contexts, or you have template
     contexts with lazy datastructures that you don't want to be evaluated.

   * ``TAG``

     If set, this will be the tag to which debug_toolbar will attach the
     debug toolbar. Defaults to 'body'.

   * ``ENABLE_STACKTRACES``

     If set, this will show stacktraces for SQL queries
     and cache calls. Enabling stacktraces can increase the CPU time used when
     executing queries. Defaults to True.

   * ``HIDDEN_STACKTRACE_MODULES``

     Useful for eliminating server-related entries which can result
     in enormous DOM structures and toolbar rendering delays.
     Default: ``('socketserver', 'threading', 'wsgiref', 'debug_toolbar')``.

     (The first value is ``socketserver`` on Python 3 and ``SocketServer`` on
     Python 2.)

   * ``ROOT_TAG_ATTRS``

     This setting is injected in the root template div in order to avoid conflicts
     with client-side frameworks. For example, when using with Angular.js, set
     this to 'ng-non-bindable' or 'class="ng-non-bindable"'. Defaults to ''.

   * ``SQL_WARNING_THRESHOLD``

     The SQL panel highlights queries that took more that this amount of time,
     in milliseconds, to execute. The default is 500.

   Example configuration::

       def custom_show_toolbar(request):
           return True  # Always show toolbar, for example purposes only.

       DEBUG_TOOLBAR_CONFIG = {
           'INTERCEPT_REDIRECTS': True,
           'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
           'EXTRA_SIGNALS': ['myproject.signals.MySignal'],
           'HIDE_DJANGO_SQL': False,
           'TAG': 'div',
           'ENABLE_STACKTRACES': True,
           'HIDDEN_STACKTRACE_MODULES': ('gunicorn', 'newrelic'),
       }

   * ``RESULTS_CACHE_SIZE``

     The toolbar keeps up to this many results in memory. Defaults to 10.
