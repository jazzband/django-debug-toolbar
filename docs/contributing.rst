Contributing
============

Bug reports and feature requests
--------------------------------

You can report bugs and request features in the `bug tracker
<http://github.com/django-debug-toolbar/django-debug-toolbar/issues>`_.

Please search the existing database for duplicates before filing an issue.

Code
----

The code is available `on GitHub
<http://github.com/django-debug-toolbar/django-debug-toolbar>`_.

Once you've obtained a checkout, you should create a virtualenv_ and install
the libraries required for working on the Debug Toolbar::

    $ pip install -r requirements_dev.txt

.. _virtualenv: http://www.virtualenv.org/

Tests
-----

Once you've set up a development environment as explained above, you can run
the test suite::

    $ make test

You can also run the test suite on all supported versions of Django and
Python::

    $ tox

This is strongly recommended before committing changes to Python code.

At this time, there isn't an easy way to test against databases other than
SQLite. The JaveScript code isn't tested either.

Style
-----

Python code for the Django Debug Toolbar follows PEP8. Line length is limited
to 100 characters. You can check for style violations with::

    $ make flake8

Patches
-------

Please submit `pull requests
<http://github.com/django-debug-toolbar/django-debug-toolbar/pulls>`_!

The Debug Toolbar includes a limited but growing test suite. If you fix a bug
or add a feature code, please consider adding proper coverage in the test
suite, especially if it has a chance for a regression.

If you change a CSS or a JavaScript file, you should update both the original
file and the minified version in the same commit. Use ``make compress_css``
and ``make compress_js`` to minify files.

Translations
------------

Translation efforts are coordinated on `Transifex
<https://www.transifex.net/projects/p/django-debug-toolbar/>`_.

Help translate the Debug Toolbar in your language!

Prior to a release, the English ``.po`` file must be updated with ``make
translatable_strings``. Once translators have updated the translations on
Transifex, all ``.po`` files must be updated with ``make update_translations``.

Mailing list
------------

This project doesn't have a mailing list at this time. If you wish to discuss
a topic, please open an issue on GitHub.
