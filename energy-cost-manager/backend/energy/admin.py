from django.contrib import admin
from .models import *


class TariffRateInline(admin.TabularInline):
    model = TariffRate
    extra = 1


@admin.register(EnergyPlan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "provider",
        "data_source",
        "tariff_type",
        "daily_supply_charge",
        "plan_reference",
        "distributor",
        "active",
    )

    list_filter = (
        "data_source",
        "provider",
        "tariff_type",
        "distributor",
        "active",
    )

    search_fields = (
        "name",
        "provider__name",
        "plan_reference",
        "distributor",
    )

    inlines = [TariffRateInline]


@admin.register(EnergyProvider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "active",
    )


@admin.register(UsageUpload)
class UploadAdmin(admin.ModelAdmin):
    list_display = (
        "original_name",
        "user",
        "status",
        "total_kwh",
        "created_at",
    )

    readonly_fields = (
        "created_at",
    )


admin.site.register(UsageReading)
admin.site.register(Comparison)
admin.site.register(ComparisonResult)