Change log
==========

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
* Various JavaScript improvements.

Deprecated features
~~~~~~~~~~~~~~~~~~~

* The `INTERCEPT_REDIRECT` setting is superseded by the more generic
  `DISABLE_PANELS`.

1.0
---

This is the first stable version of the Debug Toolbar!

It includes many new features and performance improvements as well a few
backwards-incompatible changes to make the toolbar easier to deploy, use,
extend and maintain in the future.

You're strongly encouraged to review the installation and configuration docs
and redo the setup in your projects.

Third-party panels will need to be updated to work with this version.
