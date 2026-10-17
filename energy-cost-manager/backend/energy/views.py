import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from .models import *
from .serializers import *
from .services import process_upload, analytics_for_upload, create_comparison
from django.db.models import Q
from django.utils import timezone

@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def health(request): return Response({"status":"ok"})

class UsageUploadViewSet(viewsets.ModelViewSet):
    serializer_class=UsageUploadSerializer; http_method_names=["get","post","delete"]
    def get_queryset(self): return UsageUpload.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        f=self.request.FILES.get("file")
        if not f: raise ValueError("file is required")
        if not f.name.lower().endswith(".csv"): from rest_framework.exceptions import ValidationError; raise ValidationError({"file":"Only CSV files are supported."})
        obj=serializer.save(user=self.request.user,original_name=f.name,status="processing")
        try: process_upload(obj)
        except Exception: pass
    @action(detail=True,methods=["get"])
    def analytics(self,request,pk=None):
        obj=self.get_object()
        if obj.status!="ready": return Response({"detail":"Upload is not ready.","error":obj.error_message},status=400)
        return Response(analytics_for_upload(obj))

class ProviderViewSet(viewsets.ModelViewSet):
    serializer_class=EnergyProviderSerializer
    def get_queryset(self): return EnergyProvider.objects.filter(active=True).prefetch_related("plans__rates")
    def get_permissions(self): return [permissions.IsAdminUser()] if self.action in ("create","update","partial_update","destroy") else [permissions.IsAuthenticated()]

class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = EnergyPlanSerializer

    def get_queryset(self):
        today = timezone.localdate()

        return (
            EnergyPlan.objects.filter(
                active=True,
                provider__active=True
            )
            .filter(
                Q(effective_from__isnull=True) |
                Q(effective_from__lte=today)
            )
            .filter(
                Q(effective_to__isnull=True) |
                Q(effective_to__gte=today)
            )
            .select_related("provider")
            .prefetch_related("rates")
        )

    def get_permissions(self):
        if self.action in (
            "create",
            "update",
            "partial_update",
            "destroy"
        ):
            return [permissions.IsAdminUser()]

        return [permissions.IsAuthenticated()]

class ComparisonListView(generics.ListAPIView):
    serializer_class=ComparisonSerializer
    def get_queryset(self): return Comparison.objects.filter(user=self.request.user).select_related("upload","current_plan").prefetch_related("results__plan__provider","results__plan__rates")

class ComparisonDetailView(generics.RetrieveAPIView):
    serializer_class=ComparisonSerializer
    def get_queryset(self): return Comparison.objects.filter(user=self.request.user).prefetch_related("results__plan__provider","results__plan__rates")

@api_view(["POST"])
def compare(request):
    upload=get_object_or_404(UsageUpload,id=request.data.get("upload_id"),user=request.user,status="ready")
    current=None
    if request.data.get("current_plan_id"):
        current = get_object_or_404(
            EnergyPlan,
            id=request.data["current_plan_id"]
        )

    try:
        comp, skipped_plans = create_comparison(
            request.user,
            upload,
            current
        )

    except ValueError as e:
        return Response(
            {"detail": str(e)},
            status=400
        )

    data = ComparisonSerializer(comp).data

    data["skipped_plans"] = skipped_plans

    return Response(
        data,
        status=201
    )

@api_view(["GET"])
def comparison_report(request,pk):
    comp=get_object_or_404(Comparison,id=pk,user=request.user)
    response=HttpResponse(content_type="text/csv"); response["Content-Disposition"]=f'attachment; filename="comparison-{comp.id}.csv"'
    w=csv.writer(response); w.writerow(["Rank","Provider","Plan","Historical cost","Estimated annual cost","Estimated annual saving"])
    for r in comp.results.select_related("plan__provider").all(): w.writerow([r.rank,r.plan.provider.name,r.plan.name,r.historical_cost,r.estimated_annual_cost,r.estimated_annual_saving or ""])
    return response


@api_view(["GET"])
def comparison_analytics_report(request, pk):
    comp = get_object_or_404(
        Comparison,
        id=pk,
        user=request.user
    )

    upload = comp.upload

    if upload.status != "ready":
        return Response(
            {
                "detail": "Usage data is not ready for analytics."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    usage_analytics = analytics_for_upload(upload)

    response = HttpResponse(
        content_type="text/csv"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="usage-analytics-{comp.id}.csv"'
    )

    writer = csv.writer(response)

    # --------------------------------------------------
    # REPORT INFORMATION
    # --------------------------------------------------

    writer.writerow([
        "Energy Cost Manager - Usage Analytics",
        ""
    ])

    writer.writerow([
        "Usage file",
        upload.original_name
    ])

    writer.writerow([
        "Analysis created from comparison",
        comp.created_at
    ])

    writer.writerow([])

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    writer.writerow([
        "SUMMARY",
        ""
    ])

    writer.writerow([
        "Metric",
        "Value"
    ])

    writer.writerow([
        "Total consumption (kWh)",
        usage_analytics["total_kwh"]
    ])

    writer.writerow([
        "Average daily consumption (kWh)",
        usage_analytics["average_daily_kwh"]
    ])

    #peak usage hour
    peak_hours = usage_analytics["peak_hours"]
    peak_hours_text = ", ".join(
        f"{hour:02d}:00"
        for hour in peak_hours
    )

    writer.writerow([
        "Peak usage hour(s)",
        peak_hours_text
    ])

    writer.writerow([])

    # --------------------------------------------------
    # DAILY CONSUMPTION
    # --------------------------------------------------

    writer.writerow([
        "DAILY CONSUMPTION",
        ""
    ])

    writer.writerow([
        "Date",
        "Consumption (kWh)"
    ])

    for item in usage_analytics["daily"]:
        writer.writerow([
            item["date"],
            item["kwh"]
        ])

    writer.writerow([])

    # --------------------------------------------------
    # MONTHLY CONSUMPTION
    # --------------------------------------------------

    writer.writerow([
        "MONTHLY CONSUMPTION",
        ""
    ])

    writer.writerow([
        "Month",
        "Consumption (kWh)"
    ])

    for item in usage_analytics["monthly"]:
        writer.writerow([
            item["month"],
            item["kwh"]
        ])

    writer.writerow([])

    # --------------------------------------------------
    # HOURLY CONSUMPTION
    # --------------------------------------------------

    writer.writerow([
        "HOURLY CONSUMPTION",
        ""
    ])

    writer.writerow([
        "Hour",
        "Average consumption (kWh)"
    ])

    for item in usage_analytics["hourly"]:
        average = item["average_kwh"]

        writer.writerow([
            f'{item["hour"]:02d}:00',
            (
                average
                if average is not None
                else "No data"
            )
    ])

    return response