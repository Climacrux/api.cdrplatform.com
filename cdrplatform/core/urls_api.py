from django.urls import include, path

from .api.cdr.pricing import CDRPricingView
from .api.cdr.purchase import CDRRemovalView

app_name = "core"

cdr_routes = [
    path("price/", CDRPricingView.as_view(), name="cdr_price"),
    path("", CDRRemovalView.as_view(), name="cdr_request"),
]

urlpatterns = [
    path("cdr/", include(cdr_routes)),
]
