from django.db import models
from django.utils.translation import gettext_lazy as _


class Invoice(models.Model):
    user = models.ForeignKey()
    invoice_id = models.CharField(max_length=10)
    issued_date = models.DateField()
    paid_date = models.DateField()
    fees = models.PositiveIntegerField()
    currency = models.CharField(max_length=3)


class Certificate(models.Model):
    removal_request = models.ForeignKey(
        "RemovalRequest",
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
        on_delete=models.SET_NULL,
    )
    currency = models.CharField(max_length=3)
    user = models.ForeignKey()
    removal_partners = models.ManyToManyField(
        "RemovalPartner",
        through="RemovalRequestItem",
    )


class RemovalRequestItem(models.Model):
    removal_partner = models.ForeignKey(
        "RemovalPartner",
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
        on_delete=models.SET_NULL,
    )
    removal_request = models.ForeignKey(
        "RemovalRequest",
        on_delete=models.SET_NULL,
    )
    certificate_id = models.CharField(max_length=64)
    issued_date = models.DateField()
    name = models.CharField(max_length=128)
    removal_request_item = models.ForeignKey(
        "RemovalRequestItem",
        on_delete=models.SET_NULL,
    )


class RemovalPartner(models.Model):
    removal_method = models.ForeignKey(
        "RemovalMethod",
        on_delete=models.SET_NULL,
    )
    name = models.CharField(max_length=128)
    description = models.TextField()
    website = models.URLField()
    cost_per_tonne = models.PositiveIntegerField()
    currency = models.CharField(max_length=3)


class RemovalMethod(models.Model):
    name = models.CharField(max_length=128)
