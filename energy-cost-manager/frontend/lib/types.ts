export type Upload={id:string;original_name:string;status:string;error_message:string;start_at:string|null;end_at:string|null;total_kwh:string;interval_minutes:number|null;created_at:string;reading_count:number};
export type Rate={id:string;name:string;rate_type:string;price_per_kwh:string;start_time:string|null;end_time:string|null;days_of_week:string;priority:number};
export type Plan={id:string;provider:string;provider_name:string;name:string;tariff_type:string;daily_supply_charge:string;description:string;active:boolean;rates:Rate[]};
export type Result={id:string;plan:Plan;historical_cost:string;estimated_annual_cost:string;estimated_annual_saving:string|null;usage_cost:string;supply_cost:string;rank:number};
export type Comparison={id:string;upload:string;upload_name:string;current_plan:string|null;created_at:string;results:Result[]};
export type Analytics={total_kwh:number;average_daily_kwh:number;peak_hour:number|null;daily:{date:string;kwh:number}[];monthly:{month:string;kwh:number}[];hourly:{hour:number;average_kwh:number}[]};
