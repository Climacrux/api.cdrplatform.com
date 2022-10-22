from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username="DELETED")[0]


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

    objects = UserManager()

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


class Invoice(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user),
    )
    invoice_id = models.CharField(max_length=10)
    issued_date = models.DateField()
    paid_date = models.DateField()
    fees = models.PositiveIntegerField()
    currency = models.CharField(max_length=3)


class Certificate(models.Model):
    removal_request = models.ForeignKey(
        "RemovalRequest",
        null=True,
        on_delete=models.SET_NULL,
    )
    certificate_id = models.CharField(max_length=11)
    issued_date = models.DateField()
    name = models.CharField(max_length=128)


class RemovalRequest(models.Model):
    class WeightChoices(models.TextChoices):
        GRAM = "g", _("Gram")
        KILOGRAM = "kg", _("Kilogram")
        TONNE = "t", _("Tonne")

    requested_date = models.DateField()
    weight_unit = models.CharField(
        choices=WeightChoices.choices,
        max_length=2,
    )
    invoice = models.ForeignKey(
        "Invoice",
        null=True,
        on_delete=models.SET_NULL,
    )
    currency = models.CharField(max_length=3)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET(get_sentinel_user),
    )
    removal_partners = models.ManyToManyField(
        "RemovalPartner",
        through="RemovalRequestItem",
    )


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
    cost = models.PositiveIntegerField()
    amount = models.PositiveIntegerField()


class PartnerCertificate(models.Model):
    removal_partner = models.ForeignKey(
        "RemovalPartner",
        null=True,
        on_delete=models.SET_NULL,
    )
    removal_request = models.ForeignKey(
        "RemovalRequest",
        null=True,
        on_delete=models.SET_NULL,
    )
    certificate_id = models.CharField(max_length=64)
    issued_date = models.DateField()
    name = models.CharField(max_length=128)
    removal_request_item = models.ForeignKey(
        "RemovalRequestItem",
        null=True,
        on_delete=models.SET_NULL,
    )


class RemovalPartner(models.Model):
    removal_method = models.ForeignKey(
        "RemovalMethod",
        null=True,
        on_delete=models.SET_NULL,
    )
    name = models.CharField(max_length=128)
    description = models.TextField()
    website = models.URLField()
    cost_per_tonne = models.PositiveIntegerField()
    currency = models.CharField(max_length=3)


class RemovalMethod(models.Model):
    name = models.CharField(max_length=128)
