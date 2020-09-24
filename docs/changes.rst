Change log
==========

3.2 (unreleased)
----------------

* Fixed a regression where the JavaScript code crashed with an invalid
  CSS selector when searching for an element to replace.


3.1 (2020-09-21)
----------------

* Fixed a crash in the history panel when sending an empty JSON POST
  request.
* Made ``make example`` also set up the database and a superuser
  account.
* Added a Makefile target for regenerating the django-debug-toolbar
  screenshot.
* Added automatic escaping of panel titles resp. disallowed HTML tags.
* Removed some CSS
* Restructured the SQL stats template.
* Changed command line examples to prefer ``python -m pip`` to ``pip``.


3.0 (2020-09-20)
----------------

* Added an ``.editorconfig`` file specifying indentation rules etc.
* Updated the italian translation.
* Added support for Django 3.1a1. ``fetch()`` and ``jQuery.ajax`` requests are
  now detected by the absence of a ``Accept: text/html`` header instead of the
  jQuery-specific ``X-Requested-With`` header on Django 3.1 or better.
* Pruned unused CSS and removed hacks for ancient browsers.
* Added the new :attr:`Panel.scripts <debug_toolbar.panels.Panel.scripts>`
  property. This property should return a list of JavaScript resources to be
  loaded in the browser when displaying the panel. Right now, this is used by a
  single panel, the Timer panel. Third party panels can use this property to
  add scripts rather then embedding them in the content HTML.
* Switched from JSHint to ESLint. Added an ESLint job to the Travis CI matrix.
* Debug toolbar state which is only needed in the JavaScript code now uses
  localStorage.
* Updated the code to avoid a few deprecation warnings and resource warnings.
* Started loading JavaScript as ES6 modules.
* Added support for ``cache.touch()`` when using django-debug-toolbar.
* Eliminated more inline CSS.
* Updated ``tox.ini`` and ``Makefile`` to use isort>=5.
* Increased RESULTS_CACHE_SIZE to 25 to better support AJAX requests.
* Fixed the close button CSS by explicitly specifying the
  ``box-sizing`` property.
* Simplified the ``isort`` configuration by taking advantage of isort's
  ``black`` profile.
* Added HistoryPanel including support for AJAX requests.

**Backwards incompatible changes**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Loading panel content no longer executes the scripts elements embedded in the
  HTML. Third party panels that require JavaScript resources should now use the
  :attr:`Panel.scripts <debug_toolbar.panels.Panel.scripts>` property.
* Removed support for end of life Django 1.11. The minimum supported Django is
  now 2.2.


2.2 (2020-01-31)
----------------

* Removed support for end of life Django 2.0 and 2.1.
* Added support for Python 3.8.
* Add locals() option for sql panel.
* Added support for Django 3.0.


2.1 (2019-11-12)
----------------

* Changed the Travis CI matrix to run style checks first.
* Exposed the ``djdt.init`` function too.
* Small improvements to the code to take advantage of newer Django APIs
  and avoid warnings because of deprecated code.
* Verified compatibility with the upcoming Django 3.0 (at the time of
  writing).


2.0 (2019-06-20)
----------------

* Updated ``StaticFilesPanel`` to be compatible with Django 3.0.
* The ``ProfilingPanel`` is now enabled but inactive by default.
* Fixed toggling of table rows in the profiling panel UI.
* The ``ProfilingPanel`` no longer skips remaining panels or middlewares.
* Improved the installation documentation.
* Fixed a possible crash in the template panel.
* Added support for psycopg2 ``Composed`` objects.
* Changed the Jinja2 tests to use Django's own Jinja2 template backend.
* Added instrumentation to queries using server side cursors.
* Too many small improvements and cleanups to list them all.

**Backwards incompatible changes**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Removed support for Python 2.
* Removed support for Django's deprecated ``MIDDLEWARE_CLASSES`` setting.
* Restructured ``Panel`` to execute more like the new-style Django MIDDLEWARE.
  The ``Panel.__init__()`` method is now passed ``get_response`` as the first
  positional argument. The ``Panel.process_request()`` method must now always
  return a response. Usually this is the response returned by
  ``get_response()`` but the panel may also return a different response as is
  the case in the ``RedirectsPanel``. Third party panels must adjust to this
  new architecture. ``Panel.process_response()`` and ``Panel.process_view()``
  have been removed as a result of this change.

The deprecated API, ``debug_toolbar.panels.DebugPanel``, has been removed.
Third party panels should use ``debug_toolbar.panels.Panel`` instead.

The following deprecated settings have been removed:

* ``HIDDEN_STACKTRACE_MODULES``
* ``HIDE_DJANGO_SQL``
* ``INTERCEPT_REDIRECTS``
* ``RESULTS_STORE_SIZE``
* ``ROOT_TAG_ATTRS``
* ``TAG``

1.11 (2018-12-03)
-----------------

* Use ``defer`` on all ``<script>`` tags to avoid blocking HTML parsing,
  removed inline JavaScript.
* Stop inlining images in CSS to avoid Content Security Policy errors
  altogether.
* Reformatted the code using `black <https://github.com/ambv/black>`__.
* Added the Django mail panel to the list of third-party panels.
* Convert system check errors to warnings to accommodate exotic
  configurations.
* Fixed a crash when explaining raw querysets.
* Fixed an obscure unicode error with binary data fields.
* Added MariaDB and Python 3.7 builds to the CI.

1.10.1 (2018-09-11)
-------------------

* Fixed a problem where the duplicate query detection breaks for
  non-hashable query parameters.
* Added support for structured types when recording SQL.
* Made Travis CI also run one test no PostgreSQL.
* Added fallbacks for inline images in CSS.
* Improved cross-browser compatibility around ``URLSearchParams`` usage.
* Fixed a few typos and redundancies in the documentation, removed
  mentions of django-debug-toolbar's jQuery which aren't accurate
  anymore.

1.10 (2018-09-06)
-----------------

* Removed support for Django < 1.11.
* Added support and testing for Django 2.1 and Python 3.7. No actual code
  changes were required.
* Removed the jQuery dependency. This means that django-debug-toolbar
  now requires modern browsers with support for ``fetch``, ``classList``
  etc. The ``JQUERY_URL`` setting is also removed because it isn't
  necessary anymore. If you depend on jQuery, integrate it yourself.
* Added support for the server timing header.
* Added a differentiation between similar and duplicate queries. Similar
  queries are what duplicate queries used to be (same SQL, different
  parameters).
* Stopped hiding frames from Django's contrib apps in stacktraces by
  default.
* Lots of small cleanups and bugfixes.

1.9.1 (2017-11-15)
------------------

* Fix erroneous ``ContentNotRenderedError`` raised by the redirects panel.

1.9 (2017-11-13)
----------------

This version is compatible with Django 2.0 and requires Django 1.8 or
later.

Bugfixes
~~~~~~~~

* The profiling panel now escapes reported data resulting in valid HTML.
* Many minor cleanups and bugfixes.

1.8 (2017-05-05)
----------------

This version is compatible with Django 1.11 and requires Django 1.8 or
later.

**Backwards incompatible changes**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``debug_toolbar.middleware.show_toolbar`` (the default value of setting
  ``SHOW_TOOLBAR_CALLBACK``) no longer returns ``False`` for AJAX requests.
  This is to allow reusing the ``SHOW_TOOLBAR_CALLBACK`` function to verify
  access to panel views requested via AJAX. Projects defining a custom
  ``SHOW_TOOLBAR_CALLBACK`` should remove checks for AJAX requests in order to
  continue to allow access to these panels.

Features
~~~~~~~~

* New decorator ``debug_toolbar.decorators.require_show_toolbar`` prevents
  unauthorized access to decorated views by checking ``SHOW_TOOLBAR_CALLBACK``
  every request. Unauthorized access results in a 404.
* The ``SKIP_TEMPLATE_PREFIXES`` setting allows skipping templates in
  the templates panel. Template-based form widgets' templates are
  skipped by default to avoid panel sizes going into hundreds of
  megabytes of HTML.

Bugfixes
~~~~~~~~

* All views are now decorated with
  ``debug_toolbar.decorators.require_show_toolbar`` preventing unauthorized
  access.
* The templates panel now reuses contexts' pretty printed version which
  makes the debug toolbar usable again with Django 1.11's template-based
  forms rendering.
* Long SQL statements are now forcibly wrapped to fit on the screen.

1.7 (2017-03-05)
----------------

Bugfixes
~~~~~~~~

* Recursive template extension is now understood.
* Deprecation warnings were fixed.
* The SQL panel uses HMAC instead of simple hashes to verify that SQL
  statements have not been changed. Also, the handling of bytes and text
  for hashing has been hardened. Also, a bug with Python's division
  handling has been fixed for improved Python 3 support.
* An error with django-jinja has been fixed.
* A few CSS classes have been prefixed with ``djdt-`` to avoid
  conflicting class names.

1.6 (2016-10-05)
----------------

The debug toolbar was adopted by jazzband.

Removed features
~~~~~~~~~~~~~~~~

* Support for automatic setup has been removed as it was frequently
  problematic. Installation now requires explicit setup. The
  ``DEBUG_TOOLBAR_PATCH_SETTINGS`` setting has also been removed as it is now
  unused. See the :doc:`installation documentation <installation>` for details.

Bugfixes
~~~~~~~~

* The ``DebugToolbarMiddleware`` now also supports Django 1.10's ``MIDDLEWARE``
  setting.

1.5 (2016-07-21)
----------------

This version is compatible with Django 1.10 and requires Django 1.8 or later.

Support for Python 3.2 is dropped.

Bugfixes
~~~~~~~~

* Restore compatibility with sqlparse ≥ 0.2.0.
* Add compatibility with Bootstrap 4, Pure CSS, MDL, etc.
* Improve compatibility with RequireJS / AMD.
* Improve the UI slightly.
* Fix invalid (X)HTML.

1.4 (2015-10-06)
----------------

This version is compatible with Django 1.9 and requires Django 1.7 or later.

New features
~~~~~~~~~~~~

* New panel method :meth:`debug_toolbar.panels.Panel.generate_stats` allows panels
  to only record stats when the toolbar is going to be inserted into the
  response.

Bugfixes
~~~~~~~~

* Response time for requests of projects with numerous media files has
  been improved.

1.3 (2015-03-10)
----------------

This is the first version compatible with Django 1.8.

New features
~~~~~~~~~~~~

* A new panel is available: Template Profiler.
* The ``SHOW_TOOLBAR_CALLBACK`` accepts a callable.
* The toolbar now provides a :ref:`javascript-api`.

Bugfixes
~~~~~~~~

* The toolbar handle cannot leave the visible area anymore when the toolbar is
  collapsed.
* The root level logger is preserved.
* The ``RESULTS_CACHE_SIZE`` setting is taken into account.
* CSS classes are prefixed with ``djdt-`` to prevent name conflicts.
* The private copy of jQuery no longer registers as an AMD module on sites
  that load RequireJS.

1.2 (2014-04-25)
----------------

New features
~~~~~~~~~~~~

* The ``JQUERY_URL`` setting defines where the toolbar loads jQuery from.

Bugfixes
~~~~~~~~

* The toolbar now always loads a private copy of jQuery in order to avoid
  using an incompatible version. It no longer attemps to integrate with AMD.

  This private copy is available in ``djdt.jQuery``. Third-party panels are
  encouraged to use it because it should be as stable as the toolbar itself.

1.1 (2014-04-12)
----------------

This is the first version compatible with Django 1.7.

New features
~~~~~~~~~~~~

* The SQL panel colors queries depending on the stack level.
* The Profiler panel allows configuring the maximum depth.

Bugfixes
~~~~~~~~

* Support languages where lowercase and uppercase strings may have different
  lengths.
* Allow using cursor as context managers.
* Make the SQL explain more helpful on SQLite.
* Various JavaScript improvements.

Deprecated features
~~~~~~~~~~~~~~~~~~~

* The ``INTERCEPT_REDIRECTS`` setting is superseded by the more generic
  ``DISABLE_PANELS``.

1.0 (2013-12-21)
----------------

This is the first stable version of the Debug Toolbar!

It includes many new features and performance improvements as well a few
backwards-incompatible changes to make the toolbar easier to deploy, use,
extend and maintain in the future.

You're strongly encouraged to review the installation and configuration docs
and redo the setup in your projects.

Third-party panels will need to be updated to work with this version.
