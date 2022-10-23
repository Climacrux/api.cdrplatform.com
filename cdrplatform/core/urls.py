from django.urls import include, path

from .views import CDRPricing, cdr_removal_request

app_name = "core"

cdr_routes = [
    path("price/", CDRPricing.as_view(), name="cdr_price"),
    path("", cdr_removal_request, name="cdr_request"),
]

urlpatterns = [
    path("cdr/", include(cdr_routes)),
]
