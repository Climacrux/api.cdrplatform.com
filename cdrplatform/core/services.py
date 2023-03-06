from typing import Dict, List, Tuple

from django.contrib.auth import get_user_model
from django.http.request import HttpRequest
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from cdrplatform.core.consts import SESSION_KEY_ORG_ID
from cdrplatform.core.selectors import (
    customer_organisation_get_from_session,
    removal_method_calculate_removal_cost,
    removal_partner_get_from_method_slug,
    variable_fees_calculate,
)

from .models import (
    CDRUser,
    CurrencyChoices,
    CustomerOrganisation,
    OrganisationAPIKey,
    RemovalPartner,
    RemovalRequest,
    RemovalRequestItem,
    WeightUnitChoices,
)

User = get_user_model()


def user_signup_with_default_customer_organisation(
    *,
    name: str,
    email: str,
    password: str,
):
    new_user = CDRUser.objects.create_user(name=name, email=email, password=password)
    new_user.organisations.create(organisation_name="Default")

    return new_user


def removal_request_create(
    *,
    is_test: bool,
    weight_unit: WeightUnitChoices,
    currency: CurrencyChoices,
    org_id: int,
    request_items: List[Dict[str, str | int]],
) -> RemovalRequest:
    removal_request = RemovalRequest.objects.create(
        is_test=is_test,
        weight_unit=weight_unit,
        requested_datetime=timezone.now(),
        currency=currency,
        customer_organisation_id=org_id,
    )

    for item in request_items:
        # These items should be typed better but for now they need
        # to have a `method_type` and `cdr_amount` attribute
        removal_partner = removal_partner_get_from_method_slug(
            method_slug=item.get("method_type")
        )

        removal_request_item_create(
            removal_partner=removal_partner,
            removal_request=removal_request,
            cdr_amount=item.get("cdr_amount"),
        )

    return removal_request


def removal_request_item_create(
    *,
    removal_partner: RemovalPartner,
    removal_request: RemovalRequest,
    cdr_amount: int,
) -> RemovalRequestItem:
    removal_cost = removal_method_calculate_removal_cost(
        removal_partner=removal_partner,
        currency=removal_request.currency,
        cdr_amount=cdr_amount,
        weight_unit=removal_request.weight_unit,
    )

    variable_fees = variable_fees_calculate(removal_cost=removal_cost)

    return RemovalRequestItem.objects.create(
        removal_partner=removal_partner,
        removal_request=removal_request,
        cdr_cost=removal_cost,
        variable_fees=variable_fees,
        cdr_amount=cdr_amount,
    )


def customer_organisation_create(
    *,
    user: User,
    organisation_name: str,
) -> CustomerOrganisation:
    return user.customer_organisation_set.create(
        organisation_name=organisation_name,
    )


def customer_organisation_save_to_session(
    *,
    organisation: CustomerOrganisation,
    request: HttpRequest,
):
    if not request.user.is_authenticated:
        # Only for authenticated users
        raise PermissionDenied

    request.session[SESSION_KEY_ORG_ID] = organisation.short_id


def api_key_create(
    *,
    organisation: CustomerOrganisation,
    api_key_name: str = "",
    test_key: bool = False,
) -> Tuple[OrganisationAPIKey, str]:
    """Generates an API key for a given organisation"""
    if test_key:
        key_objects = OrganisationAPIKey.test_objects
    else:
        key_objects = OrganisationAPIKey.objects

    if api_key_name is None:
        api_key_name = ""

    return key_objects.create_key(
        organisation=organisation,
        name=api_key_name,
    )


def api_key_create_from_session(
    *,
    request: HttpRequest,
    api_key_name: str,
    test_key: bool = False,
) -> Tuple[OrganisationAPIKey, str]:
    """Generates an API key by extracting the current organisation from
    the HTTP request"""
    org = customer_organisation_get_from_session(request=request)

    return api_key_create(
        organisation=org, api_key_name=api_key_name, test_key=test_key
    )


def api_key_revoke(
    *,
    org: CustomerOrganisation,
    key_prefix: str,
):
    """Expires a given API key based on the prefix and the organisation."""
    _ = OrganisationAPIKey.objects.filter(prefix=key_prefix, organisation=org).update(
        expiry_date=timezone.now()
    )
