from cdrplatform.core.permissions import HasOrganisationAPIKey


class UnauthenticatedMixin:
    """Removes the default authentication. This is useful for us as API endpoints
    will require authentication by default (configured in `settings.py`) but
    can be explicitly disabled when we want to rely on using an APIKey to
    associate a request with an Organisation."""

    authentication_classes = ()


class APIKeyRequiredMixin:
    """A base view that requires callers to have an Organisation API
    Key attached."""

    permission_classes = (HasOrganisationAPIKey,)
