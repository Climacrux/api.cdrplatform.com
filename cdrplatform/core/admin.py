from django.contrib import admin

from cdrplatform.core.models import (
    CurrencyConversionRate,
    CustomerOrganisation,
    RemovalMethod,
    RemovalPartner,
    RemovalRequest,
    RemovalRequestItem,
)


@admin.register(RemovalMethod)
class RemovalMethodAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(RemovalPartner)
class RemovalPartnerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "cost_per_tonne",
        "currency",
    )
    prepopulated_fields = {"slug": ("name",)}


@admin.register(CurrencyConversionRate)
class CurrencyConversionRateAdmin(admin.ModelAdmin):
    list_display = (
        "from_currency",
        "to_currency",
        "rate",
        "date_time",
    )


@admin.register(RemovalRequest)
class RemovalRequestAdmin(admin.ModelAdmin):
    list_display = (
        "weight_unit",
        "requested_datetime",
        "currency",
        "customer_organisation",
        "uuid",
        "customer_order_id",
    )


@admin.register(RemovalRequestItem)
class RemovalRequestItemAdmin(admin.ModelAdmin):
    list_display = (
        "removal_partner",
        "removal_request",
        "cdr_cost",
        "cdr_amount",
    )


@admin.register(CustomerOrganisation)
class CustomerOrganisationAdmin(admin.ModelAdmin):
    list_display = ("organisation_name",)
