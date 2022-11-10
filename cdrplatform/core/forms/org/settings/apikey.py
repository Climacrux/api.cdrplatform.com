from django import forms
from django.utils.translation import gettext_lazy as _


class NewAPIKeyForm(forms.Form):
    """A lightweight form used to create a new API key."""

    name = forms.CharField(
        required=True,
        label=_("API key name"),
        max_length=50,
    )
    name.widget.attrs.update(
        {
            "class": """block w-full flex-1 rounded-md border-gray-300
        focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm""",
            "placeholder": _("API key name"),
        }
    )

    test_key = forms.BooleanField(
        required=False,
        label=_("Test key"),
    )
    test_key.widget.attrs.update(
        {
            "class": """h-4 w-4 rounded border-gray-300
            text-indigo-600 focus:ring-indigo-500"""
        }
    )
