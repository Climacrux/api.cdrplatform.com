import django.contrib.auth.views as auth_views
from django.contrib import messages
from django.contrib.auth import login
from django.db.utils import IntegrityError
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import FormView

from cdrplatform.core.forms.auth.registration import UserRegistrationForm
from cdrplatform.core.services import user_signup_with_default_customer_organisation


class UserRegisterView(auth_views.RedirectURLMixin, FormView):
    """Used to register users and automatically create a default
    customer organisation for them."""

    template_name = "registration/register.html"
    redirect_authenticated_user = False

    form_class = UserRegistrationForm

    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse("org:settings:api_keys")

    def form_valid(self, form) -> HttpResponse:
        try:
            user = user_signup_with_default_customer_organisation(
                name=form.cleaned_data.get("name"),
                email=form.cleaned_data.get("email"),
                password=form.cleaned_data.get("password"),
            )
        except IntegrityError:
            # If we get a DB integrity error it's likely because the email
            # already addresses to show a message and show this page again
            messages.error(self.request, _("A user with this email already exists"))
            return self.render_to_response(self.get_context_data())

        login(request=self.request, user=user)

        return super().form_valid(form)
