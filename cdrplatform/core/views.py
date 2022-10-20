from django.http import JsonResponse
from rest_framework import serializers, status
from rest_framework.decorators import api_view


@api_view(("POST",))
def cdr_pricing(request):
    class BreakdownInputSerializer(serializers.Serializer):
        forestation = serializers.IntegerField(required=False)

    class InputSerializer(serializers.Serializer):
        weight_unit = serializers.ChoiceField(
            required=True,
            choices=(("g", "gram"), ("kg", "kilogram"), ("t", "tonne")),
        )
        breakdown = BreakdownInputSerializer()

    if request.method == "POST":
        serializer = InputSerializer(data=request.data)
        if serializer.is_valid():
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
