from typing import Any

from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext as _


class LoginForm(AuthenticationForm):
    """Custom login form to style widgets"""

    input_classes = """relative block w-full appearance-none
    rounded-none border border-gray-300 px-3 py-2 text-gray-900
    placeholder-gray-500 focus:z-10 focus:border-indigo-500
    focus:outline-none focus:ring-indigo-500 sm:text-sm"""
    label_classes = "sr-only"

    def __init__(self, request: Any = ..., *args: Any, **kwargs: Any) -> None:
        super().__init__(request, *args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": self.input_classes + " rounded-t-md",
                "placeholder": _("Email address"),
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": self.input_classes + " rounded-b-md",
                "placeholder": _("Password"),
            }
        )
