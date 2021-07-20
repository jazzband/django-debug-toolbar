from django import forms


class HistoryStoreForm(forms.Form):
    """
    Validate params

        store_id: The key for the store instance to be fetched.
    """

    store_id = forms.CharField(widget=forms.HiddenInput())
