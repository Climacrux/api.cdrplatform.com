from django.urls import include, path

from .views import cdr_pricing

app_name = "core"

cdr_routes = [
    path("price/", cdr_pricing),
]

urlpatterns = [
    path(
        "cdr/",
        include(cdr_routes),
    )
]
