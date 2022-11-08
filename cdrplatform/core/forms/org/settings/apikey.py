from django import forms
from django.utils.translation import gettext_lazy as _


class NewAPIKeyForm(forms.Form):
    """A lightweight form used to create a new API key."""

    name = forms.CharField(
        required=True,
        label=_("API key name"),
        max_length=50,
    )
    test_key = forms.BooleanField(
        required=False,
        label=_("Test key"),
    )
