from datetime import time
from decimal import Decimal
from django.core.management.base import BaseCommand
from energy.models import EnergyProvider, EnergyPlan, TariffRate

class Command(BaseCommand):
    help="Seed demonstration providers and tariffs (fictional rates; not retail advice)."
    def handle(self,*args,**kwargs):
        data=[
            ("Southern Spark","Everyday Flat","flat","1.05",[("Flat","flat","0.3400",None,None,10)]),
            ("GreenGrid Energy","Simple Saver","flat","0.92",[("Flat","flat","0.3050",None,None,10)]),
            ("Metro Energy","Flex Time","tou","1.00",[("Off-peak","offpeak","0.2100",time(22),time(7),5),("Peak","peak","0.4300",time(16),time(21),10),("Shoulder AM","shoulder","0.3000",time(7),time(16),20),("Shoulder PM","shoulder","0.3000",time(21),time(22),20)]),
        ]
        for provider_name,plan_name,kind,supply,rates in data:
            provider,_=EnergyProvider.objects.get_or_create(name=provider_name,defaults={"active":True})
            plan,_=EnergyPlan.objects.get_or_create(provider=provider,name=plan_name,defaults={"tariff_type":kind,"daily_supply_charge":Decimal(supply),"description":"Demonstration tariff only; replace with verified plan data."})
            plan.tariff_type=kind; plan.daily_supply_charge=Decimal(supply); plan.active=True; plan.save()
            plan.rates.all().delete()
            for name,rt,price,start,end,priority in rates:
                TariffRate.objects.create(plan=plan,name=name,rate_type=rt,price_per_kwh=Decimal(price),start_time=start,end_time=end,priority=priority)
        self.stdout.write(self.style.SUCCESS("Seeded demonstration energy plans."))
