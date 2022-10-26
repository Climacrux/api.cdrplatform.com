"""cdrplatform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.views.generic.base import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

app_patterns = (
    path("", RedirectView.as_view(url=reverse_lazy("swagger-ui"))),
    path("v1/", include("cdrplatform.core.urls", namespace="v1")),
    # path("v2/", include("cdrplatform.core.urls", namespace="v2")),
    path("schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
)

other_patterns = (
    # path("accounts/", include(("django.contrib.auth.urls", "auth"))),
)
if settings.ENABLE_DJANGO_ADMIN:
    other_patterns += (path(settings.DJANGO_ADMIN_PATH, admin.site.urls),)

if settings.DEBUG:
    other_patterns += (path("__debug__/", include("debug_toolbar.urls")),)


urlpatterns = app_patterns + other_patterns
