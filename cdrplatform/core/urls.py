from django.urls import path

from .views import cdr_pricing

urlpatterns = [
    path(
        "v1/cdr/price",
        cdr_pricing,
    )
]
