import uuid

from django.urls import reverse
from django.utils import timezone
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    CurrencyChoices,
    CurrencyConversionRate,
    CustomerOrganisation,
    OrganisationAPIKey,
    RemovalRequest,
)

fake = Faker()


class APIKeyMixin:
    """Our API needs an API Key so use this mixin
    to have the functionality setup and configured."""

    @classmethod
    def setUpTestData(cls) -> None:
        cls.org = CustomerOrganisation.objects.create(
            organisation_name=fake.company(),
        )

        # Create and save an API Key on the class to use later
        _, cls.apiKey = OrganisationAPIKey.objects.create_key(
            organisation=cls.org,
            name="test-api-key",
        )
        return super().setUpTestData()

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Api-Key {self.apiKey}")
        return super().setUp()


class CDRPricingViewTestCase(APIKeyMixin, APITestCase):

    fixtures = ("removal_methods_partners", "currency_conversion_rates")

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
        return super().setUpTestData()

    def test_disabled_partner(self):
        """
        Ensure requesting the price of disabled partners is not possible.
        """
        url = reverse("v1:cdr_price")
        data = {
            "weight_unit": "t",
            "currency": "chf",
            "items": [{"method_type": "dacs", "cdr_amount": 10}],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "type": "validation_error",
                "errors": [
                    {
                        "code": "invalid_choice",
                        "detail": '"dacs" is not a valid choice.',
                        "attr": "items.0.method_type",
                    }
                ],
            },
        )

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
        response = self.client.post(url, data)
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
        Check if we get the correct error status for invalid request data.
        """
        url = reverse("v1:cdr_price")
        data = {
            "weight_unit": "t",
            "currency": "chf",
            "items": [{"method_type": "foo", "cdr_amount": 10}],
        }
        response = self.client.post(url, data)
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
        response = self.client.post(url, data)
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


class CDRRemovalViewTestCase(APIKeyMixin, APITestCase):

    fixtures = ("removal_methods_partners", "currency_conversion_rates")

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
        return super().setUpTestData()

    def test_disabled_partner(self):
        """
        Ensure requesting the removal of disabled partners is not possible.
        """
        url = reverse("v1:cdr_price")
        data = {
            "weight_unit": "t",
            "currency": "chf",
            "items": [{"method_type": "dacs", "cdr_amount": 10}],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data,
            {
                "type": "validation_error",
                "errors": [
                    {
                        "code": "invalid_choice",
                        "detail": '"dacs" is not a valid choice.',
                        "attr": "items.0.method_type",
                    }
                ],
            },
        )

    def test_carbon_removal_request(self):
        """
        Ensure we can successfully request carbon removal.
        """

        removal_requests = RemovalRequest.objects.filter(customer_organisation=self.org)
        self.assertEqual(removal_requests.count(), 0)

        url = reverse("v1:cdr_request")
        data = {
            "weight_unit": "t",
            "currency": "chf",
            "items": [{"method_type": "forestation", "cdr_amount": 10}],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        uuid.UUID(
            response.data["transaction_uuid"]
        )  # this will raise an exception if not a valid UUID

        # We should have created one removal request for our org
        removal_requests = RemovalRequest.objects.filter(customer_organisation=self.org)
        self.assertEqual(removal_requests.count(), 1)

        # The request should have stored the correct cdr amount, cost and variable fees
        removal_request = removal_requests[0]
        self.assertEqual(removal_request.removal_cost, 11040)
        self.assertEqual(removal_request.variable_fees, 960)
        self.assertEqual(removal_request.total_cost, 12000)

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
        response = self.client.post(url, data)
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
        # This should not have created a removal request for our org
        removal_requests = RemovalRequest.objects.filter(customer_organisation=self.org)
        self.assertEqual(removal_requests.count(), 0)

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
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        transaction_uuid = uuid.UUID(
            response.data["transaction_uuid"]
        )  # this will raise an exception if not a valid UUID

        removal_requests = RemovalRequest.objects.filter(customer_organisation=self.org)
        # Check the UUID matches
        self.assertEqual(removal_requests.first().uuid, transaction_uuid)
        # We should have created one removal request for our org
        self.assertEqual(removal_requests.count(), 1)
        # The request should have stored the correct cdr amount, cost and variable fees
        removal_request = removal_requests[0]
        self.assertEqual(removal_request.removal_cost, 1211040)
        self.assertEqual(removal_request.variable_fees, 105308)
        self.assertEqual(removal_request.total_cost, 1316348)

        # Send another request and check we have the correct number of requests
        response = self.client.post(url, data)
        removal_requests = RemovalRequest.objects.filter(customer_organisation=self.org)
        self.assertEqual(removal_requests.count(), 2)
