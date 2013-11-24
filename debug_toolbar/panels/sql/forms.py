from __future__ import absolute_import, unicode_literals

import json
import hashlib

from django import forms
from django.conf import settings
from django.db import connections
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.core.exceptions import ValidationError

from debug_toolbar.panels.sql.utils import reformat_sql


class SQLSelectForm(forms.Form):
    """
    Validate params

        sql: The sql statement with interpolated params
        raw_sql: The sql statement with placeholders
        params: JSON encoded parameter values
        duration: time for SQL to execute passed in from toolbar just for redisplay
        hash: the hash of (secret + sql + params) for tamper checking
    """
    sql = forms.CharField()
    raw_sql = forms.CharField()
    params = forms.CharField()
    alias = forms.CharField(required=False, initial='default')
    duration = forms.FloatField()
    hash = forms.CharField()

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', None)

        if initial is not None:
            initial['hash'] = self.make_hash(initial)

        super(SQLSelectForm, self).__init__(*args, **kwargs)

        for name in self.fields:
            self.fields[name].widget = forms.HiddenInput()

    def clean_raw_sql(self):
        value = self.cleaned_data['raw_sql']

        if not value.lower().strip().startswith('select'):
            raise ValidationError("Only 'select' queries are allowed.")

        return value

    def clean_params(self):
        value = self.cleaned_data['params']

        try:
            return json.loads(value)
        except ValueError:
            raise ValidationError('Is not valid JSON')

    def clean_alias(self):
        value = self.cleaned_data['alias']

        if value not in connections:
            raise ValidationError("Database alias '%s' not found" % value)

        return value

    def clean_hash(self):
        hash = self.cleaned_data['hash']

        if hash != self.make_hash(self.data):
            raise ValidationError('Tamper alert')

        return hash

    def reformat_sql(self):
        return reformat_sql(self.cleaned_data['sql'])

    def make_hash(self, data):
        params = (force_text(settings.SECRET_KEY) +
                  force_text(data['sql']) + force_text(data['params']))
        return hashlib.sha1(params.encode('utf-8')).hexdigest()

    @property
    def connection(self):
        return connections[self.cleaned_data['alias']]

    @cached_property
    def cursor(self):
        return self.connection.cursor()
