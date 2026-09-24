import csv, io
from collections import defaultdict
from datetime import datetime, timedelta
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
        try: return timezone.make_aware(datetime.strptime(raw,fmt), timezone.get_current_timezone())
        except ValueError: pass
    raise ValueError(f"Unsupported date/time: {raw}")

def _parse_usage(row):
    for h in USAGE_HEADERS:
        if row.get(h) not in (None,""):
            v=Decimal(str(row[h]).strip())
            if v < 0: raise ValueError("Negative usage is not supported")
            return v
    raise ValueError("Missing usage_kwh column")

@transaction.atomic
def process_upload(upload):
    try:
        upload.file.open("rb"); raw=upload.file.read(); upload.file.close()
        text=raw.decode("utf-8-sig")
        reader=csv.DictReader(io.StringIO(text)); reader.fieldnames=[(h or "").strip().lower() for h in (reader.fieldnames or [])]
        parsed=[]; seen=set()
        for line_no,row in enumerate(reader,start=2):
            row={(k or "").strip().lower():(v or "").strip() for k,v in row.items()}
            if not any(row.values()): continue
            try: ts=_parse_dt(row); usage=_parse_usage(row)
            except Exception as e: raise ValueError(f"Row {line_no}: {e}")
            if ts in seen: raise ValueError(f"Row {line_no}: duplicate timestamp {ts.isoformat()}")
            seen.add(ts); parsed.append((ts,usage))
        if not parsed: raise ValueError("CSV contains no usage rows")
        parsed.sort(key=lambda x:x[0])
        UsageReading.objects.bulk_create([UsageReading(upload=upload,timestamp=t,usage_kwh=u) for t,u in parsed])
        intervals=[int((parsed[i+1][0]-parsed[i][0]).total_seconds()/60) for i in range(len(parsed)-1) if parsed[i+1][0]>parsed[i][0]]
        interval=sorted(intervals)[len(intervals)//2] if intervals else None
        upload.status="ready"; upload.error_message=""; upload.start_at=parsed[0][0]; upload.end_at=parsed[-1][0]; upload.total_kwh=sum((u for _,u in parsed),Decimal("0")); upload.interval_minutes=interval
        upload.save()
    except Exception as e:
        upload.status="failed"; upload.error_message=str(e); upload.save(update_fields=["status","error_message"]); raise
    return upload

def analytics_for_upload(upload):
    readings=list(upload.readings.all())
    by_day=defaultdict(Decimal); by_month=defaultdict(Decimal); by_hour=defaultdict(Decimal); hour_count=defaultdict(int)
    for r in readings:
        local=timezone.localtime(r.timestamp)
        by_day[local.date().isoformat()]+=r.usage_kwh
        by_month[local.strftime("%Y-%m")]+=r.usage_kwh
        by_hour[local.hour]+=r.usage_kwh; hour_count[local.hour]+=1
    avg_hour={h:(by_hour[h]/hour_count[h] if hour_count[h] else Decimal("0")) for h in range(24)}
    peak_hour=max(avg_hour,key=avg_hour.get) if readings else None
    days=max(len(by_day),1)
    return {
        "total_kwh":float(upload.total_kwh), "average_daily_kwh":float(upload.total_kwh/Decimal(days)), "peak_hour":peak_hour,
        "daily":[{"date":k,"kwh":round(float(v),3)} for k,v in sorted(by_day.items())],
        "monthly":[{"month":k,"kwh":round(float(v),3)} for k,v in sorted(by_month.items())],
        "hourly":[{"hour":h,"average_kwh":round(float(avg_hour[h]),4)} for h in range(24)],
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
    local=timezone.localtime(timestamp)
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
    start=timezone.localtime(readings[0].timestamp).date(); end=timezone.localtime(readings[-1].timestamp).date(); days=(end-start).days+1
    supply_cost=Decimal(days)*plan.daily_supply_charge
    historical=usage_cost+supply_cost
    factor=Decimal("365")/Decimal(max(days,1))
    annual=(historical*factor).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
    return {"usage_cost":usage_cost.quantize(Decimal("0.01")),"supply_cost":supply_cost.quantize(Decimal("0.01")),"historical_cost":historical.quantize(Decimal("0.01")),"annual_cost":annual}

@transaction.atomic
def create_comparison(user, upload, current_plan=None):
    plans=list(EnergyPlan.objects.filter(active=True,provider__active=True).prefetch_related("rates","provider"))
    calculated=[]
    for p in plans:
        try: calculated.append((p,calculate_plan(upload,p)))
        except ValueError: continue
    if not calculated: raise ValueError("No active plans have usable tariff rates")
    current_annual=None
    if current_plan:
        match=next((c for p,c in calculated if p.id==current_plan.id),None)
        if match: current_annual=match["annual_cost"]
        else: current_annual=calculate_plan(upload,current_plan)["annual_cost"]
    calculated.sort(key=lambda x:x[1]["annual_cost"])
    comp=Comparison.objects.create(user=user,upload=upload,current_plan=current_plan)
    for i,(p,c) in enumerate(calculated,start=1):
        saving=(current_annual-c["annual_cost"]) if current_annual is not None else None
        ComparisonResult.objects.create(comparison=comp,plan=p,historical_cost=c["historical_cost"],estimated_annual_cost=c["annual_cost"],estimated_annual_saving=saving,usage_cost=c["usage_cost"],supply_cost=c["supply_cost"],rank=i)
    return comp
