import os
from setuptools import setup, find_packages

version = '0.1'

setup(
    name='debug_toolbar',
    version=version,
    description='A configurable set of panels that display various debug information about the current request/response.',
    long_description=open('README.rst').read(),
    # Get more strings from http://www.python.org/pypi?:action=list_classifiers
    author='Rob Hudson',
    author_email='rob@cogit8.org',
    url='http://rob.cogit8.org/blog/2008/Sep/19/introducing-django-debug-toolbar/',
    download_url='http://github.com/robhudson/django-debug-toolbar/tree/master',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
