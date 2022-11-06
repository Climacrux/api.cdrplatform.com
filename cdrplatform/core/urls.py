from django.urls import include, path

from .views import HealthView, OrgSettingsAPIKeysView

org_settings_routes = (
    [
        path("api-keys/", OrgSettingsAPIKeysView.as_view(), name="apikeys"),
    ],
    "settings",
)

# Namespaced with 'org' so when using names use something like
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
