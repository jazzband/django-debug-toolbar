#!/usr/bin/env python

from io import open

from setuptools import find_packages, setup


def readall(path):
    with open(path, encoding="utf-8") as fp:
        return fp.read()


setup(
    name="django-debug-toolbar",
    version="1.11.1",
    description="A configurable set of panels that display various debug "
    "information about the current request/response.",
    long_description=readall("README.rst"),
    author="Rob Hudson",
    author_email="rob@cogit8.org",
    url="https://github.com/jazzband/django-debug-toolbar",
    download_url="https://pypi.org/project/django-debug-toolbar/",
    license="BSD",
    packages=find_packages(exclude=("tests.*", "tests", "example")),
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=["Django>=1.11", "sqlparse>=0.2.0"],
    include_package_data=True,
    zip_safe=False,  # because we're including static files
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
