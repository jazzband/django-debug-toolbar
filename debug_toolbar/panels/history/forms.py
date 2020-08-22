import hashlib
import hmac

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.crypto import constant_time_compare
from django.utils.encoding import force_bytes


class HistoryStoreForm(forms.Form):
    """
    Validate params

        store_id: The key for the store instance to be fetched.
    """

    store_id = forms.CharField(widget=forms.HiddenInput())
    hash = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        initial = kwargs.get("initial", None)

        if initial is not None:
            initial["hash"] = self.make_hash(initial)

        super().__init__(*args, **kwargs)

    @staticmethod
    def make_hash(data):
        m = hmac.new(key=force_bytes(settings.SECRET_KEY), digestmod=hashlib.sha1)
        m.update(force_bytes(data["store_id"]))
        return m.hexdigest()

    def clean_hash(self):
        hash = self.cleaned_data["hash"]

        if not constant_time_compare(hash, self.make_hash(self.data)):
            raise ValidationError("Tamper alert")

        return hash
