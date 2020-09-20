README
======

About
-----

This sample project demonstrates how to use the debug toolbar. It is designed
to run under the latest stable version of Django.

It also provides a few test pages to ensure the debug toolbar doesn't
interfere with common JavaScript frameworks.

How to
------

The test project requires a working installation of Django::

    $ python -m pip install Django

The following commands must be run from the root directory of a checkout of
the debug toolbar, ie. the directory that contains ``example/``.

Before running the example for the first time, you must create a database::

    $ python -m django migrate --settings=example.settings

Then you can use the following command to run the example::

    $ python -m django runserver --settings=example.settings

You can change the database used by specifying the ``DJANGO_DATABASE_ENGINE``
environment variable::

    $ DJANGO_DATABASE_ENGINE=postgresql python -m django migrate --settings=example.settings
    $ DJANGO_DATABASE_ENGINE=postgresql python -m django runserver --settings=example.settings

