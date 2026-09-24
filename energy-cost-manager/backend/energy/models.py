import uuid
from django.conf import settings
from django.db import models

class UUIDModel(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class Meta: abstract=True

class UsageUpload(UUIDModel):
    STATUS=(("processing","Processing"),("ready","Ready"),("failed","Failed"))
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="usage_uploads")
    file=models.FileField(upload_to="usage/%Y/%m/")
    original_name=models.CharField(max_length=255)
    status=models.CharField(max_length=20,choices=STATUS,default="processing")
    error_message=models.TextField(blank=True)
    start_at=models.DateTimeField(null=True,blank=True); end_at=models.DateTimeField(null=True,blank=True)
    total_kwh=models.DecimalField(max_digits=14,decimal_places=4,default=0)
    interval_minutes=models.PositiveIntegerField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=["-created_at"]

class UsageReading(UUIDModel):
    upload=models.ForeignKey(UsageUpload,on_delete=models.CASCADE,related_name="readings")
    timestamp=models.DateTimeField(); usage_kwh=models.DecimalField(max_digits=12,decimal_places=6)
    class Meta:
        ordering=["timestamp"]; constraints=[models.UniqueConstraint(fields=["upload","timestamp"],name="unique_upload_timestamp")]

class EnergyProvider(UUIDModel):
    name=models.CharField(max_length=150,unique=True); website=models.URLField(blank=True); active=models.BooleanField(default=True)
    def __str__(self): return self.name

class EnergyPlan(UUIDModel):
    TARIFF_TYPES=(("flat","Flat Rate"),("tou","Time of Use"))
    provider=models.ForeignKey(EnergyProvider,on_delete=models.CASCADE,related_name="plans")
    name=models.CharField(max_length=150); tariff_type=models.CharField(max_length=10,choices=TARIFF_TYPES,default="flat")
    daily_supply_charge=models.DecimalField(max_digits=10,decimal_places=4,help_text="AUD per day")
    description=models.TextField(blank=True); effective_from=models.DateField(null=True,blank=True); effective_to=models.DateField(null=True,blank=True)
    active=models.BooleanField(default=True)
    class Meta: unique_together=("provider","name")
    def __str__(self): return f"{self.provider.name} - {self.name}"

class TariffRate(UUIDModel):
    RATE_TYPES=(("flat","Flat"),("peak","Peak"),("shoulder","Shoulder"),("offpeak","Off-peak"))
    plan=models.ForeignKey(EnergyPlan,on_delete=models.CASCADE,related_name="rates")
    name=models.CharField(max_length=80); rate_type=models.CharField(max_length=12,choices=RATE_TYPES)
    price_per_kwh=models.DecimalField(max_digits=10,decimal_places=5)
    start_time=models.TimeField(null=True,blank=True); end_time=models.TimeField(null=True,blank=True)
    days_of_week=models.CharField(max_length=20,default="0,1,2,3,4,5,6",help_text="0=Monday ... 6=Sunday")
    priority=models.PositiveIntegerField(default=10)
    class Meta: ordering=["priority","start_time"]

class Comparison(UUIDModel):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="comparisons")
    upload=models.ForeignKey(UsageUpload,on_delete=models.CASCADE,related_name="comparisons")
    current_plan=models.ForeignKey(EnergyPlan,on_delete=models.SET_NULL,null=True,blank=True,related_name="current_comparisons")
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=["-created_at"]

class ComparisonResult(UUIDModel):
    comparison=models.ForeignKey(Comparison,on_delete=models.CASCADE,related_name="results")
    plan=models.ForeignKey(EnergyPlan,on_delete=models.CASCADE)
    historical_cost=models.DecimalField(max_digits=12,decimal_places=2)
    estimated_annual_cost=models.DecimalField(max_digits=12,decimal_places=2)
    estimated_annual_saving=models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    usage_cost=models.DecimalField(max_digits=12,decimal_places=2); supply_cost=models.DecimalField(max_digits=12,decimal_places=2)
    rank=models.PositiveIntegerField(default=0)
    class Meta: ordering=["rank","estimated_annual_cost"]
