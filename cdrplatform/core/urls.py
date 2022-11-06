from django.urls import include, path

from .api.healthcheck import HealthView
from .views.org.settings import APIKeysView

# Namespaced with `settings` so when using URL names use something like
# `core:org:settings:api_keys`
org_settings_routes = (
    [
        path("api-keys/", APIKeysView.as_view(), name="api_keys"),
    ],
    "settings",
)

# Namespaced with 'org' so when using URL names use something like
# `core:org:create`
org_routes = (
    [
        path("settings/", include(org_settings_routes)),
    ],
    "org",
)

urlpatterns = [
    path("org/", include(org_routes)),
    path("health/", HealthView.as_view(), name="health_check"),
]
