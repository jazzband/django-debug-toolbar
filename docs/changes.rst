Change log
==========

1.4
---

This version is compatible with the upcoming Django 1.9 release. It requires
Django 1.7 or later.

New features
~~~~~~~~~~~~

* New panel method :meth:`debug_toolbar.panels.Panel.generate_stats` allows panels
  to only record stats when the toolbar is going to be inserted into the
  response.

Bugfixes
~~~~~~~~

* Response time for requests of projects with numerous media files has
  been improved.

1.3
---

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

1.2
---

New features
~~~~~~~~~~~~

* The ``JQUERY_URL`` setting defines where the toolbar loads jQuery from.

Bugfixes
~~~~~~~~

* The toolbar now always loads a private copy of jQuery in order to avoid
  using an incompatible version. It no longer attemps to integrate with AMD.

  This private copy is available in ``djdt.jQuery``. Third-party panels are
  encouraged to use it because it should be as stable as the toolbar itself.

1.1
---

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

1.0
---

This is the first stable version of the Debug Toolbar!

It includes many new features and performance improvements as well a few
backwards-incompatible changes to make the toolbar easier to deploy, use,
extend and maintain in the future.

You're strongly encouraged to review the installation and configuration docs
and redo the setup in your projects.

Third-party panels will need to be updated to work with this version.
