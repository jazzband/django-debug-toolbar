Change log
==========

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
