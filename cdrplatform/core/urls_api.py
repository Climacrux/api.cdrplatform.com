from django.urls import include, path, register_converter

from cdrplatform.core.api.certificate.retrieve import CertificateRetrievalView

from .api.cdr.pricing import CDRPricingView
from .api.cdr.purchase import CDRRemovalView
from .converters import CertificateIDConverter

app_name = "core"

register_converter(CertificateIDConverter, "certificate_id")

cdr_routes = [
    path("price/", CDRPricingView.as_view(), name="cdr_price"),
    path("", CDRRemovalView.as_view(), name="cdr_request"),
]

certificate_routes = [
    path(
        "<certificate_id:id>/",
        CertificateRetrievalView.as_view(),
        name="certificate_retrieve",
    ),
]

urlpatterns = [
    path("cdr/", include(cdr_routes)),
    path("certificate/", include(certificate_routes)),
]
