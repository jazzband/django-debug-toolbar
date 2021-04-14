import json

from django import forms
from django.core.exceptions import ValidationError
from django.db import connections
from django.utils.functional import cached_property

from debug_toolbar.panels.sql.utils import reformat_sql


class SQLSelectForm(forms.Form):
    """
    Validate params

        sql: The sql statement with interpolated params
        raw_sql: The sql statement with placeholders
        params: JSON encoded parameter values
        duration: time for SQL to execute passed in from toolbar just for redisplay
    """

    sql = forms.CharField()
    raw_sql = forms.CharField()
    params = forms.CharField()
    alias = forms.CharField(required=False, initial="default")
    duration = forms.FloatField()

    def clean_raw_sql(self):
        value = self.cleaned_data["raw_sql"]

        if not value.lower().strip().startswith("select"):
            raise ValidationError("Only 'select' queries are allowed.")

        return value

    def clean_params(self):
        value = self.cleaned_data["params"]

        try:
            return json.loads(value)
        except ValueError:
            raise ValidationError("Is not valid JSON")

    def clean_alias(self):
        value = self.cleaned_data["alias"]

        if value not in connections:
            raise ValidationError("Database alias '%s' not found" % value)

        return value

    def reformat_sql(self):
        return reformat_sql(self.cleaned_data["sql"], with_toggle=False)

    @property
    def connection(self):
        return connections[self.cleaned_data["alias"]]

    @cached_property
    def cursor(self):
        return self.connection.cursor()
