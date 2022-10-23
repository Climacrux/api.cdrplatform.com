from django.urls import include, path

from .views import cdr_pricing, cdr_removal_request

app_name = "core"

cdr_routes = [
    path("price/", cdr_pricing, name="cdr_price"),
    path("", cdr_removal_request, name="cdr_request"),
]

urlpatterns = [
    path(
        "cdr/",
        include(cdr_routes),
    ),
]
