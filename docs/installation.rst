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

     $ pip install -e git+https://github.com/jazzband/django-debug-toolbar.git#egg=django-debug-toolbar

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

URLconf
-------

Add the Debug Toolbar's URLs to your project's URLconf as follows::

    from django.conf import settings
    from django.conf.urls import include, url

    if settings.DEBUG:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

This example uses the ``__debug__`` prefix, but you can use any prefix that
doesn't clash with your application's URLs. Note the lack of quotes around
``debug_toolbar.urls``.

Middleware
----------

The Debug Toolbar is mostly implemented in a middleware. Enable it in your
settings module as follows::

    MIDDLEWARE = [
        # ...
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        # ...
    ]

Old-style middleware::

    MIDDLEWARE_CLASSES = [
        # ...
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        # ...
    ]

.. warning::

    The order of ``MIDDLEWARE`` and ``MIDDLEWARE_CLASSES`` is important. You
    should include the Debug Toolbar middleware as early as possible in the
    list. However, it must come after any other middleware that encodes the
    response's content, such as
    :class:`~django.middleware.gzip.GZipMiddleware`.

Internal IPs
------------

The Debug Toolbar is shown only if your IP is listed in the ``INTERNAL_IPS``
setting. (You can change this logic with the ``SHOW_TOOLBAR_CALLBACK``
option.) For local development, you should add ``'127.0.0.1'`` to
``INTERNAL_IPS``.
