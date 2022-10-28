import collections
import decimal
import functools
import math
from typing import Iterable

from django.utils import timezone
from django.utils.functional import lazy
from drf_spectacular.utils import extend_schema, extend_schema_serializer
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from cdrplatform.core.permissions import HasOrganisationAPIKey

from .data import FEES
from .models import (
    CurrencyChoices,
    CurrencyConversionRate,
    OrganisationAPIKey,
    RemovalPartner,
    RemovalRequest,
    RemovalRequestItem,
    WeightUnitChoices,
)


def removal_partner_list() -> Iterable[RemovalPartner]:
    return RemovalPartner.objects.all()


def removal_method_choices():
    try:
        _partners = [
            (m.removal_method.slug, m.removal_method.name)
            for m in removal_partner_list().select_related("removal_method")
        ]
    except Exception:
        _partners = tuple(tuple())
    return _partners


class BaseAPIView(APIView):
    pass


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


@extend_schema(
    tags=("CO₂ Removal",),
)
class CDRPricingView(BaseAPIView, UnauthenticatedMixin, APIKeyRequiredMixin):
    """Calculate a carbon dioxide removal price for a given portfolio of
    CDR items.
    """

    @extend_schema_serializer(component_name="PricingRequestInput")
    class InputSerializer(serializers.Serializer):
        @extend_schema_serializer(component_name="PricingRequestRemovalMethod")
        class InputRemovalMethodSerializer(serializers.Serializer):
            method_type = serializers.ChoiceField(
                required=True,
                choices=lazy(removal_method_choices, tuple)(),
            )
            cdr_amount = serializers.IntegerField(required=True, min_value=1)

        weight_unit = serializers.ChoiceField(
            required=True,
            choices=WeightUnitChoices.choices,
        )
        currency = serializers.ChoiceField(
            required=True,
            choices=CurrencyChoices.choices,
        )
        items = InputRemovalMethodSerializer(many=True, min_length=1)

        def validate_items(self, value):
            counter = collections.Counter(map(lambda x: x["method_type"], value))
            for key in counter:
                if counter[key] > 1:
                    raise serializers.ValidationError(
                        f'"{key}" can not appear more than once in items.'
                    )
            return value

    @extend_schema_serializer(component_name="PricingRequestOutput")
    class OutputSerializer(serializers.Serializer):
        class CostSerializer(serializers.Serializer):
            items = serializers.ListField()
            removal = serializers.IntegerField()
            variable_fees = serializers.IntegerField()
            total = serializers.IntegerField()

        cost = CostSerializer()
        currency = serializers.ChoiceField(
            choices=CurrencyChoices.choices,
        )
        weight_unit = serializers.ChoiceField(
            required=True,
            choices=WeightUnitChoices.choices,
        )

    @extend_schema(
        operation_id="Calculate price of CDR",
        request=InputSerializer,
        responses={
            status.HTTP_201_CREATED: OutputSerializer,
        },
        tags=("CO₂ Removal",),
        description="""Calculate the removal costs and
fees for a future CO₂ removal purchase.""",
    )
    def post(self, request):
        input = self.InputSerializer(data=request.data)
        # We raise an exception if the data is invalid because it will be automatically
        # caught and handled by drf-standardized-errors.
        # This means it will have the same error format as every other error 👍
        if input.is_valid(raise_exception=True):

            def calculate_cost(element):
                partner = RemovalPartner.objects.get(
                    removal_method__slug=element["method_type"]
                )
                # We specify the default ordering on the Model itself (`-date_time`)
                # so no need to explicitly order again here.
                currency_conversion_rate = CurrencyConversionRate.objects.filter(
                    # We convert from the partner currency into the currency requested
                    # e.g. I want prices in CHF so convert partner cost in USD to CHF
                    from_currency=partner.currency,
                    to_currency=input.validated_data.get("currency"),
                ).first()  # Limit to 1 record to get the latest conversion rate

                if currency_conversion_rate is None:
                    raise serializers.ValidationError(
                        f'Unable to convert partner currency "{partner.currency}"'
                        + f' to "{input.validated_data.get("currency")}"'
                    )

                if input.validated_data["weight_unit"] == "t":
                    amount_g = element["cdr_amount"] * 1000 * 1000
                elif input.validated_data["weight_unit"] == "kg":
                    amount_g = element["cdr_amount"] * 1000
                else:
                    amount_g = element["cdr_amount"]

                partner_cost = decimal.Decimal(
                    partner.cost_per_tonne * amount_g / (1000 * 1000)
                )

                element["cost"] = math.ceil(
                    partner_cost * currency_conversion_rate.rate
                )
                return element

            items = list(map(calculate_cost, input.validated_data.get("items")))
            removal_cost = functools.reduce(lambda x, y: x + y["cost"], items, 0)
            variable_fee = math.ceil(
                removal_cost
                * FEES["climacrux"]["variable_pct"]
                / (100 - FEES["climacrux"]["variable_pct"])
            )

            output = self.OutputSerializer(
                {
                    "cost": {
                        "items": items,
                        "removal": removal_cost,
                        "variable_fees": variable_fee,
                        "total": removal_cost + variable_fee,
                    },
                    "currency": input.validated_data.get("currency"),
                    "weight_unit": input.validated_data.get("weight_unit"),
                }
            )
            return Response(output.data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=("CO₂ Removal",),
)
class CDRRemovalView(BaseAPIView, UnauthenticatedMixin, APIKeyRequiredMixin):
    """Order and commit to purchasing carbon dioxide removal for a given portfolio of
    CDR items.
    """

    @extend_schema_serializer(component_name="RemovalRequestInput")
    class InputSerializer(serializers.Serializer):
        @extend_schema_serializer(component_name="CDRRemovalRequestRemovalMethod")
        class InputRemovalMethodSerializer(serializers.Serializer):
            method_type = serializers.ChoiceField(
                required=True,
                choices=lazy(removal_method_choices, tuple)(),
            )
            cdr_amount = serializers.IntegerField(required=True, min_value=1)

        weight_unit = serializers.ChoiceField(
            required=True,
            choices=WeightUnitChoices.choices,
        )
        currency = serializers.ChoiceField(
            choices=CurrencyChoices.choices,
        )
        items = InputRemovalMethodSerializer(many=True, min_length=1)

        def validate_items(self, value):
            counter = collections.Counter(map(lambda x: x["method_type"], value))
            for key in counter:
                if counter[key] > 1:
                    raise serializers.ValidationError(
                        f'"{key}" can not appear more than once in items.'
                    )
            return value

    @extend_schema_serializer(component_name="RemovalRequestOutput")
    class OutputSerializer(serializers.Serializer):
        transaction_uuid = serializers.UUIDField()

    @extend_schema(
        request=InputSerializer,
        responses={
            status.HTTP_201_CREATED: OutputSerializer,
        },
        operation_id="Purchase CDR",
        description="""Submit .

By using this endpoint your organisation is committing to buy

Returns a transaction ID that is unique to this removal request. This can
be stored in your records and used to retrieve the status of the request,
removal certificate

**Note:** This will not return any """,
    )
    def post(self, request):
        input = self.InputSerializer(data=request.data)
        # We raise an exception if the data is invalid because it will be automatically
        # caught and handled by drf-standardized-errors.
        # This means it will have the same error format as every other error 👍
        if input.is_valid(raise_exception=True):
            key = request.META["HTTP_AUTHORIZATION"].split()[1]
            api_key = OrganisationAPIKey.objects.get_from_key(key)
            removal_request = RemovalRequest.objects.create(
                weight_unit=input.validated_data.get("weight_unit"),
                requested_datetime=timezone.now(),
                currency=input.validated_data.get("currency"),
                customer_organisation_id=api_key.organisation_id,
            )
            for item in input.validated_data.get("items"):
                removal_partner = RemovalPartner.objects.get(
                    removal_method__slug=item["method_type"]
                )
                RemovalRequestItem.objects.create(
                    removal_partner=removal_partner,
                    removal_request=removal_request,
                    cdr_cost=0,
                    cdr_amount=item.get("cdr_amount"),
                )
            output = self.OutputSerializer({"transaction_uuid": removal_request.uuid})
            return Response(output.data, status=status.HTTP_201_CREATED)
