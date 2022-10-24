from django.contrib import admin

from cdrplatform.core.models import RemovalMethod


@admin.register(RemovalMethod)
class RemovalMethodAdmin(admin.ModelAdmin):
    pass
