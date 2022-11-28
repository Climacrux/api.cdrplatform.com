import math
from decimal import Decimal
from typing import Iterable, Optional

from django.contrib.auth import get_user_model
from django.http.request import HttpRequest
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from cdrplatform.core.consts import SESSION_KEY_ORG_ID
from cdrplatform.core.crypto import TestKeyGenerator
from cdrplatform.core.data import FEES
from cdrplatform.core.exceptions import (
    APIKeyExpiredException,
    APIKeyNotPresentOrRevoked,
    CustomerOrganizationNotFound,
    MissingData,
)

from .models import (
    CurrencyChoices,
    CurrencyConversionRate,
    CustomerOrganisation,
    OrganisationAPIKey,
    RemovalPartner,
    WeightUnitChoices,
)

User = get_user_model()


def api_key_list_all(
    *,
    org: CustomerOrganisation,
) -> Iterable[OrganisationAPIKey]:
    return OrganisationAPIKey.objects.filter(organisation=org)


def api_key_list_test_only(
    *,
    org: CustomerOrganisation,
) -> Iterable[OrganisationAPIKey]:
    return api_key_list_all(org=org).filter(
        prefix__istartswith=TestKeyGenerator.prefix,
    )


def api_key_list_prod_only(
    *,
    org: CustomerOrganisation,
) -> Iterable[OrganisationAPIKey]:
    return api_key_list_all(org=org).exclude(
        prefix__istartswith=TestKeyGenerator.prefix,
    )


def api_key_get_from_key(*, key: str) -> OrganisationAPIKey:
    try:
        return OrganisationAPIKey.objects.get_from_key(key=key)
    except OrganisationAPIKey.DoesNotExist as err:
        raise err  # be explicit


def api_key_must_be_present_and_valid(
    *,
    key: str,
) -> OrganisationAPIKey:
    """Tries to look up an API key and raises an exception if one
    of the following occurs:

    - Key not present: :class:`APIKeyNotPresentOrRevoked`
    - Key revoked: :class:`APIKeyNotPresentOrRevoked`
    - Key expired: :class:`APIKeyExpiredException`
    """
    try:
        api_key = api_key_get_from_key(key=key)
    except OrganisationAPIKey.DoesNotExist:
        raise APIKeyNotPresentOrRevoked

    if api_key.has_expired or api_key.revoked:
        raise APIKeyExpiredException
    return api_key


def removal_partner_get_from_method_slug(
    *,
    method_slug: str,
) -> RemovalPartner:
    try:
        return RemovalPartner.objects.get(removal_method__slug=method_slug)
    except RemovalPartner.DoesNotExist as err:
        raise err  # be explicit


def removal_partner_list() -> Iterable[RemovalPartner]:
    return RemovalPartner.objects.filter(disabled=False)


def currency_conversion_rate_get_latest(
    *, from_currency: str, to_currency: str
) -> CurrencyConversionRate:
    # We specify the default ordering on the Model itself (`-date_time`)
    # so no need to explicitly order again here.
    return CurrencyConversionRate.objects.filter(
        # We convert from the partner currency into the currency requested
        # e.g. I want prices in CHF so convert partner cost in USD to CHF
        from_currency=from_currency,
        to_currency=to_currency,
    ).first()  # Limit to 1 record to get the latest conversion rate


def cdr_weight_get_in_grams(*, cdr_amount: int, weight_unit: WeightUnitChoices) -> int:
    if weight_unit == "t":
        cdr_amount_g = cdr_amount * 1000 * 1000
    elif weight_unit == "kg":
        cdr_amount_g = cdr_amount * 1000
    else:
        cdr_amount_g = cdr_amount

    return cdr_amount_g


def partner_cost_calculate(*, partner: RemovalPartner, cdr_amount_g: int) -> Decimal:
    return Decimal(partner.cost_per_tonne * cdr_amount_g / (1000 * 1000))


def removal_method_choices():
    try:
        _partners = [
            (m.removal_method.slug, m.removal_method.name)
            for m in removal_partner_list().select_related("removal_method")
        ]
    except Exception:
        _partners = tuple(tuple())
    return _partners


def removal_method_calculate_removal_cost(
    *,
    removal_partner: Optional[RemovalPartner] = None,
    removal_method_slug: Optional[str] = None,
    currency: CurrencyChoices,
    cdr_amount: int,
    weight_unit: WeightUnitChoices,
) -> int:
    """For a given removal method, lookup the corresponding partner
    (we only have one partner per removal method at this time) and
    calculate the removal cost for the given weight in the respective
    currency.

    Currency is required as we convert from the native partner currency
    into the requested currency.

    Note: This does not include fees, it is purely the removal cost.
    """

    if removal_partner is None and removal_method_slug is None:
        raise MissingData

    _partner = removal_partner
    if removal_partner is None:
        _partner = removal_partner_get_from_method_slug(
            method_slug=removal_method_slug,
        )

    currency_conversion_rate = currency_conversion_rate_get_latest(
        from_currency=_partner.currency,
        to_currency=currency,
    )

    if currency_conversion_rate is None:
        raise serializers.ValidationError(
            f'Unable to convert partner currency "{_partner.currency}"'
            + f' to "{input.validated_data.get("currency")}"'
        )

    partner_cost = partner_cost_calculate(
        partner=_partner,
        cdr_amount_g=cdr_weight_get_in_grams(
            cdr_amount=cdr_amount, weight_unit=weight_unit
        ),
    )

    return math.ceil(partner_cost * currency_conversion_rate.rate)


def variable_fees_calculate(*, removal_cost: int) -> int:
    """Given a removal cost, calculates the variable fee."""
    return math.ceil(
        removal_cost
        * FEES["climacrux"]["variable_pct"]
        / (100 - FEES["climacrux"]["variable_pct"])
    )


def customer_organisation_get_by_short_id(*, short_id: str) -> CustomerOrganisation:
    return CustomerOrganisation.objects.filter(short_id=short_id)


def customer_organisation_get_default(*, user: User) -> CustomerOrganisation:
    """Returns the default organisation of a user. Currently just returns the
    oldest organisation as we don't filter on default."""
    return CustomerOrganisation.objects.filter(users=user).first()


def customer_organisation_get_from_session(
    *, request: HttpRequest
) -> CustomerOrganisation:
    """Looks up an organisation from a session. If not present
    then uses the users default organisation."""
    if not request.user.is_authenticated:
        raise PermissionDenied
    org_short_id = request.session.get(SESSION_KEY_ORG_ID)
    if org_short_id is None:
        org = customer_organisation_get_default(user=request.user)
    else:
        org = customer_organisation_get_by_short_id(short_id=org_short_id)

    if org is None:
        raise CustomerOrganizationNotFound

    return org
