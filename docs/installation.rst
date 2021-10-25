Installation
============

Each of the following steps needs to be configured for the Debug Toolbar to be
fully functional.

Getting the code
----------------

The recommended way to install the Debug Toolbar is via pip_::

    $ python -m pip install django-debug-toolbar

If you aren't familiar with pip, you may also obtain a copy of the
``debug_toolbar`` directory and add it to your Python path.

.. _pip: https://pip.pypa.io/

To test an upcoming release, you can install the in-development version
instead with the following command::

     $ python -m pip install -e git+https://github.com/jazzband/django-debug-toolbar.git#egg=django-debug-toolbar

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

Make sure your ``TEMPLATES`` setting contains a ``DjangoTemplates`` backend
whose ``APP_DIRS`` options is set to ``True``. It's in there by default, so
you'll only need to change this if you've changed that setting.


If you're upgrading from a previous version, you should review the
:doc:`change log <changes>` and look for specific upgrade instructions.

Setting up URLconf
------------------

Add the Debug Toolbar's URLs to your project's URLconf::

    import debug_toolbar
    from django.conf import settings
    from django.urls import include, path

    urlpatterns = [
        ...
        path('__debug__/', include(debug_toolbar.urls)),
    ]

This example uses the ``__debug__`` prefix, but you can use any prefix that
doesn't clash with your application's URLs. Note the lack of quotes around
``debug_toolbar.urls``.

Enabling middleware
-------------------

The Debug Toolbar is mostly implemented in a middleware. Enable it in your
settings module as follows::

    MIDDLEWARE = [
        # ...
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        # ...
    ]

.. warning::

    The order of ``MIDDLEWARE`` is important. You should include the Debug
    Toolbar middleware as early as possible in the list. However, it must come
    after any other middleware that encodes the response's content, such as
    :class:`~django.middleware.gzip.GZipMiddleware`.

.. _internal-ips:

Configuring Internal IPs
------------------------

The Debug Toolbar is shown only if your IP address is listed in the
:setting:`INTERNAL_IPS` setting.  This means that for local
development, you *must* add ``'127.0.0.1'`` to :setting:`INTERNAL_IPS`;
you'll need to create this setting if it doesn't already exist in your
settings module::

   INTERNAL_IPS = [
       # ...
       '127.0.0.1',
       # ...
   ]

You can change the logic of determining whether or not the Debug Toolbar
should be shown with the :ref:`SHOW_TOOLBAR_CALLBACK <SHOW_TOOLBAR_CALLBACK>`
option.  This option allows you to specify a custom function for this purpose.

.. warning::

    If using Docker the following will set your `INTERNAL_IPS` correctly only if you are in Debug mode.::
    
        if DEBUG:
            import os  # only if you haven't already imported this
            import socket  # only if you haven't already imported this
            hostname, _, ips = socker.gethostbyname_ex(socket.gethostname())
            INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + ['127.0.0.1', '10.0.2.2']
            
           
Troubleshooting
---------------

On some platforms, the Django ``runserver`` command may use incorrect content
types for static assets. To guess content types, Django relies on the
:mod:`mimetypes` module from the Python standard library, which itself relies
on the underlying platform's map files. If you find improper content types for
certain files, it is most likely that the platform's map files are incorrect or
need to be updated. This can be achieved, for example, by installing or
updating the ``mailcap`` package on a Red Hat distribution, ``mime-support`` on
a Debian distribution, or by editing the keys under ``HKEY_CLASSES_ROOT`` in
the Windows registry.

Cross-Origin Request Blocked
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Debug Toolbar loads a `JavaScript module`_. Typical local development using
Django ``runserver`` is not impacted. However, if your application server and
static files server are at different origins, you may see `CORS errors`_ in
your browser's development console:

.. code-block:: text

    Cross-Origin Request Blocked: The Same Origin Policy disallows reading the remote resource at http://localhost/static/debug_toolbar/js/toolbar.js. (Reason: CORS header ‘Access-Control-Allow-Origin’ missing).

Or

.. code-block:: text

    Access to script at 'http://localhost/static/debug_toolbar/js/toolbar.js' from origin 'http://localhost:8000' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.

To resolve, configure your static files server to add the
`Access-Control-Allow-Origin header`_ with the origin of the application
server. For example, if your application server is at ``http://example.com``,
and your static files are served by NGINX, add:

.. code-block:: nginx

    add_header Access-Control-Allow-Origin http://example.com;

And for Apache:

.. code-block:: apache

    Header add Access-Control-Allow-Origin http://example.com

.. _JavaScript module: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules
.. _CORS errors: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS/Errors/CORSMissingAllowOrigin
.. _Access-Control-Allow-Origin header: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Origin

Django Channels & Async
^^^^^^^^^^^^^^^^^^^^^^^

The Debug Toolbar currently doesn't support Django Channels or async projects.
If you are using Django channels are having issues getting panels to load,
please review the documentation for the configuration option
:ref:`RENDER_PANELS <RENDER_PANELS>`.
