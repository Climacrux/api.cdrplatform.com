import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from cdrplatform.core.managers import CDRUserManager


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


class PartnerConfirmation(models.Model):
    partner_purchase = models.ForeignKey(
        "PartnerPurchase",
        on_delete=models.CASCADE,
    )
    confirmation_id = models.CharField(max_length=64)
    confirmation_url = models.URLField(null=True)
    confirmation_file = models.FileField(null=True)
    confirmation_image = models.ImageField(null=True)


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


class CustomerOrganisation(models.Model):
    organisation_name = models.CharField(max_length=64)

    def __str__(self) -> str:
        return f"{self.organisation_name}"


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
    customer_order_id = models.CharField(
        max_length=128,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.uuid}"


class RemovalRequestItem(models.Model):
    removal_partner = models.ForeignKey(
        "RemovalPartner",
        null=True,
        on_delete=models.SET_NULL,
    )
    removal_request = models.ForeignKey(
        "RemovalRequest",
        on_delete=models.CASCADE,
    )
    # cost in smallest denomination of :class:`RemovalRequest` currency
    # e.g. in cents for USD; rappen for CHF etc; pence for GBP etc.
    cdr_cost = models.PositiveIntegerField()
    # amount of CDR in unit defined in related :class:`RemovalRequest`
    # e.g. 5t; 100g; 500kg; etc.
    cdr_amount = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.pk}"


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
