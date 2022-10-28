from .models import OrganisationAPIKey, RemovalPartner


def api_key_get_from_key(*, key: str):
    try:
        return OrganisationAPIKey.objects.get_from_key(key)
    except OrganisationAPIKey.DoesNotExist:
        raise  # be explicit


def removal_partner_get_from_method_slug(*, method_slug: str) -> RemovalPartner:
    try:
        return RemovalPartner.objects.get(removal_method__slug=method_slug)
    except RemovalPartner.DoesNotExist:
        raise  # be explicit
