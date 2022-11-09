import collections

from django.utils.functional import lazy
from drf_spectacular.utils import extend_schema, extend_schema_serializer
from rest_framework import serializers, status
from rest_framework.response import Response

from cdrplatform.core.api.base import BaseAPIView
from cdrplatform.core.auth import APIKeyRequiredMixin, UnauthenticatedMixin
from cdrplatform.core.models import CurrencyChoices, WeightUnitChoices
from cdrplatform.core.selectors import (
    api_key_must_be_present_and_valid,
    removal_method_choices,
)
from cdrplatform.core.services import removal_request_create


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
        client_reference_id = serializers.CharField(
            required=False,
            max_length=128,
            allow_blank=True,
        )
        certificate_display_name = serializers.CharField(
            required=False,
            max_length=128,
            allow_blank=True,
        )

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
        operation_id="CDRPurchase",
        description="""Submit a request to purchase carbon dioxide removal.

By using this endpoint your organisation is committing to buy CO₂ from Climacrux LLC.

Returns a transaction ID that is unique to this removal request. This can
be stored in your records and used to retrieve the status of the request,
removal certificate

**Note:** This will not return any prices, only a transaction UUID""",
    )
    def post(self, request):
        key = request.META["HTTP_AUTHORIZATION"].split()[1]
        api_key = api_key_must_be_present_and_valid(key=key)

        input = self.InputSerializer(data=request.data)
        # We raise an exception if the data is invalid because it will be automatically
        # caught and handled by drf-standardized-errors.
        # This means it will have the same error format as every other error 👍
        if input.is_valid(raise_exception=True):

            removal_request = removal_request_create(
                weight_unit=input.validated_data.get("weight_unit"),
                currency=input.validated_data.get("currency"),
                org_id=api_key.organisation_id,
                request_items=input.validated_data.get("items"),
            )

            output = self.OutputSerializer({"transaction_uuid": removal_request.uuid})
            return Response(output.data, status=status.HTTP_201_CREATED)
