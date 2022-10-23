from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(("POST",))
def cdr_pricing(request):
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
            choices=(("g", "gram"), ("kg", "kilogram"), ("t", "tonne")),
        )
        items = ItemInputSerializer()

    if request.method == "POST":
        serializer = InputSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(("POST",))
def cdr_removal_request(request):
    if request.method == "POST":
        return Response({"foo": request.version})
