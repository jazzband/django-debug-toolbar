from django import forms
from django.conf import settings
from django.utils.encoding import smart_str
from django.core.exceptions import ValidationError

from debug_toolbar.utils.functional import cached_property
from debug_toolbar.utils.sql import reformat_sql

try:
    import json
except ImportError:
    from django.utils import simplejson as json

try:
    from hashlib import sha1
except ImportError:
    from django.utils.hashcompat import sha_constructor as sha1

from debug_toolbar.utils.compat.db import connections


class SQLSelectForm(forms.Form):
    """
    Validate params

        sql: urlencoded sql with positional arguments
        params: JSON encoded parameter values
        duration: time for SQL to execute passed in from toolbar just for redisplay
        hash: the hash of (secret + sql + params) for tamper checking
    """
    sql = forms.CharField()
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

    def clean_sql(self):
        value = self.cleaned_data['sql']

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
        sql, params = self.cleaned_data['sql'], self.cleaned_data['params']
        return reformat_sql(self.cursor.db.ops.last_executed_query(self.cursor, sql, params))

    def make_hash(self, data):
        params = settings.SECRET_KEY + data['sql'] + data['params']
        return sha1(smart_str(params)).hexdigest()

    @property
    def connection(self):
        return connections[self.cleaned_data['alias']]

    @cached_property
    def cursor(self):
        return self.connection.cursor()
