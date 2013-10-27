Installation
============

#. The recommended way to install the Debug Toolbar is via pip_::

       $ pip install django-debug-toolbar

   If you aren't familiar with pip, you may also obtain a copy of the
   ``debug_toolbar`` directory and add it to your Python path.

   .. _pip: http://www.pip-installer.org/


   To test an upcoming release, you can install the `in-development version
   <http://github.com/django-debug-toolbar/django-debug-toolbar/tarball/master#egg=django-debug-toolbar-dev>`_
   instead with the following command::

        $ pip install django-debug-toolbar==dev

#. Add the following middleware to your project's ``settings.py`` file::

       MIDDLEWARE_CLASSES = (
           # ...
           'debug_toolbar.middleware.DebugToolbarMiddleware',
           # ...
       )

   Tying into middleware allows each panel to be instantiated on request and
   rendering to happen on response.

   The order of ``MIDDLEWARE_CLASSES`` is important: the Debug Toolbar
   middleware must come after any other middleware that encodes the
   response's content (such as GZipMiddleware).

   .. note::

      The debug toolbar will only display itself if the mimetype of the
      response is either ``text/html`` or ``application/xhtml+xml`` and
      contains a closing ``</body>`` tag.

   .. note ::

      Be aware of middleware ordering and other middleware that may intercept
      requests and return responses. Putting the debug toolbar middleware
      *after* the Flatpage middleware, for example, means the toolbar will not
      show up on flatpages.

#. Make sure your IP is listed in the ``INTERNAL_IPS`` setting. If you are
   working locally this will be::

       INTERNAL_IPS = ('127.0.0.1',)

   .. note::

      This is required because of the built-in requirements of the
      ``show_toolbar`` method. See below for how to define a method to
      determine your own logic for displaying the toolbar.

#. Add ``debug_toolbar`` to your ``INSTALLED_APPS`` setting so Django can
   find the template files associated with the Debug Toolbar::

       INSTALLED_APPS = (
           # ...
           'debug_toolbar',
       )
