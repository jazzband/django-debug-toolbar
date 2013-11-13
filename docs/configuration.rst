Configuration
=============

The debug toolbar provides two settings that you can add in your project's
settings module to customize its behavior.

DEBUG_TOOLBAR_PANELS
--------------------

This setting specifies the full Python path to each panel that you want
included in the toolbar. It works like Django's ``MIDDLEWARE_CLASSES``
setting. The default value is::

    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.cache.CacheDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
    )

This setting allows you to:

* add built-in panels that aren't enabled by default,
* add third-party panels,
* remove built-in panels,
* change the order of panels.

DEBUG_TOOLBAR_CONFIG
--------------------

This dictionary contains all other configuration options. Some apply to the
toolbar itself, others are specific to some panels.

Toolbar options
~~~~~~~~~~~~~~~

* ``RENDER_PANELS``

  Default: ``None``

  If set to ``False``, the debug toolbar will keep the contents of panels in
  memory on the server and load them on demand. If set to ``True``, it will
  render panels inside every page. This may slow down page rendering but it's
  required on multi-process servers, for example if you deploy the toolbar in
  production (which isn't recommended).

  The default value of ``None`` tells the toolbar to automatically do the
  right thing depending on whether the WSGI container runs multiple processes.
  This setting allows you to force a different behavior if needed.

* ``INTERCEPT_REDIRECTS``

  Default: ``False``

  If set to ``True``, the debug toolbar will show an intermediate page upon
  redirect so you can view any debug information prior to redirecting. This
  page will provide a link to the redirect destination you can follow when
  ready. If set to ``False``, redirects will proceed as normal.

* ``RESULTS_CACHE_SIZE``

  Default: ``10``

  The toolbar keeps up to this many results in memory.

* ``ROOT_TAG_ATTRS``

  Default: ``''``

  This setting is injected in the root template div in order to avoid
  conflicts with client-side frameworks. For example, when using the debug
  toolbar with Angular.js, set this to ``'ng-non-bindable'`` or
  ``'class="ng-non-bindable"'``.

* ``SHOW_TOOLBAR_CALLBACK``

  Default: ``None``

  If set to ``None``, the debug toolbar middleware will use its built-in
  ``show_toolbar`` method for determining whether the toolbar should show or
  not. The default checks are that ``DEBUG`` must be set to ``True`` and the
  IP of the request must be in ``INTERNAL_IPS``. You can provide your own
  method for displaying the toolbar which contains your custom logic. This
  method should return ``True`` or ``False``.

* ``TAG``

  Default: ``'body'``

  If set, this will be the closing tag to which the debug toolbar will attach
  itself.

Panel options
~~~~~~~~~~~~~

* ``EXTRA_SIGNALS``

  Default: ``[]``

  Panel: signals

  A list of custom signals that might be in your project, defined as the
  Python path to the signal.

* ``ENABLE_STACKTRACES``

  Default: ``True``

  Panels: cache, SQL

  If set to ``True``, this will show stacktraces for SQL queries and cache
  calls. Enabling stacktraces can increase the CPU time used when executing
  queries.

* ``HIDDEN_STACKTRACE_MODULES``

  Default: ``('socketserver', 'threading', 'wsgiref', 'debug_toolbar')``. The
  first value is ``socketserver`` on Python 3 and ``SocketServer`` on Python
  2.

  Panels: cache, SQL

  Useful for eliminating server-related entries which can result
  in enormous DOM structures and toolbar rendering delays.

* ``HIDE_DJANGO_SQL``

  Default: ``True``

  Panels: cache, SQL

  If set to ``True`` then code in Django itself won't be shown in
  stacktraces.

* ``SHOW_TEMPLATE_CONTEXT``

  Default: ``True``

  Panel: templates

  If set to ``True`` then a template's context will be included with it in the
  template debug panel. Turning this off is useful when you have large
  template contexts, or you have template contexts with lazy datastructures
  that you don't want to be evaluated.

* ``SQL_WARNING_THRESHOLD``

  Default: ``500``

  Panel: SQL

  The SQL panel highlights queries that took more that this amount of time,
  in milliseconds, to execute.

Here's an example::

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
