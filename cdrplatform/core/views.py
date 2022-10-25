import collections
import functools
import math
from typing import Iterable

from django.utils.functional import lazy
from drf_spectacular.utils import extend_schema, extend_schema_serializer
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .data import FEES
from .models import CurrencyChoices, RemovalPartner, WeightChoices


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


class InputRemovalMethodSerializer(serializers.Serializer):
    method_type = serializers.ChoiceField(
        required=True,
        choices=lazy(removal_method_choices, tuple)(),
    )
    amount = serializers.IntegerField(required=True, min_value=1)


class BaseAPIView(APIView):
    pass


class CDRPricingView(BaseAPIView):
    """Calculate a carbon dioxide removal price for a given portfolio of
    CDR items.
    """

    @extend_schema_serializer(component_name="PricingRequestInput")
    class InputSerializer(serializers.Serializer):
        weight_unit = serializers.ChoiceField(
            required=True,
            choices=WeightChoices.choices,
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
            choices=WeightChoices.choices,
        )

    @extend_schema(
        request=InputSerializer,
        responses={
            status.HTTP_201_CREATED: OutputSerializer,
        },
        methods=("POST",),
    )
    def post(self, request):
        input = self.InputSerializer(data=request.data)
        # We raise an exception if the data is invalid because it will be automatically
        # caught and handled by drf-standardized-errors.
        # This means it will have the same error format as every other error 👍
        if input.is_valid(raise_exception=True):
            # todo: perform the calculation here

            def calculate_cost(element):
                partner = RemovalPartner.objects.get(
                    removal_method__slug=element["method_type"]
                )
                if input.validated_data["weight_unit"] == "t":
                    amount_g = element["amount"] * 1000 * 1000
                elif input.validated_data["weight_unit"] == "kg":
                    amount_g = element["amount"] * 1000
                else:
                    amount_g = element["amount"]

                element["cost"] = int(partner.cost_per_tonne * amount_g / (1000 * 1000))
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


class CDRRemoval(BaseAPIView):
    """Order and commit to purchasing carbon dioxide removal for a given portfolio of
    CDR items.
    """

    @extend_schema_serializer(component_name="RemovalRequestInput")
    class InputSerializer(serializers.Serializer):
        weight_unit = serializers.ChoiceField(
            required=True,
            choices=WeightChoices.choices,
        )
        currency = serializers.ChoiceField(
            choices=CurrencyChoices.choices,
        )
        items = InputRemovalMethodSerializer(many=True)
        # Whether or not the fees should be
        include_fees = serializers.BooleanField(
            required=False,
            default=False,
        )

    @extend_schema_serializer(component_name="RemovalRequestOutput")
    class OutputSerializer(serializers.Serializer):
        transaction_uuid = serializers.UUIDField()

    @extend_schema(
        request=InputSerializer,
        responses={
            status.HTTP_201_CREATED: OutputSerializer,
        },
        methods=("POST",),
    )
    def post(self, request):
        return Response({"foo": request.version})
