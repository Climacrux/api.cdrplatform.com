from django.urls import include, path

from .views import CDRPricing, CDRRemoval

app_name = "core"

cdr_routes = [
    path("price/", CDRPricing.as_view(), name="cdr_price"),
    path("", CDRRemoval.as_view(), name="cdr_request"),
]

urlpatterns = [
    path("cdr/", include(cdr_routes)),
]
