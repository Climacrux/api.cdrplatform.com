from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import WeightChoices


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
    """A base API View class for all Views to inherit from.

    Can contain any shared logic of functions.
    """


class CDRPricing(BaseAPIView):
    """Calculate a carbon dioxide removal price for a given portfolio of
    CDR items.
    """

    class InputSerializer(serializers.Serializer):
        weight_unit = serializers.ChoiceField(
            required=True,
            choices=WeightChoices.choices,
        )
        # todo: add validation on currency
        currency = serializers.CharField(min_length=3, max_length=3)
        items = ItemInputSerializer()
        # Whether or not the fees should be
        include_fees = serializers.BooleanField(
            required=False,
            default=False,
        )

    class OutputSerializer(serializers.Serializer):
        cost = serializers.IntegerField(min_value=0)
        currency = serializers.CharField(min_length=3, max_length=3)

    @extend_schema(
        request=InputSerializer,
        responses={
            status.HTTP_201_CREATED: OutputSerializer,
        },
        methods=("POST",),
    )
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(("POST",))
def cdr_removal_request(request):
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

    class InputSerializer(serializers.Serializer):
        weight_unit = serializers.ChoiceField(
            required=True,
            choices=WeightChoices.choices,
        )
        currency = serializers.CharField(min_length=3, max_length=3)
        items = ItemInputSerializer()

    class OutputSerializer(serializers.Serializer):
        request_id = serializers.UUIDField()

    if request.method == "POST":
        return Response({"foo": request.version})
