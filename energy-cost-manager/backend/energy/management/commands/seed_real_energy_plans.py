from datetime import date, time
from decimal import Decimal

from django.core.management.base import BaseCommand

from energy.models import EnergyProvider, EnergyPlan, TariffRate


class Command(BaseCommand):
    help = "Seed verified real-world energy plans for case-study testing."

    def handle(self, *args, **kwargs):

        # =========================================================
        # Provider: Lumo Energy (SA)
        # =========================================================

        provider, _ = EnergyProvider.objects.get_or_create(
            name="Lumo Energy (SA)",
            defaults={
                "active": True,
                "website": "https://www.lumoenergy.com.au/",
            },
        )

        provider.active = True
        provider.save()

        # =========================================================
        # PLAN 1: Lumo Basic - Single Rate
        # Source: Australian Government Energy Made Easy
        # Distribution area: SA Power Networks
        # =========================================================

        flat_plan, flat_created = EnergyPlan.objects.update_or_create(
            provider=provider,
            plan_reference="LUM203109MRE24",
            defaults={
                "name": "Lumo Basic",
                "data_source": "real",
                "tariff_type": "flat",
                "daily_supply_charge": Decimal("1.2100"),
                "description": (
                    "Real-world residential electricity plan used for "
                    "case-study testing. Verify current availability and "
                    "eligibility before relying on the estimate."
                ),
                "distributor": "SA Power Networks",
                "source_url": (
                    "https://www.energymadeeasy.gov.au/"
                    "plan?id=LUM203109MRE&postcode=5031"
                ),
                "source_checked_at": date(2026, 9, 29),
                "effective_from": date(2026, 9, 8),
                "effective_to": None,
                "active": True,
            },
        )

        # Delete existing rates before recreating them.
        # This prevents duplicate tariff records when the command
        # is run more than once.
        flat_plan.rates.all().delete()

        TariffRate.objects.create(
            plan=flat_plan,
            name="General usage",
            rate_type="flat",
            price_per_kwh=Decimal("0.3935"),
            start_time=None,
            end_time=None,
            priority=10,
        )

        flat_action = "Created" if flat_created else "Updated"

        self.stdout.write(
            self.style.SUCCESS(
                f"{flat_action} real-world plan: "
                f"{provider.name} - {flat_plan.name} "
                f"({flat_plan.plan_reference})"
            )
        )

        # =========================================================
        # PLAN 2: Lumo Basic - Time of Use
        # Source: Australian Government Energy Made Easy
        # Distribution area: SA Power Networks
        # =========================================================

        tou_plan, tou_created = EnergyPlan.objects.update_or_create(
            provider=provider,
            plan_reference="LUM203103MRE22",
            defaults={
                "name": "Lumo Basic",
                "data_source": "real",
                "tariff_type": "tou",
                "daily_supply_charge": Decimal("1.1880"),
                "description": (
                    "Real-world residential time-of-use electricity plan "
                    "used for case-study testing. Verify current availability "
                    "and eligibility before relying on the estimate."
                ),
                "distributor": "SA Power Networks",
                "source_url": (
                    "https://www.energymadeeasy.gov.au/"
                    "plan?id=LUM203103MRE&postcode=5091"
                ),
                "source_checked_at": date(2026, 9, 29),
                "effective_from": date(2026, 9, 8),
                "effective_to": None,
                "active": True,
            },
        )

        # Delete existing TOU rates before recreating them.
        tou_plan.rates.all().delete()

        tou_rates = [
            (
                "Peak - Morning",
                "peak",
                "0.4788",
                time(6, 0),
                time(10, 0),
                10,
            ),
            (
                "Shoulder",
                "shoulder",
                "0.1818",
                time(10, 0),
                time(15, 0),
                20,
            ),
            (
                "Peak - Afternoon/Evening",
                "peak",
                "0.4788",
                time(15, 0),
                time(1, 0),
                10,
            ),
            (
                "Off-peak",
                "offpeak",
                "0.3003",
                time(1, 0),
                time(6, 0),
                30,
            ),
        ]

        for name, rate_type, price, start, end, priority in tou_rates:
            TariffRate.objects.create(
                plan=tou_plan,
                name=name,
                rate_type=rate_type,
                price_per_kwh=Decimal(price),
                start_time=start,
                end_time=end,
                priority=priority,
            )

        tou_action = "Created" if tou_created else "Updated"

        self.stdout.write(
            self.style.SUCCESS(
                f"{tou_action} real-world plan: "
                f"{provider.name} - {tou_plan.name} "
                f"({tou_plan.plan_reference})"
            )
        )

        # =========================================================
        # Finished
        # =========================================================

        self.stdout.write(
            self.style.SUCCESS(
                "Finished seeding real-world case-study energy plans."
            )
        )