from django.contrib import admin

from cdrplatform.core.models import RemovalMethod, RemovalPartner


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
