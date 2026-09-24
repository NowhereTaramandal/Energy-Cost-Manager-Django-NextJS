import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from .models import *
from .serializers import *
from .services import process_upload, analytics_for_upload, create_comparison

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
    serializer_class=EnergyPlanSerializer
    def get_queryset(self): return EnergyPlan.objects.filter(active=True,provider__active=True).select_related("provider").prefetch_related("rates")
    def get_permissions(self): return [permissions.IsAdminUser()] if self.action in ("create","update","partial_update","destroy") else [permissions.IsAuthenticated()]

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
    if request.data.get("current_plan_id"): current=get_object_or_404(EnergyPlan,id=request.data["current_plan_id"])
    try: comp=create_comparison(request.user,upload,current)
    except ValueError as e: return Response({"detail":str(e)},status=400)
    return Response(ComparisonSerializer(comp).data,status=201)

@api_view(["GET"])
def comparison_report(request,pk):
    comp=get_object_or_404(Comparison,id=pk,user=request.user)
    response=HttpResponse(content_type="text/csv"); response["Content-Disposition"]=f'attachment; filename="comparison-{comp.id}.csv"'
    w=csv.writer(response); w.writerow(["Rank","Provider","Plan","Historical cost","Estimated annual cost","Estimated annual saving"])
    for r in comp.results.select_related("plan__provider").all(): w.writerow([r.rank,r.plan.provider.name,r.plan.name,r.historical_cost,r.estimated_annual_cost,r.estimated_annual_saving or ""])
    return response
