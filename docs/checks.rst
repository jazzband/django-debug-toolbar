=============
System checks
=============

The following :doc:`system checks <topics/checks>` help verify the Django
Debug Toolbar setup and configuration:

* **debug_toolbar.W001**: ``debug_toolbar.middleware.DebugToolbarMiddleware``
  is missing from ``MIDDLEWARE``.
* **debug_toolbar.W002**: ``debug_toolbar.middleware.DebugToolbarMiddleware``
  occurs multiple times in ``MIDDLEWARE``.
* **debug_toolbar.W003**: ``debug_toolbar.middleware.DebugToolbarMiddleware``
  occurs before ``django.middleware.gzip.GZipMiddleware`` in ``MIDDLEWARE``.
* **debug_toolbar.W004**: ``debug_toolbar`` is incompatible with
  ``MIDDLEWARE_CLASSES`` setting.
* **debug_toolbar.W005**: Setting ``DEBUG_TOOLBAR_PANELS`` is empty.
* **debug_toolbar.W006**: ``django.contrib.postgres`` occurs after
  ``debug_toolbar`` in ``INSTALLED_APPS``.
