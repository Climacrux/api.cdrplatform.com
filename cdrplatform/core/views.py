from django.http import HttpResponseNotFound, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers
from rest_framework.parsers import JSONParser


@csrf_exempt
def cdr_pricing(request):
    class InputSerializer(serializers.Serializer):
        weight_unit = serializers.ChoiceField(
            required=True,
            choices=(("g", "gram"), ("kg", "kilogram"), ("t", "tonne")),
        )

    if request.method == "POST":
        data = JSONParser().parse(request)
        serializer = InputSerializer(data=data)
        if serializer.is_valid():
            return JsonResponse({"message": "Hello World"})
        return JsonResponse(serializer.errors, status=400)

    return HttpResponseNotFound()
