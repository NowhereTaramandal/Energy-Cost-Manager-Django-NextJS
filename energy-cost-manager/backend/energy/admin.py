from django.contrib import admin
from .models import *
class TariffRateInline(admin.TabularInline): model=TariffRate; extra=1
@admin.register(EnergyPlan)
class PlanAdmin(admin.ModelAdmin):
    list_display=("name","provider","tariff_type","daily_supply_charge","active"); list_filter=("provider","tariff_type","active"); inlines=[TariffRateInline]
@admin.register(EnergyProvider)
class ProviderAdmin(admin.ModelAdmin): list_display=("name","active")
@admin.register(UsageUpload)
class UploadAdmin(admin.ModelAdmin): list_display=("original_name","user","status","total_kwh","created_at"); readonly_fields=("created_at",)
admin.site.register(UsageReading); admin.site.register(Comparison); admin.site.register(ComparisonResult)
