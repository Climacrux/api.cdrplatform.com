import collections
import functools

from django.utils.functional import lazy
from drf_spectacular.utils import extend_schema, extend_schema_serializer
from rest_framework import serializers, status
from rest_framework.response import Response

from cdrplatform.core.api.base import BaseAPIView
from cdrplatform.core.auth import APIKeyRequiredMixin, UnauthenticatedMixin
from cdrplatform.core.models import CurrencyChoices, WeightUnitChoices
from cdrplatform.core.selectors import (
    removal_method_calculate_removal_cost,
    removal_method_choices,
    variable_fees_calculate,
)


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
                element["cost"] = removal_method_calculate_removal_cost(
                    removal_method_slug=element["method_type"],
                    currency=input.validated_data.get("currency"),
                    cdr_amount=element["cdr_amount"],
                    weight_unit=input.validated_data["weight_unit"],
                )
                return element

            items = list(map(calculate_cost, input.validated_data.get("items")))
            removal_cost = functools.reduce(lambda x, y: x + y["cost"], items, 0)
            variable_fee = variable_fees_calculate(removal_cost=removal_cost)

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
