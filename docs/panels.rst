Panels
======

The Django Debug Toolbar ships with a series of built-in panels. In addition,
several third-party panels are available.

Default built-in panels
-----------------------

The following panels are enabled by default.

Version
~~~~~~~

Path: ``debug_toolbar.panels.version.VersionDebugPanel``

Django version.

Timer
~~~~~

Path: ``debug_toolbar.panels.timer.TimerDebugPanel``

Request timer.

Settings
~~~~~~~~

Path: ``debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel``

A list of settings in settings.py.

Header
~~~~~~

Path: ``debug_toolbar.panels.headers.HeaderDebugPanel``

Common HTTP headers.

Request
~~~~~~~

Path: ``debug_toolbar.panels.request_vars.RequestVarsDebugPanel``

GET/POST/cookie/session variable display.

SQL
~~~

Path: ``debug_toolbar.panels.sql.SQLDebugPanel``

SQL queries including time to execute and links to EXPLAIN each query.

Template
~~~~~~~~

Path: ``debug_toolbar.panels.template.TemplateDebugPanel``

Templates and context used, and their template paths.

Cache
~~~~~

Path: ``debug_toolbar.panels.cache.CacheDebugPanel``

Cache queries.

Signal
~~~~~~

Path: ``debug_toolbar.panels.signals.SignalDebugPanel``

List of signals, their args and receivers.

Logging
~~~~~~~

Path: ``debug_toolbar.panels.logger.LoggingPanel``

Logging output via Python's built-in :mod:`logging`, or via the `logbook <http://logbook.pocoo.org>`_ module.

Non-default built-in panels
---------------------------

The following panels are disabled by default. You must add them to the
``DEBUG_TOOLBAR_PANELS`` setting to enable them.

Profiling
~~~~~~~~~

Path: ``debug_toolbar.panels.profiling.ProfilingDebugPanel``

Profiling information for the view function.

Third-party panels
------------------

.. note:: Third-party panels aren't officially supported!

    The authors of the Django Debug Toolbar maintain a list of third-party
    panels, but they can't vouch for the quality of each of them. Please
    report bugs to their authors.

If you'd like to add a panel to this list, please submit a pull request!

Haystack
~~~~~~~~

URL: https://github.com/streeter/django-haystack-panel

Path: ``haystack_panel.panel.HaystackDebugPanel``

See queries made by your Haystack_ backends.

.. _Haystack: http://haystacksearch.org/

HTML Tidy/Validator
~~~~~~~~~~~~~~~~~~~

URL: https://github.com/joymax/django-dtpanel-htmltidy

Path: ``debug_toolbar_htmltidy.panels.HTMLTidyDebugPanel``

HTML Tidy or HTML Validator is a custom panel that validates your HTML and
displays warnings and errors.

Inspector
~~~~~~~~~

URL: https://github.com/santiagobasulto/debug-inspector-panel

Path: ``inspector_panel.panels.inspector.InspectorPanel``

Retrieves and displays information you specify using the ``debug`` statement.
Inspector panel also logs to the console by default, but may be instructed not
to.

Memcache
~~~~~~~~

URL: https://github.com/ross/memcache-debug-panel

Path: ``memcache_toolbar.panels.memcache.MemcachePanel`` or ``memcache_toolbar.panels.pylibmc.PylibmcPanel``

This panel tracks memcached usage. It currently supports both the pylibmc and
memcache libraries.

MongoDB
~~~~~~~

URL: https://github.com/hmarr/django-debug-toolbar-mongo

Path: ``debug_toolbar_mongo.panel.MongoDebugPanel``

Adds MongoDB debugging information.

Neo4j
~~~~~

URL: https://github.com/robinedwards/django-debug-toolbar-neo4j-panel

Path: ``neo4j_panel.Neo4jPanel``

Trace neo4j rest API calls in your django application, this also works for neo4django and neo4jrestclient, support for py2neo is on its way.

Sites
~~~~~

URL: https://github.com/elvard/django-sites-toolbar

Path: ``sites_toolbar.panels.SitesDebugPanel``

Browse Sites registered in ``django.contrib.sites`` and switch between them.
Useful to debug project when you use `django-dynamicsites
<https://bitbucket.org/uysrc/django-dynamicsites/src>`_ which sets SITE_ID
dynamically.

Template Timings
~~~~~~~~~~~~~~~~

URL: https://github.com/orf/django-debug-toolbar-template-timings

Path: ``template_timings_panel.panels.TemplateTimings.TemplateTimings``

Displays template rendering times for your Django application.

User
~~~~

URL: https://github.com/playfire/django-debug-toolbar-user-panel

Path: ``debug_toolbar_user_panel.panels.UserPanel``

Easily switch between logged in users, see properties of current user.
