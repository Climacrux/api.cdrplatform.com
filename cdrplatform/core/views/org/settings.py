from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class APIKeysView(LoginRequiredMixin, TemplateView):

    template_name = "core/org/settings/api-keys.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        # At the moment we only allow users to have one organisation so we can
        # look up the organisation they are connected to.
        # Todo: replace this with a cookie to change

        return context

    def post(self, request):
        return
