from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='debug_toolbar',
      version=version,
      description="A configurable set of panels that display various debug information about the current request/response.",
      long_description=open("README.rst").read(),
      # Get more strings from http://www.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Framework :: Django",
        ],
      keywords='',
      author='Rob Hudson',
      author_email='rob@cogit8.com',
      url='http://rob.cogit8.org/blog/2008/Sep/19/introducing-django-debug-toolbar/',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      """,
      )
