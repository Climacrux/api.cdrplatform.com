from django.urls import include, path

from .views import CDRPricingView, CDRRemovalView

app_name = "core"

cdr_routes = [
    path("price/", CDRPricingView.as_view(), name="cdr_price"),
    path("", CDRRemovalView.as_view(), name="cdr_request"),
]

urlpatterns = [
    path("cdr/", include(cdr_routes)),
]
