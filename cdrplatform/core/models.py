import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework_api_key.models import AbstractAPIKey
from shortuuid.django_fields import ShortUUIDField

from cdrplatform.core.managers import (
    CDRUserManager,
    ProdAPIKeyManager,
    TestAPIKeyManager,
)


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="DELETED")[0]


class WeightUnitChoices(models.TextChoices):
    GRAM = "g", _("Gram")
    KILOGRAM = "kg", _("Kilogram")
    TONNE = "t", _("Tonne")


class CurrencyChoices(models.TextChoices):
    """Specific currencies we support.

    We hard code these as they are integral to our business and if we were to
    adopt a new currency it would likely require code changes anyway."""

    CHF = "chf", "CHF"
    USD = "usd", "USD"
    GBP = "gbp", "GBP"
    EUR = "eur", "EUR"


class CDRUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(_("name"), max_length=150, blank=True)
    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _("A user with that email address already exists."),
        },
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = CDRUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class PartnerPurchase(models.Model):
    cdr_amount = models.PositiveIntegerField()
    weight_unit = models.CharField(
        choices=WeightUnitChoices.choices,
        max_length=2,
    )
    cdr_cost = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, choices=CurrencyChoices.choices)
    removal_partner = models.ForeignKey(
        "RemovalPartner",
        null=True,
        on_delete=models.SET_NULL,
    )
    invoice_id = models.CharField(max_length=64)
    ordered_date = models.DateField(null=True)
    paid_date = models.DateField(null=True)
    completed_date = models.DateField(null=True)
    invoice_file = models.FileField(null=True)

    def __str__(self) -> str:
        return (
            f"{self.cdr_amount}{self.get_weight_unit_display()}"
            + f" - {self.currency}{self.cdr_cost}"
        )


class CustomerInvoice(models.Model):
    invoice_id = models.CharField(max_length=10)
    issued_date = models.DateField()
    paid_date = models.DateField(null=True)
    fees = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, choices=CurrencyChoices.choices)
    customer_organisation = models.ForeignKey(
        "CustomerOrganisation",
        null=True,
        on_delete=models.SET_NULL,
    )
    receiver_email = models.EmailField()
    invoice_file = models.FileField(null=True)

    @property
    def is_paid(self):
        """Helper function to tell if the invoice is paid or not."""
        return self.paid_date is not None

    def __str__(self) -> str:
        return f"{self.invoice_id} - {self.issued_date.strftime('%Y/%m/%d')}"


class PartnerConfirmation(models.Model):
    partner_purchase = models.ForeignKey(
        "PartnerPurchase",
        on_delete=models.CASCADE,
    )
    confirmation_id = models.CharField(max_length=64)
    confirmation_url = models.URLField(blank=True)
    confirmation_file = models.FileField(null=True)
    confirmation_image = models.ImageField(null=True)

    def __str__(self) -> str:
        return f"{self.confirmation_id} - " + f"{self.confirmation_url}"


class RemovalPartner(models.Model):
    removal_method = models.ForeignKey(
        "RemovalMethod",
        null=True,
        on_delete=models.SET_NULL,
    )
    name = models.CharField(max_length=128)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    website = models.URLField()
    cost_per_tonne = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, choices=CurrencyChoices.choices)
    disabled = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.pk} - {self.name}"


class Certificate(models.Model):
    removal_request = models.ForeignKey(
        "RemovalRequest",
        null=True,
        on_delete=models.SET_NULL,
    )
    certificate_id = models.CharField(max_length=11)
    issued_date = models.DateField()
    display_name = models.CharField(max_length=128)

    def __str__(self) -> str:
        return (
            f"{self.certificate_id} - "
            + f"{self.display_name} - "
            + f"{self.issued_date.strftime('%Y/%m/%d')}"
        )


class CustomerOrganisation(models.Model):
    short_id = ShortUUIDField(
        length=22,
        max_length=40,
        prefix="org_",
        unique=True,
    )
    organisation_name = models.CharField(max_length=64)
    created_date = models.DateField(auto_now_add=True)
    # Organisations can have multiple users and
    # users can be part of multiple organisations
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="organisations",
    )  # look up with `user.organisations`

    class Meta:
        ordering = ("created_date",)

    def __str__(self) -> str:
        return f"{self.short_id} - {self.organisation_name}"


class RemovalMethod(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return f"{self.pk} - {self.name}"


class RemovalRequest(models.Model):
    weight_unit = models.CharField(
        choices=WeightUnitChoices.choices,
        max_length=2,
    )
    requested_datetime = models.DateTimeField(
        auto_now_add=True,  # automatically set the datetime when saving model
    )
    currency = models.CharField(max_length=3, choices=CurrencyChoices.choices)
    invoice = models.ForeignKey(
        "CustomerInvoice",
        null=True,
        on_delete=models.SET_NULL,
    )
    customer_organisation = models.ForeignKey(
        "CustomerOrganisation",
        null=True,
        on_delete=models.SET_NULL,
    )
    uuid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )

    # ##################
    # Optional metadata fields that can be provided
    # by the customer when making the request
    # ##################

    # client_reference_id - an identifier provided by the customer that can be used to
    # lookup requests in the future
    # example: e-commerce order ID where CO2 was purchased
    meta_client_reference_id = models.CharField(
        max_length=128,
        blank=True,
    )
    # a custom display name for the certificate that will be generated
    meta_certificate_display_name = models.CharField(
        max_length=128,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.uuid}"

    @property
    def removal_cost(self) -> int:
        """Helper function to sum all the request items for the
        total removal cost."""
        q = self.items.aggregate(models.Sum("cdr_cost"))
        return q["cdr_cost__sum"]

    @property
    def variable_fees(self) -> int:
        """Helper function to sum all the request items for the
        total variable_fees."""
        q = self.items.aggregate(models.Sum("variable_fees"))
        return q["variable_fees__sum"]

    @property
    def total_cost(self) -> int:
        """Helper function to sum all the request items for the
        total cost."""
        q = self.items.aggregate(
            models.Sum("variable_fees"),
            models.Sum("cdr_cost"),
        )
        return q["cdr_cost__sum"] + q["variable_fees__sum"]


class RemovalRequestItem(models.Model):
    removal_partner = models.ForeignKey(
        "RemovalPartner",
        null=True,
        on_delete=models.SET_NULL,
    )
    removal_request = models.ForeignKey(
        "RemovalRequest",
        on_delete=models.CASCADE,
        related_name="items",
        related_query_name="item",
    )
    # cost in smallest denomination of :class:`RemovalRequest` currency
    # e.g. in cents for USD; rappen for CHF etc; pence for GBP etc.
    cdr_cost = models.PositiveIntegerField()
    variable_fees = models.PositiveIntegerField()
    # amount of CDR in unit defined in related :class:`RemovalRequest`
    # e.g. 5t; 100g; 500kg; etc.
    cdr_amount = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.pk}"

    @property
    def total_cost(self) -> int:
        """Helper function to return the total cost (cdr_cost + variable_fees)
        for this item."""
        return self.cdr_cost + self.variable_fees


class CurrencyConversionRate(models.Model):
    from_currency = models.CharField(max_length=3, choices=CurrencyChoices.choices)
    to_currency = models.CharField(max_length=3, choices=CurrencyChoices.choices)
    rate = models.DecimalField(max_digits=6, decimal_places=4)
    date_time = models.DateTimeField()

    class Meta:
        ordering = ("-date_time",)

    def __str__(self) -> str:
        return (
            f"{self.from_currency} to {self.to_currency}"
            + f" - {self.date_time.strftime('%Y-%m-%d')}"
        )


class OrganisationAPIKey(AbstractAPIKey):
    """Create special API keys that are connected to a :class:`CustomerOrganisation`.

    This is how we will tie API requests to an Organisation for billing.
    """

    # prefix must be unique but if we prefix with `test_` make sure
    # we have enough characters left to have a randomly unique string
    prefix = models.CharField(max_length=13, unique=True, editable=False)
    organisation = models.ForeignKey(
        CustomerOrganisation,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )

    objects = ProdAPIKeyManager()

    # Used for interacting with Test API keys
    # e.g. OrganisationAPIKey.test_objects.create_key()
    test_objects = TestAPIKeyManager()
