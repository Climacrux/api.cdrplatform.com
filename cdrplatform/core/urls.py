from django.urls import include, path

from .views import CDRPricingView, CDRRemoval

app_name = "core"

cdr_routes = [
    path("price/", CDRPricingView.as_view(), name="cdr_price"),
    path("", CDRRemoval.as_view(), name="cdr_request"),
]

urlpatterns = [
    path("cdr/", include(cdr_routes)),
]
