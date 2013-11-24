Installation
============

Getting the code
----------------

The recommended way to install the Debug Toolbar is via pip_::

    $ pip install django-debug-toolbar

If you aren't familiar with pip, you may also obtain a copy of the
``debug_toolbar`` directory and add it to your Python path.

.. _pip: http://www.pip-installer.org/

To test an upcoming release, you can install the `in-development version
<http://github.com/django-debug-toolbar/django-debug-toolbar/tarball/master#egg=django-debug-toolbar-dev>`_
instead with the following command::

     $ pip install django-debug-toolbar==dev

Quick setup
-----------

Make sure that ``'django.contrib.staticfiles'`` is set up properly and add
``'debug_toolbar'`` to your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        # ...
        'django.contrib.staticfiles',
        # ...
        'debug_toolbar',
    )

    STATIC_URL = '/static/'

For a simple Django project, that's all you need!

The Debug Toolbar will automatically adjust a few settings when you start the
development server. This happens only when the ``DEBUG`` setting is ``True``.

If you're upgrading from a previous version, you should review the
:doc:`change log <changes>` and look for specific upgrade instructions.

If the automatic setup doesn't work for your project, if you want to learn
what it does, or if you prefer defining your settings explicitly, read below.

.. note::

    The automatic setup relies on ``debug_toolbar.models`` being imported when
    the server starts. Django doesn't provide a better hook to execute code
    during the start-up sequence. This works with ``manage.py runserver``
    because it validates models before serving requests.

Explicit setup
--------------

URLconf
~~~~~~~

Add the Debug Toolbar's URLs to your project's URLconf as follows::

    from django.conf import settings
    from django.conf.urls import include, patterns, url

    if settings.DEBUG:
        import debug_toolbar
        urlpatterns += patterns('',
            url(r'^__debug__/', include(debug_toolbar.urls)),
        )

This example uses the ``__debug__`` prefix, but you can use any prefix that
doesn't clash with your application's URLs. Note the lack of quotes around
``debug_toolbar.urls``.

If the URLs aren't included in your root URLconf, the Debug Toolbar
automatically appends them.

Middleware
~~~~~~~~~~

The Debug Toolbar is mostly implemented in a middleware. Enable it in your
settings module as follows::

    MIDDLEWARE_CLASSES = (
        # ...
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        # ...
    )

The order of ``MIDDLEWARE_CLASSES`` is important. You should include the Debug
Toolbar middleware as early as possible in the list. However, it must come
after any other middleware that encodes the response's content, such as
``GZipMiddleware``.

If ``MIDDLEWARE_CLASSES`` doesn't contain the middleware, the Debug Toolbar
automatically adds it the beginning of the list.

Internal IPs
~~~~~~~~~~~~

The Debug Toolbar is shown only if your IP is listed in the ``INTERNAL_IPS``
setting. (You can change this logic with the ``SHOW_TOOLBAR_CALLBACK``
option.) For local development, you should add ``'127.0.0.1'`` to
``INTERNAL_IPS``.

If ``INTERNAL_IPS`` is empty, the Debug Toolbar automatically sets it to
``'127.0.0.1'`` and ``'::1'``.
