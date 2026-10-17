from datetime import time
from decimal import Decimal

from django.core.management.base import BaseCommand

from energy.models import EnergyProvider, EnergyPlan, TariffRate


class Command(BaseCommand):
    help = "Seed controlled demonstration providers and tariffs."

    def handle(self, *args, **kwargs):
        demo_plans = [
            {
                "provider": "Southern Spark",
                "plan": "Everyday Flat",
                "tariff_type": "flat",
                "supply": "1.05",
                "rates": [
                    ("Flat", "flat", "0.3400", None, None, 10),
                ],
            },
            {
                "provider": "GreenGrid Energy",
                "plan": "Simple Saver",
                "tariff_type": "flat",
                "supply": "0.92",
                "rates": [
                    ("Flat", "flat", "0.3050", None, None, 10),
                ],
            },
            {
                "provider": "Metro Energy",
                "plan": "Flex Time",
                "tariff_type": "tou",
                "supply": "1.00",
                "rates": [
                    (
                        "Off-peak",
                        "offpeak",
                        "0.2100",
                        time(22, 0),
                        time(7, 0),
                        5,
                    ),
                    (
                        "Peak",
                        "peak",
                        "0.4300",
                        time(16, 0),
                        time(21, 0),
                        10,
                    ),
                    (
                        "Shoulder AM",
                        "shoulder",
                        "0.3000",
                        time(7, 0),
                        time(16, 0),
                        20,
                    ),
                    (
                        "Shoulder PM",
                        "shoulder",
                        "0.3000",
                        time(21, 0),
                        time(22, 0),
                        20,
                    ),
                ],
            },
        ]

        for item in demo_plans:
            provider, _ = EnergyProvider.objects.get_or_create(
                name=item["provider"],
                defaults={"active": True},
            )

            provider.active = True
            provider.save()

            plan, _ = EnergyPlan.objects.get_or_create(
                provider=provider,
                name=item["plan"],
                data_source="demo",
                defaults={
                    "tariff_type": item["tariff_type"],
                    "daily_supply_charge": Decimal(item["supply"]),
                },
            )

            plan.data_source = "demo"
            plan.tariff_type = item["tariff_type"]
            plan.daily_supply_charge = Decimal(item["supply"])
            plan.description = (
                "Controlled fictional tariff for software testing only. "
                "Not a retail electricity offer."
            )

            # Demonstration plans do not represent external market offers.
            plan.plan_reference = None
            plan.distributor = ""
            plan.source_url = ""
            plan.source_checked_at = None
            plan.effective_from = None
            plan.effective_to = None
            plan.active = True
            plan.save()

            plan.rates.all().delete()

            for name, rate_type, price, start, end, priority in item["rates"]:
                TariffRate.objects.create(
                    plan=plan,
                    name=name,
                    rate_type=rate_type,
                    price_per_kwh=Decimal(price),
                    start_time=start,
                    end_time=end,
                    priority=priority,
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Seeded controlled demonstration energy plans."
            )
        )