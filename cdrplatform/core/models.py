from django.db import models

# Create your models here.


class Invoice(models.Model):
    user = models.ForeignKey()
    invoice_id = models.CharField(max_length=10)
    issued_date = models.DateField()
    paid_date = models.DateField()
    fees = models.PositiveIntegerField()
    currency = models.CharField(max_length=3)


class Certificate(models.Model):
    removal_request = models.ForeignKey()
    certificate_id = models.CharField(max_length=10)
    issued_date = models.DateField()
    name = models.CharField(max_length=50)


class RemovalRequest(models.Model):
    requested_date = models.DateField()
    weight_unit = models.CharField(max_length=2)
    invoice = models.ForeignKey()
    currency = models.CharField(max_length=3)
    user = models.ForeignKey()


class ApiKey:
    key = models.CharField(max_length=30)
    user = models.ForeignKey()


class RemovalRequestItem(models.Model):
    removal_method = models.ForeignKey()
    removal_request = models.ForeignKey()
    cost = models.PositiveIntegerField()
    amount = models.PositiveIntegerField()


class PartnerCertificate(models.Model):
    partner = models.ForeignKey()
    removal_request = models.ForeignKey()
    certificate_id = models.CharField(max_length=30)
    issued_date = models.DateField()
    name = models.CharField(max_length=30)
    removal_request_item = models.ForeignKey()


class Partner(models.Model):
    removal_method = models.ForeignKey()
    name = models.CharField(max_length=30)
    description = models.TextField()
    website = models.URLField()
    cost_per_tonne = models.PositiveIntegerField()
    currency = models.CharField(max_length=3)


class RemovalMethod(models.Model):
    name = models.CharField(max_length=30)
