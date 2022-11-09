from django import forms
from django.contrib.auth.password_validation import validate_password
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
        error_messages={
            "unique": _("A user with that email address already exists."),
        },
    )
    password = forms.CharField(
        required=True,
        label=_("Password"),
        max_length=128,
        widget=forms.PasswordInput,
        validators=(validate_password,),
    )

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validate_password(password=password)
        return password
