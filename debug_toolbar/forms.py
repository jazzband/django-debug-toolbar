from __future__ import absolute_import, unicode_literals

import hashlib
import hmac
import os

from django import forms
from django.conf import settings
from django.utils.crypto import constant_time_compare
from django.utils.encoding import force_bytes


class ViewFileForm(forms.Form):
    """
    Validate params
        full_path: Full path to file to view
        line_no: Line number to highlight
        hash: the hash of (secret + path + line_no) for tamper checking
    """
    full_path = forms.CharField(widget=forms.HiddenInput())
    line_no = forms.IntegerField(min_value=1, widget=forms.HiddenInput())
    hash = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', None)

        if initial is not None:
            initial['hash'] = self.make_hash(initial)

        super(ViewFileForm, self).__init__(*args, **kwargs)

    def clean_full_path(self):
        path = self.cleaned_data['full_path']

        if not os.path.exists(path):
            raise forms.ValidationError('File does not exist')

        return path

    def clean_hash(self):
        hash = self.cleaned_data['hash']

        if not constant_time_compare(hash, self.make_hash(self.data)):
            raise forms.ValidationError('Tamper alert')

        return hash

    def make_hash(self, data):
        m = hmac.new(key=force_bytes(settings.SECRET_KEY), digestmod=hashlib.sha1)
        for item in [data['full_path'], data['line_no']]:
            m.update(force_bytes(item))
        return m.hexdigest()
