#!/usr/bin/env python3

import sys

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
