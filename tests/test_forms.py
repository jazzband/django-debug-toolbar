from datetime import datetime, timezone

from django import forms
from django.test import TestCase

from debug_toolbar.forms import SignedDataForm

SIGNATURE = "-WiogJKyy4E8Om00CrFSy0T6XHObwBa6Zb46u-vmeYE"

DATA = {"date": datetime(2020, 1, 1, tzinfo=timezone.utc), "value": "foo"}
SIGNED_DATA = f'{{"date": "2020-01-01 00:00:00+00:00", "value": "foo"}}:{SIGNATURE}'


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
                "date": "2020-01-01 00:00:00+00:00",
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
