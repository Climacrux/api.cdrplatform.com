from django.views.generic import TemplateView


class APIKeysView(TemplateView):

    template_name = "core/org/settings/api-keys.html"

    def post(self, request):
        return
