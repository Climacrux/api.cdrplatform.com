from rest_framework_api_key.permissions import BaseHasAPIKey

from .models import OrganisationAPIKey


class HasOrganisationAPIKey(BaseHasAPIKey):
    model = OrganisationAPIKey
