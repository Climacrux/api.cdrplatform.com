from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CurrencyChoices, RemovalMethod, RemovalPartner


class CDRPricingViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        removal_method = RemovalMethod.objects.create(
            name="forestation", slug="forestation", description=""
        )
        RemovalPartner.objects.create(
            removal_method=removal_method,
            name="eden",
            slug="eden",
            description="",
            website="example.com",
            cost_per_tonne=552,
            currency=CurrencyChoices.USD,
        )
        return super().setUpTestData()

    def test_retrieve_price(self):
        """
        Ensure we can successfully retrieve a price.
        """
        url = reverse("v1:cdr_price")
        data = {
            "weight_unit": "t",
            "currency": "chf",
            "items": [{"method_type": "forestation", "amount": 10}],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            {
                "cost": {
                    "items": [
                        {"method_type": "forestation", "amount": 10, "cost": 5520}
                    ],
                    "removal": 5520,
                    "variable_fees": 480,
                    "total": 6000,
                },
                "currency": "chf",
                "weight_unit": "t",
            },
        )
