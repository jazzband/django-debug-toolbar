from django import forms
from django.contrib.auth.models import User


class TemplateReprForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())

    def __repr__(self):
        return repr(self)
