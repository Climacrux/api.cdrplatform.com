from django import forms
from django.utils.translation import gettext_lazy as _


class UserRegistrationForm(forms.Form):

    name = forms.CharField(
        required=True,
        label=_("Name"),
        max_length=150,
    )
    email = forms.EmailField(
        required=True,
        label=_("Email"),
    )
    password = forms.CharField(
        required=True,
        label=_("Password"),
        max_length=128,
        widget=forms.PasswordInput,
    )
