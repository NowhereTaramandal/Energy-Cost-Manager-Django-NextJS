export type Upload={id:string;original_name:string;status:string;error_message:string;start_at:string|null;end_at:string|null;total_kwh:string;interval_minutes:number|null;created_at:string;reading_count:number};
export type Rate={id:string;name:string;rate_type:string;price_per_kwh:string;start_time:string|null;end_time:string|null;days_of_week:string;priority:number};
export type Plan={
    id:string;
    provider:string;
    provider_name:string;
    name:string;
    tariff_type:string;
    daily_supply_charge:string;
    description:string;
    effective_from:string|null;
    effective_to:string|null;
    plan_reference:string|null;
    distributor:string;
    source_url:string;
    source_checked_at:string|null;
    active:boolean;
    rates:Rate[];
};
export type Result={
    id:string;
    plan:Plan;
    plan_snapshot:PlanSnapshot;
    historical_cost:string;
    estimated_annual_cost:string;
    estimated_annual_saving:string|null;
    usage_cost:string;
    supply_cost:string;
    rank:number};


export type SkippedPlan = {
    plan_id: string;
    provider: string;
    plan: string;
    tariff_type: string;
    reason: string;
};
export type Comparison={
    id:string;
    upload:string;
    upload_name:string;
    current_plan:string|null;
    created_at:string;
    results:Result[];
    skipped_plans?:SkippedPlan[];
};
export type Analytics={total_kwh:number;average_daily_kwh:number;
    peak_hours:number[];
    daily:{
        date:string;
        kwh:number;}[];
    monthly:{
        month:string;
        kwh:number;}[];
    hourly:{
        hour:number;
        average_kwh:number| null;}[];
};

export type PlanSnapshotRate = {
    name: string;
    rate_type: string;
    price_per_kwh: string;
    start_time: string | null;
    end_time: string | null;
    days_of_week: string;
    priority: number;
};

export type PlanSnapshot = {
    provider_name: string;
    plan_name: string;
    plan_reference: string | null;
    tariff_type: string;
    daily_supply_charge: string;
    distributor: string;
    source_url: string;
    source_checked_at: string | null;
    effective_from: string | null;
    effective_to: string | null;
    rates: PlanSnapshotRate[];
};