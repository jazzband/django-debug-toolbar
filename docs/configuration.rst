Configuration
=============

The debug toolbar provides two settings that you can add in your project's
settings module to customize its behavior.

.. note:: Do you really need a customized configuration?

    The debug toolbar ships with a default configuration that is considered
    sane for the vast majority of Django projects. Don't copy-paste blindly
    the default values shown below into your settings module! It's useless and
    it'll prevent you from taking advantage of better defaults that may be
    introduced in future releases.

DEBUG_TOOLBAR_PANELS
--------------------

This setting specifies the full Python path to each panel that you want
included in the toolbar. It works like Django's ``MIDDLEWARE`` setting. The
default value is::

    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.history.HistoryPanel',
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
    ]

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

* ``DISABLE_PANELS``

  Default: ``{'debug_toolbar.panels.redirects.RedirectsPanel'}``

  This setting is a set of the full Python paths to each panel that you
  want disabled (but still displayed) by default.

* ``INSERT_BEFORE``

  Default: ``'</body>'``

  The toolbar searches for this string in the HTML and inserts itself just
  before.

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

* ``RESULTS_CACHE_SIZE``

  Default: ``25``

  The toolbar keeps up to this many results in memory.

* ``ROOT_TAG_EXTRA_ATTRS``

  Default: ``''``

  This setting is injected in the root template div in order to avoid
  conflicts with client-side frameworks. For example, when using the debug
  toolbar with Angular.js, set this to ``'ng-non-bindable'`` or
  ``'class="ng-non-bindable"'``.

* ``SHOW_COLLAPSED``

  Default: ``False``

  If changed to ``True``, the toolbar will be collapsed by default.

.. _SHOW_TOOLBAR_CALLBACK:

* ``SHOW_TOOLBAR_CALLBACK``

  Default: ``'debug_toolbar.middleware.show_toolbar'``

  This is the dotted path to a function used for determining whether the
  toolbar should show or not. The default checks are that ``DEBUG`` must be set
  to ``True`` and the IP of the request must be in ``INTERNAL_IPS``. You can
  provide your own function ``callback(request)`` which returns ``True`` or
  ``False``.

  For versions < 1.8, the callback should also return ``False`` for AJAX
  requests. Since version 1.8, AJAX requests are checked in the middleware, not
  the callback. This allows reusing the callback to verify access to panel
  views requested via AJAX.

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

* ``ENABLE_STACKTRACES_LOCALS``

  Default: ``False``

  Panels: cache, SQL

  If set to ``True``, this will show locals() for each stacktrace piece of
  code for SQL queries and cache calls.
  Enabling stacktraces locals will increase the CPU time used when executing
  queries and will give too verbose information in most cases, but is useful
  for debugging complex cases.

.. caution::
   This will expose all members from each frame of the stacktrace. This can
   potentially expose sensitive or private information. It's advised to only
   use this configuration locally.

* ``HIDE_IN_STACKTRACES``

  Default::

    (
        "socketserver",
        "threading",
        "wsgiref",
        "debug_toolbar",
        "django.db",
        "django.core.handlers",
        "django.core.servers",
        "django.utils.decorators",
        "django.utils.deprecation",
        "django.utils.functional",
    )


  Panels: cache, SQL

  Useful for eliminating server-related entries which can result
  in enormous DOM structures and toolbar rendering delays.

* ``PRETTIFY_SQL``

  Default: ``True``

  Panel: SQL

  Controls SQL token grouping.

  Token grouping allows pretty print of similar tokens,
  like aligned indentation for every selected field.

  When set to ``True``, it might cause render slowdowns
  when a view make long SQL textual queries.

  **Without grouping**::

    SELECT "auth_user"."id", "auth_user"."password", "auth_user"."last_login", "auth_user"."is_superuser", "auth_user"."username", "auth_user"."first_name", "auth_user"."last_name"
    FROM "auth_user"
    WHERE "auth_user"."username" = '''test_username'''
    LIMIT 21

  **With grouping**::

    SELECT "auth_user"."id",
       "auth_user"."password",
       "auth_user"."last_login",
       "auth_user"."is_superuser",
       "auth_user"."username",
       "auth_user"."first_name",
       "auth_user"."last_name",
      FROM "auth_user"
    WHERE "auth_user"."username" = '''test_username'''
    LIMIT 21

* ``PROFILER_MAX_DEPTH``

  Default: ``10``

  Panel: profiling

  This setting affects the depth of function calls in the profiler's
  analysis.

* ``SHOW_TEMPLATE_CONTEXT``

  Default: ``True``

  Panel: templates

  If set to ``True`` then a template's context will be included with it in the
  template debug panel. Turning this off is useful when you have large
  template contexts, or you have template contexts with lazy data structures
  that you don't want to be evaluated.

* ``SKIP_TEMPLATE_PREFIXES``

  Default: ``('django/forms/widgets/', 'admin/widgets/')``

  Panel: templates.

  Templates starting with those strings are skipped when collecting
  rendered templates and contexts. Template-based form widgets are
  skipped by default because the panel HTML can easily grow to hundreds
  of megabytes with many form fields and many options.

* ``SQL_WARNING_THRESHOLD``

  Default: ``500``

  Panel: SQL

  The SQL panel highlights queries that took more that this amount of time,
  in milliseconds, to execute.

Here's what a slightly customized toolbar configuration might look like::

    # This example is unlikely to be appropriate for your project.
    DEBUG_TOOLBAR_CONFIG = {
        # Toolbar options
        'RESULTS_CACHE_SIZE': 3,
        'SHOW_COLLAPSED': True,
        # Panel options
        'SQL_WARNING_THRESHOLD': 100,   # milliseconds
    }
