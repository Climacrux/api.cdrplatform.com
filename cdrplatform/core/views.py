from drf_spectacular.utils import extend_schema, extend_schema_serializer
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CurrencyChoices, WeightChoices


class ItemInputSerializer(serializers.Serializer):
    forestation = serializers.IntegerField(
        required=False,
        min_value=1,
    )
    biooil = serializers.IntegerField(
        required=False,
        min_value=1,
    )
    kelp = serializers.IntegerField(
        required=False,
        min_value=1,
    )
    olivine = serializers.IntegerField(
        required=False,
        min_value=1,
    )


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
        items = ItemInputSerializer()
        # Whether or not the fees should be
        include_fees = serializers.BooleanField(
            required=False,
            default=False,
        )

    @extend_schema_serializer(component_name="PricingRequestOutput")
    class OutputSerializer(serializers.Serializer):
        cost = serializers.IntegerField(min_value=0)
        currency = serializers.ChoiceField(
            choices=CurrencyChoices.choices,
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
            # perform the calculation here
            output = self.OutputSerializer(
                {
                    "cost": 100,
                    "currency": input.validated_data.get("currency"),
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
        items = ItemInputSerializer()
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
