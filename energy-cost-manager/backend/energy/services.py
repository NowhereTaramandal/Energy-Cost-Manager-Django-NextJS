import csv, io
from collections import defaultdict
from datetime import datetime, timedelta, timezone as dt_timezone
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from django.db import transaction
from .models import UsageReading, Comparison, ComparisonResult, EnergyPlan

TIMESTAMP_HEADERS=("timestamp","datetime","date_time","reading_time")
USAGE_HEADERS=("usage_kwh","kwh","consumption","consumption_kwh","usage")

def _parse_dt(row):
    raw=None
    for h in TIMESTAMP_HEADERS:
        if row.get(h): raw=row[h].strip(); break
    if not raw and row.get("date"):
        raw=f"{row['date'].strip()} {row.get('time','00:00').strip()}"
    if not raw: raise ValueError("Missing timestamp/date column")
    for fmt in ("%Y-%m-%d %H:%M:%S","%Y-%m-%d %H:%M","%d/%m/%Y %H:%M:%S","%d/%m/%Y %H:%M","%Y-%m-%dT%H:%M:%S","%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=dt_timezone.utc)
        except ValueError:
            pass
    raise ValueError(f"Unsupported date/time: {raw}")

def _parse_usage(row):
    for h in USAGE_HEADERS:
        if row.get(h) not in (None,""):
            v=Decimal(str(row[h]).strip())
            if v < 0: raise ValueError("Negative usage is not supported")
            return v
    raise ValueError("Missing usage_kwh column")


def process_upload(upload):
    try:
        with transaction.atomic():
            upload.file.open("rb")
            raw = upload.file.read()
            upload.file.close()

            text = raw.decode("utf-8-sig")

            reader = csv.DictReader(io.StringIO(text))

            reader.fieldnames = [
                (h or "").strip().lower()
                for h in (reader.fieldnames or [])
            ]

            parsed = []
            seen = set()

            for line_no, row in enumerate(reader, start=2):
                row = {
                    (k or "").strip().lower(): (v or "").strip()
                    for k, v in row.items()
                }

                if not any(row.values()):
                    continue

                try:
                    ts = _parse_dt(row)
                    usage = _parse_usage(row)
                except Exception as e:
                    raise ValueError(
                        f"Row {line_no}: {e}"
                    )

                if ts in seen:
                    raise ValueError(
                        f"Row {line_no}: duplicate timestamp "
                        f"{ts.isoformat()}"
                    )

                seen.add(ts)
                parsed.append((ts, usage))

            if not parsed:
                raise ValueError(
                    "CSV contains no usage rows"
                )

            parsed.sort(key=lambda x: x[0])

            # Maximum one calendar year of electricity usage per upload
            start_date = parsed[0][0].date()
            end_date = parsed[-1][0].date()

            try:
                one_year_later = start_date.replace(year=start_date.year + 1)
            except ValueError:
                # Handle February 29 in leap years
                one_year_later = start_date.replace(
                    year=start_date.year + 1,
                    day=28
                )

            if end_date >= one_year_later:
                raise ValueError(
                    "Date range exceeded: This file contains more than "
                    "one year of electricity usage data. "
                    "Please upload a CSV covering no more than 12 months."
    )

            UsageReading.objects.bulk_create([
                UsageReading(
                    upload=upload,
                    timestamp=t,
                    usage_kwh=u
                )
                for t, u in parsed
            ])

            intervals = [
                int(
                    (
                        parsed[i + 1][0] -
                        parsed[i][0]
                    ).total_seconds() / 60
                )
                for i in range(len(parsed) - 1)
                if parsed[i + 1][0] > parsed[i][0]
            ]

            interval = (
                sorted(intervals)[len(intervals) // 2]
                if intervals
                else None
            )

            # Check for possible missing electricity readings.
            # This is a warning, not an upload error.
            missing_intervals = []

            if interval and len(intervals) >= 2:
                for i, gap in enumerate(intervals):
                    if gap > interval and gap % interval == 0:
                        missing_count = (gap // interval) - 1

                        missing_intervals.append({
                            "after": parsed[i][0].isoformat(),
                            "before": parsed[i + 1][0].isoformat(),
                            "missing_readings": missing_count,
                        })

            if missing_intervals:
                print(
                    f"WARNING: Upload {upload.id} contains "
                    f"{sum(item['missing_readings'] for item in missing_intervals)} "
                    "potentially missing electricity readings."
                )


            upload.status = "ready"
            upload.error_message = ""
            upload.start_at = parsed[0][0]
            upload.end_at = parsed[-1][0]
            upload.total_kwh = sum(
                (u for _, u in parsed),
                Decimal("0")
            )
            upload.interval_minutes = interval

            upload.save()

    except Exception as e:
        # This happens AFTER the atomic block has rolled back.
        # Therefore the failed status is saved permanently.
        upload.status = "failed"
        upload.error_message = str(e)

        upload.save(
            update_fields=[
                "status",
                "error_message"
            ]
        )

        raise

    return upload

def analytics_for_upload(upload):
    readings = list(upload.readings.all())

    by_day = defaultdict(Decimal)
    by_month = defaultdict(Decimal)
    by_hour = defaultdict(Decimal)
    hour_count = defaultdict(int)

    for reading in readings:
        local = reading.timestamp.astimezone(dt_timezone.utc)

        by_day[local.date().isoformat()] += reading.usage_kwh
        by_month[local.strftime("%Y-%m")] += reading.usage_kwh

        by_hour[local.hour] += reading.usage_kwh
        hour_count[local.hour] += 1

    # Calculate average consumption only for hours
    # where readings actually exist.
    avg_hour = {}

    for hour in range(24):
        if hour_count[hour] > 0:
            avg_hour[hour] = (
                by_hour[hour] / Decimal(hour_count[hour])
            )
        else:
            avg_hour[hour] = None

    # Find all hours tied for the highest average consumption.
    hours_with_data = {
        hour: value
        for hour, value in avg_hour.items()
        if value is not None
    }

    if hours_with_data:
        highest_average = max(hours_with_data.values())

        peak_hours = [
            hour
            for hour, value in hours_with_data.items()
            if value == highest_average
        ]
    else:
        peak_hours = []

    days = max(len(by_day), 1)

    return {
        "total_kwh": float(upload.total_kwh),

        "average_daily_kwh": float(
            upload.total_kwh / Decimal(days)
        ),

        "peak_hours": peak_hours,

        "daily": [
            {
                "date": date,
                "kwh": round(float(value), 3)
            }
            for date, value in sorted(by_day.items())
        ],

        "monthly": [
            {
                "month": month,
                "kwh": round(float(value), 3)
            }
            for month, value in sorted(by_month.items())
        ],

        "hourly": [
            {
                "hour": hour,
                "average_kwh": (
                    round(float(avg_hour[hour]), 4)
                    if avg_hour[hour] is not None
                    else None
                )
            }
            for hour in range(24)
        ],
    }

def _time_matches(rate, dt):
    days={int(x) for x in rate.days_of_week.split(",") if x.strip().isdigit()}
    if dt.weekday() not in days: return False
    if not rate.start_time or not rate.end_time: return True
    t=dt.time().replace(tzinfo=None); start=rate.start_time; end=rate.end_time
    if start <= end: return start <= t < end
    return t >= start or t < end

def rate_for(plan, timestamp):
    rates=list(plan.rates.all())
    local=timestamp.astimezone(dt_timezone.utc)
    if plan.tariff_type=="flat":
        rate=next((r for r in rates if r.rate_type=="flat"), rates[0] if rates else None)
    else:
        rate=next((r for r in rates if _time_matches(r,local)), None)
    if not rate: raise ValueError(f"Plan '{plan}' has no matching tariff for {local}")
    return rate.price_per_kwh

def calculate_plan(upload, plan):
    readings=list(upload.readings.prefetch_related().all())
    if not readings: raise ValueError("Upload has no readings")
    usage_cost=sum((r.usage_kwh*rate_for(plan,r.timestamp) for r in readings),Decimal("0"))
    start = readings[0].timestamp.astimezone(dt_timezone.utc).date()
    end = readings[-1].timestamp.astimezone(dt_timezone.utc).date()
    days = (end - start).days + 1
    supply_cost=Decimal(days)*plan.daily_supply_charge
    historical=usage_cost+supply_cost
    factor=Decimal("365")/Decimal(max(days,1))
    annual=(historical*factor).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
    return {"usage_cost":usage_cost.quantize(Decimal("0.01")),"supply_cost":supply_cost.quantize(Decimal("0.01")),"historical_cost":historical.quantize(Decimal("0.01")),"annual_cost":annual}

def validate_plan_tariffs(plan):
    rates = list(plan.rates.all())

    if not rates:
        raise ValueError(
            f"Plan '{plan}' has no tariff rates configured"
        )

    # Flat-rate plan validation
    if plan.tariff_type == "flat":
        flat_rates = [
            rate
            for rate in rates
            if rate.rate_type == "flat"
        ]

        if not flat_rates:
            raise ValueError(
                f"Plan '{plan}' has no flat tariff rate configured"
            )

        if len(flat_rates) > 1:
            raise ValueError(
                f"plan '{plan}' has multiple flat tariff rates configured"
            )

        return True

    # Time-of-use plan validation
    #
    # Start from a known Monday and move forward
    # using timedelta so dates remain valid across
    # month boundaries.
    start_date = datetime(2026, 9, 28)

    day_names = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    for weekday in range(7):
        current_date = start_date + timedelta(days=weekday)

        for hour in range(24):
            for minute in (0, 30):
                test_dt = current_date.replace(
                    hour=hour,
                    minute=minute
                )

                matching_rates = [
                    rate
                    for rate in rates
                    if _time_matches(rate, test_dt)
                ]

                if not matching_rates:
                    raise ValueError(
                        f"Plan '{plan}' has no tariff coverage "
                        f"for {day_names[weekday]} "
                        f"at {hour:02d}:{minute:02d}"
                    )

    return True

def plan_is_currently_effective(plan):
    today = timezone.localdate()

    if plan.effective_from and plan.effective_from > today:
        return False

    if plan.effective_to and plan.effective_to < today:
        return False

    return True


def build_plan_snapshot(plan):
    return {
        "provider_name": plan.provider.name,
        "plan_name": plan.name,
        "plan_reference": plan.plan_reference,
        "tariff_type": plan.tariff_type,
        "daily_supply_charge": str(plan.daily_supply_charge),
        "distributor": plan.distributor,
        "source_url": plan.source_url,
        "source_checked_at": (
            plan.source_checked_at.isoformat()
            if plan.source_checked_at
            else None
        ),
        "effective_from": (
            plan.effective_from.isoformat()
            if plan.effective_from
            else None
        ),
        "effective_to": (
            plan.effective_to.isoformat()
            if plan.effective_to
            else None
        ),
        "rates": [
            {
                "name": rate.name,
                "rate_type": rate.rate_type,
                "price_per_kwh": str(rate.price_per_kwh),
                "start_time": (
                    rate.start_time.isoformat()
                    if rate.start_time
                    else None
                ),
                "end_time": (
                    rate.end_time.isoformat()
                    if rate.end_time
                    else None
                ),
                "days_of_week": rate.days_of_week,
                "priority": rate.priority,
            }
            for rate in plan.rates.all()
        ],
    }

@transaction.atomic
def create_comparison(user, upload, current_plan=None):
    plans = list(
        EnergyPlan.objects.filter(
            active=True,
            provider__active=True
        ).select_related(
            "provider"
        ).prefetch_related(
            "rates"
        )
    )

    calculated = []
    skipped_plans = []

    for plan in plans:
        if not plan_is_currently_effective(plan):
            skipped_plans.append({
                "plan_id": str(plan.id),
                "provider": plan.provider.name,
                "plan": plan.name,
                "tariff_type": plan.tariff_type,
                "reason": "Plan is outside its effective date range.",
            })
            continue

        try:
            validate_plan_tariffs(plan)
            calculation = calculate_plan(
                upload,
                plan
            )

            calculated.append(
                (plan, calculation)
            )

        except ValueError as e:
            skipped_plans.append({
                "plan_id": str(plan.id),
                "provider": plan.provider.name,
                "plan": plan.name,
                "tariff_type": plan.tariff_type,
                "reason": str(e),
            })

    if not calculated:
        raise ValueError(
            "No active plans have usable tariff rates"
        )

    current_annual = None

    if current_plan:
        match = next(
            (
                calculation
                for plan, calculation in calculated
                if plan.id == current_plan.id
            ),
            None
        )

        if match:
            current_annual = match["annual_cost"]

        else:
            validate_plan_tariffs(current_plan)
            current_annual = calculate_plan(
                upload,
                current_plan
            )["annual_cost"]

    calculated.sort(
        key=lambda x: x[1]["annual_cost"]
    )

    comp = Comparison.objects.create(
        user=user,
        upload=upload,
        current_plan=current_plan
    )

    for rank, (plan, calculation) in enumerate(
        calculated,
        start=1
    ):
        saving = (
            current_annual - calculation["annual_cost"]
            if current_annual is not None
            else None
        )

        ComparisonResult.objects.create(
            comparison=comp,
            plan=plan,
            plan_snapshot= build_plan_snapshot(plan),
            historical_cost=calculation["historical_cost"],
            estimated_annual_cost=calculation["annual_cost"],
            estimated_annual_saving=saving,
            usage_cost=calculation["usage_cost"],
            supply_cost=calculation["supply_cost"],
            rank=rank
        )

    return comp, skipped_plans