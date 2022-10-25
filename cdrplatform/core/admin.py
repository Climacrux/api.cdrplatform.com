from django.contrib import admin

from cdrplatform.core.models import (
    CurrencyConversionRate,
    RemovalMethod,
    RemovalPartner,
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
