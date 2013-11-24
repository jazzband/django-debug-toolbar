# coding: utf-8

from __future__ import absolute_import, unicode_literals

from django.utils import six


class NonAsciiRepr(object):
    def __repr__(self):
        return 'nôt åscíì' if six.PY3 else 'nôt åscíì'.encode('utf-8')
