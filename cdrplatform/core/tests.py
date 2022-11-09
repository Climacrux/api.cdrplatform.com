import uuid
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

from cdrplatform.core.exceptions import (
    APIKeyExpiredException,
    APIKeyNotPresentOrRevoked,
)
from cdrplatform.core.selectors import (
    api_key_list_all,
    api_key_list_prod_only,
    api_key_list_test_only,
    api_key_must_be_present_and_valid,
)
from cdrplatform.core.services import api_key_create

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
            name="api-key-for-testing",
        )
        return super().setUpTestData()

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION=f"Api-Key {self.apiKey}")
        return super().setUp()


class APIKeyTestCase(APIKeyMixin, APITestCase):
    def test_api_key_generation(self):
        # We should have 1 key from the :class:`APIKeyMixin.setUp` method
        self.assertEqual(OrganisationAPIKey.objects.count(), 1)
        api_key, key = api_key_create(
            organisation=self.org, api_key_name="api-key-for-testing"
        )
        # Check the length of the keys
        self.assertEqual(len(api_key.prefix), 13)
        self.assertEqual(len(key), 46)
        self.assertEqual(OrganisationAPIKey.objects.count(), 2)
        self.assertEqual(api_key_list_all(org=self.org).count(), 2)

    def test_test_api_key_generation(self):
        api_key, key = api_key_create(
            organisation=self.org,
            api_key_name="test-api-key-for-testing",
            test_key=True,
        )
        self.assertTrue(api_key.prefix.startswith("test_"))
        self.assertTrue(key.startswith("test_"))
        # Check that both objects and test_objects returns the key is valid
        self.assertTrue(OrganisationAPIKey.test_objects.is_valid(key))
        self.assertTrue(OrganisationAPIKey.objects.is_valid(key))
        # The length of the test keys is different from the other keys
        self.assertEqual(len(api_key.prefix), 13)
        self.assertEqual(len(key), 46)
        # Check that we have one key in the database that matches our prefix
        self.assertEqual(
            OrganisationAPIKey.objects.filter(prefix=api_key.prefix).count(),
            1,
        )
        # We should have one production & one test api key
        self.assertEqual(api_key_list_prod_only(org=self.org).count(), 1)
        self.assertEqual(api_key_list_test_only(org=self.org).count(), 1)

    def test_api_key_generation_without_a_name(self):
        api_key, key = api_key_create(
            organisation=self.org,
        )
        # Check the length of the keys and an additional key
        # was created in the database
        self.assertEqual(len(api_key.prefix), 13)
        self.assertEqual(len(key), 46)
        self.assertEqual(api_key_list_all(org=self.org).count(), 2)
        self.assertEqual(api_key_list_prod_only(org=self.org).count(), 2)

    def test_api_key_generation_with_none_name(self):
        api_key, key = api_key_create(
            organisation=self.org,
            api_key_name=None,
        )
        # Check the length of the keys and an additional key
        # was created in the database
        self.assertEqual(len(api_key.prefix), 13)
        self.assertEqual(len(key), 46)
        self.assertEqual(OrganisationAPIKey.objects.count(), 2)
        # There should now be 2 api keys for the organisation
        self.assertEqual(api_key_list_all(org=self.org).count(), 2)
        self.assertEqual(api_key_list_prod_only(org=self.org).count(), 2)

    def test_api_key_does_not_exist(self):
        with self.assertRaises(APIKeyNotPresentOrRevoked):
            api_key_must_be_present_and_valid(key="this-key-should-not-exist")

    def test_api_key_is_expired(self):
        # setup an expired api key and try to retrieve it
        # setup an api key revoke it and try to retrieve it
        api_key, key = api_key_create(
            organisation=self.org,
            api_key_name="test-api-key-for-testing--expired",
        )
        self.assertFalse(api_key.has_expired)
        api_key.expiry_date = timezone.now() - timedelta(minutes=1)
        api_key.save()
        self.assertTrue(api_key.has_expired)

        with self.assertRaises(APIKeyExpiredException):
            api_key_must_be_present_and_valid(key=key)

        # There should now be 2 api keys for the organisation
        self.assertEqual(api_key_list_all(org=self.org).count(), 2)

    def test_api_key_has_been_revoked(self):
        # setup an api key revoke it and try to retrieve it
        api_key, key = api_key_create(
            organisation=self.org,
            api_key_name="test-api-key-for-testing--revoked",
        )

        self.assertFalse(api_key.revoked)
        api_key.revoked = True
        api_key.save()
        with self.assertRaises(APIKeyNotPresentOrRevoked):
            api_key_must_be_present_and_valid(key=key)

        # There should now be 2 api keys for the organisation
        self.assertEqual(api_key_list_all(org=self.org).count(), 2)


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

    def test_unknown_api_key_allowed(self):
        """API keys aren't checked on the pricing endpoint so this should pass"""
        self.client.credentials(
            HTTP_AUTHORIZATION="Api-Key im-a-key-that-does-not-exist"
        )
        url = reverse("v1:cdr_price")
        data = {
            "weight_unit": "t",
            "currency": "chf",
            "items": [{"method_type": "forestation", "cdr_amount": 10}],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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

    def test_unknown_api_key_fails(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Api-Key im-a-key-that-does-not-exist"
        )
        url = reverse("v1:cdr_request")
        data = {
            "weight_unit": "t",
            "currency": "chf",
            "items": [{"method_type": "forestation", "cdr_amount": 10}],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data,
            {
                "type": "client_error",
                "errors": [
                    {
                        "code": "authentication_failed",
                        "detail": "API Key does not exist or has been revoked",
                        "attr": None,
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
