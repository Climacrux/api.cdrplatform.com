from django import forms
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _


class UserRegistrationForm(forms.Form):
    error_css_class = "border-red-700"

    input_classes = """relative block w-full appearance-none
    rounded-none border border-gray-300 px-3 py-2 text-gray-900
    placeholder-gray-500 focus:z-10 focus:border-indigo-500
    focus:outline-none focus:ring-indigo-500 sm:text-sm"""

    name = forms.CharField(
        required=True,
        label=_("Name"),
        max_length=150,
    )
    name.widget.attrs.update(
        {"class": input_classes + " rounded-t-md", "placeholder": _("Your name")}
    )

    email = forms.EmailField(
        required=True,
        label=_("Email"),
        error_messages={
            "unique": _("A user with that email address already exists."),
        },
    )
    email.widget.attrs.update(
        {"class": input_classes, "placeholder": _("Email address")}
    )

    password = forms.CharField(
        required=True,
        label=_("Password"),
        max_length=128,
        widget=forms.PasswordInput,
        validators=(validate_password,),
    )
    password.widget.attrs.update(
        {
            "class": input_classes + " rounded-b-md",
            "placeholder": _("Password (min. 10 chars)"),
        }
    )

    def clean_password(self):
        password = self.cleaned_data.get("password")
        validate_password(password=password)
        return password
