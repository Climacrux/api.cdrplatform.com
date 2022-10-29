import math
from decimal import Decimal

from rest_framework import serializers

from cdrplatform.core.data import FEES

from .models import (
    CurrencyChoices,
    CurrencyConversionRate,
    OrganisationAPIKey,
    RemovalPartner,
    WeightUnitChoices,
)


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


def cdr_weight_get_in_grams(*, cdr_weight: int, weight_unit: WeightUnitChoices) -> int:
    if weight_unit == "t":
        cdr_weight_g = cdr_weight * 1000 * 1000
    elif weight_unit == "kg":
        cdr_weight_g = cdr_weight_g * 1000
    else:
        cdr_weight_g = cdr_weight

    return cdr_weight_g


def partner_cost_calculate(*, partner: RemovalPartner, cdr_weight_g: int) -> Decimal:
    return Decimal(partner.cost_per_tonne * cdr_weight_g / (1000 * 1000))


def removal_method_calculate_removal_cost(
    *,
    removal_method_slug: str,
    currency: CurrencyChoices,
    cdr_weight: int,
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

    partner = removal_partner_get_from_method_slug(method_slug=removal_method_slug)
    currency_conversion_rate = currency_conversion_rate_get_latest(
        from_currency=partner.currency,
        to_currency=currency,
    )

    if currency_conversion_rate is None:
        raise serializers.ValidationError(
            f'Unable to convert partner currency "{partner.currency}"'
            + f' to "{input.validated_data.get("currency")}"'
        )

    partner_cost = partner_cost_calculate(
        partner=partner,
        cdr_weight_g=cdr_weight_get_in_grams(
            cdr_weight=cdr_weight, weight_unit=weight_unit
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
