from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView

from cdrplatform.core.forms.org.settings.apikey import NewAPIKeyForm
from cdrplatform.core.selectors import (
    api_key_list_prod_only,
    api_key_list_test_only,
    customer_organisation_get_from_session,
)
from cdrplatform.core.services import api_key_create_from_session


class APIKeysView(LoginRequiredMixin, FormView):

    template_name = "core/org/settings/api-keys.html"
    form_class = NewAPIKeyForm

    def get_context_api_keys(self) -> Dict[str, Any]:
        context = {}

        org = customer_organisation_get_from_session(request=self.request)

        context["api_keys_test"] = api_key_list_test_only(org=org)
        context["api_keys_prod"] = api_key_list_prod_only(org=org)

        return context

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # Merge in the API keys
        context |= self.get_context_api_keys()

        return context

    def form_valid(self, form):
        _, key = api_key_create_from_session(
            request=self.request,
            api_key_name=form.cleaned_data.get("name"),
            test_key=form.cleaned_data.get("test_key", False),
        )

        # Render this template without the form but
        # with the API key.
        context = {"key": key}
        context |= self.get_context_api_keys()
        return self.render_to_response(context)
