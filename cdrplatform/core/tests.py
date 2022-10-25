import uuid

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    CurrencyChoices,
    CurrencyConversionRate,
    RemovalMethod,
    RemovalPartner,
)


class CDRPricingViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        CurrencyConversionRate.objects.bulk_create(
            (
                CurrencyConversionRate(
                    from_currency=CurrencyChoices.USD,
                    to_currency=CurrencyChoices.CHF,
                    rate=2.0,
                    date_time=timezone.now(),
                ),
            )
        )
        removal_method_forestation = RemovalMethod.objects.create(
            name="forestation", slug="forestation", description=""
        )
        removal_method_biooil = RemovalMethod.objects.create(
            name="bio-oil", slug="bio-oil", description=""
        )
        RemovalPartner.objects.create(
            removal_method=removal_method_forestation,
            name="eden",
            slug="eden",
            description="",
            website="example.com",
            cost_per_tonne=552,
            currency=CurrencyChoices.USD,
        )
        RemovalPartner.objects.create(
            removal_method=removal_method_biooil,
            name="charm",
            slug="charm",
            description="",
            website="example.com",
            cost_per_tonne=60000,
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
            "items": [{"method_type": "forestation", "cdr_amount": 10}],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            {
                "cost": {
                    "items": [
                        {"method_type": "forestation", "cdr_amount": 10, "cost": 11040}
                    ],
                    "removal": 11040,
                    "variable_fees": 960,
                    "total": 12000,
                },
                "currency": "chf",
                "weight_unit": "t",
            },
        )

    def test_invalid_price_request(self):
        """
        Check if we get the correct error status for invalid requst data.
        """
        url = reverse("v1:cdr_price")
        data = {
            "weight_unit": "t",
            "currency": "chf",
            "items": [{"method_type": "foo", "cdr_amount": 10}],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "type": "validation_error",
                "errors": [
                    {
                        "code": "invalid_choice",
                        "detail": '"foo" is not a valid choice.',
                        "attr": "items.0.method_type",
                    }
                ],
            },
        )

    def test_retrieve_price_multiple(self):
        """
        Ensure we can retrieve correct price successfully.
        """
        url = reverse("v1:cdr_price")
        data = {
            "weight_unit": "t",
            "currency": "chf",
            "items": [
                {"method_type": "forestation", "cdr_amount": 10},
                {"method_type": "bio-oil", "cdr_amount": 10},
            ],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            {
                "cost": {
                    "items": [
                        {"method_type": "forestation", "cdr_amount": 10, "cost": 11040},
                        {"method_type": "bio-oil", "cdr_amount": 10, "cost": 1200000},
                    ],
                    "removal": 1211040,
                    "variable_fees": 105308,
                    "total": 1316348,
                },
                "currency": "chf",
                "weight_unit": "t",
            },
        )


class CDRRemovalViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        CurrencyConversionRate.objects.bulk_create(
            (
                CurrencyConversionRate(
                    from_currency=CurrencyChoices.USD,
                    to_currency=CurrencyChoices.CHF,
                    rate=2.0,
                    date_time=timezone.now(),
                ),
            )
        )
        removal_method_forestation = RemovalMethod.objects.create(
            name="forestation", slug="forestation", description=""
        )
        removal_method_biooil = RemovalMethod.objects.create(
            name="bio-oil", slug="bio-oil", description=""
        )
        RemovalPartner.objects.create(
            removal_method=removal_method_forestation,
            name="eden",
            slug="eden",
            description="",
            website="example.com",
            cost_per_tonne=552,
            currency=CurrencyChoices.USD,
        )
        RemovalPartner.objects.create(
            removal_method=removal_method_biooil,
            name="charm",
            slug="charm",
            description="",
            website="example.com",
            cost_per_tonne=60000,
            currency=CurrencyChoices.USD,
        )
        return super().setUpTestData()

    def test_carbon_removal_request(self):
        """
        Ensure we can successfully request carbon removal.
        """
        url = reverse("v1:cdr_request")
        data = {
            "weight_unit": "t",
            "currency": "chf",
            "items": [{"method_type": "forestation", "cdr_amount": 10}],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        uuid.UUID(response.data["transaction_uuid"])

    def test_invalid_carbon_removal_request(self):
        """
        Check if we get the correct error status for invalid request data.
        """
        url = reverse("v1:cdr_request")
        data = {
            "weight_unit": "t",
            "currency": "chf",
            "items": [{"method_type": "foo", "cdr_amount": 10}],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "type": "validation_error",
                "errors": [
                    {
                        "code": "invalid_choice",
                        "detail": '"foo" is not a valid choice.',
                        "attr": "items.0.method_type",
                    }
                ],
            },
        )

    def test_multiple_carbon_removal_request(self):
        """
        Ensure we can successfully request carbon removal.
        """
        url = reverse("v1:cdr_request")
        data = {
            "weight_unit": "t",
            "currency": "chf",
            "items": [
                {"method_type": "forestation", "cdr_amount": 10},
                {"method_type": "bio-oil", "cdr_amount": 10},
            ],
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        uuid.UUID(response.data["transaction_uuid"])
