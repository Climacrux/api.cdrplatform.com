from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed, NotFound, ValidationError


class APIKeyExpiredException(AuthenticationFailed):
    default_detail = _("API Key has expired")


class APIKeyNotPresentOrRevoked(AuthenticationFailed):
    default_detail = _("API Key does not exist or has been revoked")


class MissingData(ValidationError):
    default_detail = _("Invalid data")


class CustomerOrganizationNotFound(NotFound):
    default_detail = _("Customer Organisation not found")
