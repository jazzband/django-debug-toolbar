Installation
============

Getting the code
----------------

The recommended way to install the Debug Toolbar is via pip_::

    $ pip install django-debug-toolbar

If you aren't familiar with pip, you may also obtain a copy of the
``debug_toolbar`` directory and add it to your Python path.

.. _pip: https://pip.pypa.io/

To test an upcoming release, you can install the in-development version
instead with the following command::

     $ pip install -e git+https://github.com/django-debug-toolbar/django-debug-toolbar.git#egg=django-debug-toolbar

Prerequisites
-------------

Make sure that ``'django.contrib.staticfiles'`` is `set up properly
<https://docs.djangoproject.com/en/stable/howto/static-files/>`_ and add
``'debug_toolbar'`` to your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = [
        # ...
        'django.contrib.staticfiles',
        # ...
        'debug_toolbar',
    ]

    STATIC_URL = '/static/'

If you're upgrading from a previous version, you should review the
:doc:`change log <changes>` and look for specific upgrade instructions.

Automatic setup
---------------

If you just add the Debug Toolbar to the ``INSTALLED_APPS`` setting as shown
above, when the ``DEBUG`` setting is ``True``, the Debug Toolbar will attempt
to patch your settings to configure itself automatically.

.. warning::

    The automatic setup is known to interfere with the start-up sequence of
    some projects and to prevent them from loading or functioning properly.

    **The explicit setup described below is recommended for all but the most
    trivial projects. The automatic setup is kept for backwards-compatibility.**

.. note::

    The automatic setup imports your project's URLconf in order to add the
    Debug Toolbar's URLs. This is likely to trigger circular imports, for
    instance when the URLconf imports views that import models, a pattern
    found in almost every Django project.

    If the development server crashes with a long stack trace after hitting an
    :exc:`ImportError`, an :exc:`~django.apps.exceptions.AppRegistryNotReady`
    or an :exc:`~django.core.exceptions.ImproperlyConfigured` exception, use
    the explicit setup described below.

    When the automatic setup is used, the Debug Toolbar is not compatible with
    :class:`~django.middleware.gzip.GZipMiddleware`. Please disable that
    middleware during development or use the explicit setup to allow the
    toolbar to function properly.

Explicit setup
--------------

This is the recommended way to configure the Debug Toolbar. First, disable the
automatic setup by adding this line in your settings module::

    DEBUG_TOOLBAR_PATCH_SETTINGS = False

URLconf
~~~~~~~

Add the Debug Toolbar's URLs to your project's URLconf as follows::

    from django.conf import settings
    from django.conf.urls import include, patterns, url

    if settings.DEBUG:
        import debug_toolbar
        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]

This example uses the ``__debug__`` prefix, but you can use any prefix that
doesn't clash with your application's URLs. Note the lack of quotes around
``debug_toolbar.urls``.

.. note::

    The automatic setup appends the Debug Toolbar URLs to the root URLconf.

Middleware
~~~~~~~~~~

The Debug Toolbar is mostly implemented in a middleware. Enable it in your
settings module as follows::

    MIDDLEWARE_CLASSES = [
        # ...
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        # ...
    ]

The order of ``MIDDLEWARE_CLASSES`` is important. You should include the Debug
Toolbar middleware as early as possible in the list. However, it must come
after any other middleware that encodes the response's content, such as
:class:`~django.middleware.gzip.GZipMiddleware`.

.. note::

    The automatic setup inserts the Debug Toolbar middleware at the beginning
    of ``MIDDLEWARE_CLASSES``, unless it's already included.

Internal IPs
~~~~~~~~~~~~

The Debug Toolbar is shown only if your IP is listed in the ``INTERNAL_IPS``
setting. (You can change this logic with the ``SHOW_TOOLBAR_CALLBACK``
option.) For local development, you should add ``'127.0.0.1'`` to
``INTERNAL_IPS``.

.. note::

    The automatic setup sets ``INTERNAL_IPS`` to ``'127.0.0.1'`` and
    ``'::1'``, unless it's already set to a non-empty value.
