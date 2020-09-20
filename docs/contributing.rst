Contributing
============

.. image:: https://jazzband.co/static/img/jazzband.svg
   :target: https://jazzband.co/
   :alt: Jazzband

This is a `Jazzband <https://jazzband.co>`_ project. By contributing you agree
to abide by the `Contributor Code of Conduct <https://jazzband.co/about/conduct>`_
and follow the `guidelines <https://jazzband.co/about/guidelines>`_.

Bug reports and feature requests
--------------------------------

You can report bugs and request features in the `bug tracker
<https://github.com/jazzband/django-debug-toolbar/issues>`_.

Please search the existing database for duplicates before filing an issue.

Code
----

The code is available `on GitHub
<https://github.com/jazzband/django-debug-toolbar>`_. Unfortunately, the
repository contains old and flawed objects, so if you have set
`fetch.fsckObjects
<https://github.com/git/git/blob/0afbf6caa5b16dcfa3074982e5b48e27d452dbbb/Documentation/config.txt#L1381>`_
you'll have to deactivate it for this repository::

    git clone --config fetch.fsckobjects=false https://github.com/jazzband/django-debug-toolbar.git

Once you've obtained a checkout, you should create a virtualenv_ and install
the libraries required for working on the Debug Toolbar::

    $ pip install -r requirements_dev.txt

.. _virtualenv: https://virtualenv.pypa.io/

You can run now run the example application::

    $ DJANGO_SETTINGS_MODULE=example.settings python -m django migrate
    $ DJANGO_SETTINGS_MODULE=example.settings python -m django runserver

For convenience, there's an alias for the second command::

    $ make example

Look at ``example/settings.py`` for running the example with another database
than SQLite.

Tests
-----

Once you've set up a development environment as explained above, you can run
the test suite for the versions of Django and Python installed in that
environment::

    $ make test

You can enable coverage measurement during tests::

    $ make coverage

You can also run the test suite on all supported versions of Django and
Python::

    $ tox

This is strongly recommended before committing changes to Python code.

The test suite includes frontend tests written with Selenium. Since they're
annoyingly slow, they're disabled by default. You can run them as follows::

    $ make test_selenium

or by setting the ``DJANGO_SELENIUM_TESTS`` environment variable::

    $ DJANGO_SELENIUM_TESTS=true make test
    $ DJANGO_SELENIUM_TESTS=true make coverage
    $ DJANGO_SELENIUM_TESTS=true tox

At this time, there isn't an easy way to test against databases other than
SQLite.

Style
-----

The Django Debug Toolbar uses `black <https://github.com/psf/black>`__ to
format code and additionally uses flake8 and isort. You can reformat the code
using::

    $ make style

Patches
-------

Please submit `pull requests
<https://github.com/jazzband/django-debug-toolbar/pulls>`_!

The Debug Toolbar includes a limited but growing test suite. If you fix a bug
or add a feature code, please consider adding proper coverage in the test
suite, especially if it has a chance for a regression.

Translations
------------

Translation efforts are coordinated on `Transifex
<https://www.transifex.net/projects/p/django-debug-toolbar/>`_.

Help translate the Debug Toolbar in your language!

Mailing list
------------

This project doesn't have a mailing list at this time. If you wish to discuss
a topic, please open an issue on GitHub.

Making a release
----------------

Prior to a release, the English ``.po`` file must be updated with ``make
translatable_strings`` and pushed to Transifex. Once translators have done
their job, ``.po`` files must be downloaded with ``make update_translations``.

The release itself requires the following steps:

#. Update supported Python and Django versions:

   - ``setup.py`` ``python_requires`` list
   - ``setup.py`` trove classifiers
   - ``README.rst``

   Commit.

#. Update the screenshot in ``README.rst``.

   .. code-block:: console

       $ make example/django-debug-toolbar.png

   Commit.

#. Bump version numbers in ``docs/changes.rst``, ``docs/conf.py``,
   ``README.rst`` and ``setup.py``. Add the release date to
   ``docs/changes.rst``. Commit.

#. Tag the new version.

#. ``python setup.py sdist bdist_wheel upload``.

#. Push the commit and the tag.

#. Change the default version of the docs to point to the latest release:
   https://readthedocs.org/dashboard/django-debug-toolbar/versions/
