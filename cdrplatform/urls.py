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
from django.urls import include, path

app_patterns = [
    path("", include("cdrplatform.core.urls")),
]

other_patterns = [
    path("accounts/", include(("django.contrib.auth.urls", "auth"))),
]
if settings.ENABLE_DJANGO_ADMIN:
    other_patterns.append(
        path(settings.DJANGO_ADMIN_PATH, admin.site.urls),
    )

if settings.DEBUG:
    other_patterns.append(
        path("__debug__/", include("debug_toolbar.urls")),
    )


urlpatterns = app_patterns + other_patterns