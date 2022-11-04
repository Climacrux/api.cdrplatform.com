from typing import Dict, List, Tuple

from django.utils import timezone

from cdrplatform.core.selectors import (
    removal_method_calculate_removal_cost,
    removal_partner_get_from_method_slug,
    variable_fees_calculate,
)

from .models import (
    CurrencyChoices,
    CustomerOrganisation,
    OrganisationAPIKey,
    RemovalPartner,
    RemovalRequest,
    RemovalRequestItem,
    WeightUnitChoices,
)


def removal_request_create(
    *,
    weight_unit: WeightUnitChoices,
    currency: CurrencyChoices,
    org_id: int,
    request_items: List[Dict[str, str | int]],
) -> RemovalRequest:
    removal_request = RemovalRequest.objects.create(
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
