from datetime import datetime

import django
from django import forms
from django.test import TestCase

from debug_toolbar.forms import SignedDataForm

# Django 3.1 uses sha256 by default.
SIGNATURE = (
    "v02QBcJplEET6QXHNWejnRcmSENWlw6_RjxLTR7QG9g"
    if django.VERSION >= (3, 1)
    else "ukcAFUqYhUUnqT-LupnYoo-KvFg"
)

DATA = {"value": "foo", "date": datetime(2020, 1, 1)}
SIGNED_DATA = '{{"date": "2020-01-01 00:00:00", "value": "foo"}}:{}'.format(SIGNATURE)


class FooForm(forms.Form):
    value = forms.CharField()
    # Include a datetime in the tests because it's not serializable back
    # to a datetime by SignedDataForm
    date = forms.DateTimeField()


class TestSignedDataForm(TestCase):
    def test_signed_data(self):
        data = {"signed": SignedDataForm.sign(DATA)}
        form = SignedDataForm(data=data)
        self.assertTrue(form.is_valid())
        # Check the signature value
        self.assertEqual(data["signed"], SIGNED_DATA)

    def test_verified_data(self):
        form = SignedDataForm(data={"signed": SignedDataForm.sign(DATA)})
        self.assertEqual(
            form.verified_data(),
            {
                "value": "foo",
                "date": "2020-01-01 00:00:00",
            },
        )
        # Take it back to the foo form to validate the datetime is serialized
        foo_form = FooForm(data=form.verified_data())
        self.assertTrue(foo_form.is_valid())
        self.assertDictEqual(foo_form.cleaned_data, DATA)

    def test_initial_set_signed(self):
        form = SignedDataForm(initial=DATA)
        self.assertEqual(form.initial["signed"], SIGNED_DATA)

    def test_prevents_tampering(self):
        data = {"signed": SIGNED_DATA.replace('"value": "foo"', '"value": "bar"')}
        form = SignedDataForm(data=data)
        self.assertFalse(form.is_valid())
