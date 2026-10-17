from rest_framework import serializers
from .models import *

class UsageUploadSerializer(serializers.ModelSerializer):
    reading_count = serializers.IntegerField(
        source="readings.count",
        read_only=True
    )

    data_quality_warning = serializers.SerializerMethodField()

    class Meta:
        model = UsageUpload
        fields = (
            "id",
            "file",
            "original_name",
            "status",
            "error_message",
            "start_at",
            "end_at",
            "total_kwh",
            "interval_minutes",
            "created_at",
            "reading_count",
            "data_quality_warning",
        )

        read_only_fields = (
            "original_name",
            "status",
            "error_message",
            "start_at",
            "end_at",
            "total_kwh",
            "interval_minutes",
            "created_at",
            "reading_count",
            "data_quality_warning",
        )

    def get_data_quality_warning(self, obj):
        if obj.status != "ready":
            return None

        timestamps = list(
            obj.readings.order_by("timestamp").values_list(
                "timestamp", flat=True
            )
        )

        if len(timestamps) < 3:
            return None

        gaps = [
            int((timestamps[i + 1] - timestamps[i]).total_seconds() / 60)
            for i in range(len(timestamps) - 1)
        ]

        interval = sorted(gaps)[len(gaps) // 2]

        if interval <= 0:
            return None

        missing_count = sum(
            (gap // interval) - 1
            for gap in gaps
            if gap > interval and gap % interval == 0
        )

        if missing_count:
            return (
                f"Warning: Your electricity usage data may contain "
                f"{missing_count} missing reading(s). "
                "Annual cost estimates may be less accurate."
            )

        return None

class TariffRateSerializer(serializers.ModelSerializer):
    class Meta: model=TariffRate; fields="__all__"

class EnergyPlanSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(
        source="provider.name",
        read_only=True
    )
    rates = TariffRateSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = EnergyPlan
        fields = (
            "id",
            "provider",
            "provider_name",
            "name",
            "tariff_type",
            "daily_supply_charge",
            "description",
            "effective_from",
            "effective_to",
            "plan_reference",
            "distributor",
            "source_url",
            "source_checked_at",
            "active",
            "rates",
        )
class EnergyProviderSerializer(serializers.ModelSerializer):
    plans=EnergyPlanSerializer(many=True,read_only=True)
    class Meta: model=EnergyProvider; fields=("id","name","website","active","plans")

class ComparisonResultSerializer(serializers.ModelSerializer):
    plan=EnergyPlanSerializer(read_only=True)
    class Meta:
        model = ComparisonResult
        fields = (
            "id",
            "plan",
            "plan_snapshot",
            "historical_cost",
            "estimated_annual_cost",
            "estimated_annual_saving",
            "usage_cost",
            "supply_cost",
            "rank",
        )

class ComparisonSerializer(serializers.ModelSerializer):
    results=ComparisonResultSerializer(many=True,read_only=True); upload_name=serializers.CharField(source="upload.original_name",read_only=True)
    class Meta: model=Comparison; fields=("id","upload","upload_name","current_plan","created_at","results")
