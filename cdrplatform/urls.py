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
from django.contrib.auth import views as auth_views
from django.urls import include, path, reverse_lazy
from django.views.generic.base import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from cdrplatform.core.forms.auth.login import LoginForm
from cdrplatform.core.views.auth.registration import UserRegisterView

auth_patterns = (
    path(
        "login/",
        auth_views.LoginView.as_view(
            redirect_authenticated_user=True, form_class=LoginForm
        ),
        name="login",
    ),
    path(
        "register/",
        UserRegisterView.as_view(redirect_authenticated_user=True),
        name="register",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
)

app_patterns = (
    path("", RedirectView.as_view(url=reverse_lazy("redoc"))),
    path("", include("cdrplatform.core.urls")),
    # Separate URLs file for API urls
    path("v1/", include("cdrplatform.core.urls_api", namespace="v1")),
    # path("v2/", include("cdrplatform.core.urls_api", namespace="v2")),
    path("schema/", SpectacularAPIView.as_view(api_version="v1"), name="schema"),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
)

other_patterns = (path("accounts/", include((auth_patterns, "auth"))),)

if settings.ENABLE_DJANGO_ADMIN:
    other_patterns += (path(settings.DJANGO_ADMIN_PATH, admin.site.urls),)

if settings.DEBUG:
    other_patterns += (path("__debug__/", include("debug_toolbar.urls")),)


urlpatterns = app_patterns + other_patterns
