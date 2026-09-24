from rest_framework import serializers
from .models import *

class UsageUploadSerializer(serializers.ModelSerializer):
    reading_count=serializers.IntegerField(source="readings.count",read_only=True)
    class Meta: model=UsageUpload; fields=("id","file","original_name","status","error_message","start_at","end_at","total_kwh","interval_minutes","created_at","reading_count"); read_only_fields=("original_name","status","error_message","start_at","end_at","total_kwh","interval_minutes","created_at","reading_count")

class TariffRateSerializer(serializers.ModelSerializer):
    class Meta: model=TariffRate; fields="__all__"

class EnergyPlanSerializer(serializers.ModelSerializer):
    provider_name=serializers.CharField(source="provider.name",read_only=True); rates=TariffRateSerializer(many=True,read_only=True)
    class Meta: model=EnergyPlan; fields=("id","provider","provider_name","name","tariff_type","daily_supply_charge","description","effective_from","effective_to","active","rates")

class EnergyProviderSerializer(serializers.ModelSerializer):
    plans=EnergyPlanSerializer(many=True,read_only=True)
    class Meta: model=EnergyProvider; fields=("id","name","website","active","plans")

class ComparisonResultSerializer(serializers.ModelSerializer):
    plan=EnergyPlanSerializer(read_only=True)
    class Meta: model=ComparisonResult; fields=("id","plan","historical_cost","estimated_annual_cost","estimated_annual_saving","usage_cost","supply_cost","rank")

class ComparisonSerializer(serializers.ModelSerializer):
    results=ComparisonResultSerializer(many=True,read_only=True); upload_name=serializers.CharField(source="upload.original_name",read_only=True)
    class Meta: model=Comparison; fields=("id","upload","upload_name","current_plan","created_at","results")
