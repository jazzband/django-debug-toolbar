#!/usr/bin/env python3

import sys

from setuptools import setup

sys.stderr.write(
    """\
===============================
Unsupported installation method
===============================
This project no longer supports installation with `python setup.py install`.
Please use `python -m pip install .` instead.
"""
)
sys.exit(1)

# The code below will never execute, however is required to
# display the "Used by" section on the GitHub repository.
#
# See: https://github.com/github/feedback/discussions/6456

setup(name="django-debug-toolbar")
