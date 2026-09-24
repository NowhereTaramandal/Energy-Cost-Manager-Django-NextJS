from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from .models import EnergyProvider, EnergyPlan, TariffRate, UsageUpload
from .services import process_upload, calculate_plan

class EnergyTests(TestCase):
    def setUp(self): self.user=get_user_model().objects.create_user(username="u",email="u@example.com",password="password123")
    def test_csv_and_flat_cost(self):
        content=b"date,time,usage_kwh\n2026-01-01,00:00,1.0\n2026-01-01,00:30,2.0\n"
        up=UsageUpload.objects.create(user=self.user,file=SimpleUploadedFile("u.csv",content),original_name="u.csv")
        process_upload(up); up.refresh_from_db(); self.assertEqual(up.status,"ready"); self.assertEqual(up.total_kwh,Decimal("3.0000"))
        p=EnergyProvider.objects.create(name="P"); plan=EnergyPlan.objects.create(provider=p,name="Flat",daily_supply_charge=Decimal("1")); TariffRate.objects.create(plan=plan,name="Flat",rate_type="flat",price_per_kwh=Decimal("0.3"))
        result=calculate_plan(up,plan); self.assertEqual(result["historical_cost"],Decimal("1.90"))
