"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import api from "@/lib/api";
import Page from "@/components/Page";
import type { Comparison } from "@/lib/types";

export default function Recommendations() {
    const [c, setC] = useState<Comparison | null>(null);

    useEffect(() => {
        api.get("/comparisons/").then((r) => {
            setC(r.data[0] || null);
        });
    }, []);

    if (!c) {
        return (
            <Page title="Recommendations">
                <div className="card p-7">
                    No comparison yet.{" "}
                    <Link
                        href="/compare"
                        className="text-teal-700 font-semibold"
                    >
                        Run a plan comparison.
                    </Link>
                </div>
            </Page>
        );
    }

    return (
        <Page
            title="Recommendations"
            subtitle="Plans are ranked by estimated annual cost using your latest historical usage comparison."
        >
            <div className="grid lg:grid-cols-3 gap-5">
                {c.results.slice(0, 3).map((x, i) => {
                    const saving =
                        x.estimated_annual_saving != null
                            ? Number(x.estimated_annual_saving)
                            : null;

                    return (
                        <div
                            key={x.id}
                            className={`card p-6 ${
                                i === 0
                                    ? "ring-2 ring-emerald-500"
                                    : ""
                            }`}
                        >
                            {/* Ranking */}
                            <div className="text-sm font-semibold text-teal-700">
                                {i === 0
                                    ? "Lowest estimated annual cost"
                                    : `#${x.rank} estimated annual cost`}
                            </div>

                            {/* Provider and plan */}
                            <h2 className="text-xl font-bold mt-1">
                                {x.plan.provider_name}
                            </h2>

                            <div>
                                {x.plan.name}
                            </div>

                            <div className="text-sm muted mt-1">
                                {x.plan.tariff_type === "tou"
                                    ? "Time of Use"
                                    : "Flat Rate"}

                                {x.plan.plan_reference &&
                                    ` • ${x.plan.plan_reference}`}
                            </div>

                            {/* Annual cost */}
                            <div className="text-3xl font-bold mt-5">
                                $
                                {Number(
                                    x.estimated_annual_cost
                                ).toFixed(2)}

                                <span className="text-sm font-normal muted">
                                    {" "}
                                    / year
                                </span>
                            </div>

                            {/* Saving explanation */}
                            {saving !== null && (
                                <div className="mt-2">
                                    {saving > 0 ? (
                                        <div className="text-emerald-700 font-semibold">
                                            Save approximately $
                                            {saving.toFixed(2)}
                                            /year compared with your
                                            selected current plan.
                                        </div>
                                    ) : saving < 0 ? (
                                        <div className="text-slate-600 font-semibold">
                                            Costs approximately $
                                            {Math.abs(saving).toFixed(2)}
                                            /year more than your
                                            selected current plan.
                                        </div>
                                    ) : (
                                        <div className="text-slate-600 font-semibold">
                                            Same estimated annual cost
                                            as your selected current plan.
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Why this result */}
                            <div className="mt-5 pt-4 border-t">
                                <div className="font-semibold text-sm">
                                    Why this result?
                                </div>

                                <p className="text-sm text-slate-600 mt-1">
                                    This estimate applies this plan&apos;s
                                    tariff rates and daily supply charge
                                    to the consumption pattern in your
                                    uploaded historical usage data, then
                                    annualises the calculated cost.
                                </p>
                            </div>

                            {/* Cost breakdown */}
                            <div className="mt-4 text-sm">
                                <div>
                                    Historical usage cost:{" "}
                                    <b>
                                        $
                                        {Number(
                                            x.usage_cost
                                        ).toFixed(2)}
                                    </b>
                                </div>

                                <div>
                                    Historical supply cost:{" "}
                                    <b>
                                        $
                                        {Number(
                                            x.supply_cost
                                        ).toFixed(2)}
                                    </b>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Method explanation */}
            <div className="card p-5 mt-5">
                <h3 className="font-bold">
                    How recommendations are determined
                </h3>

                <p className="text-sm text-slate-600 mt-2">
                    The application calculates the estimated cost of
                    each eligible electricity plan using the historical
                    consumption pattern in your selected dataset.
                    Plans are then ranked from the lowest to the highest
                    estimated annual cost. The first plan therefore
                    represents the lowest calculated annual cost among
                    the plans included in that comparison.
                </p>
            </div>

            {/* Disclaimer */}
            <div className="card p-5 mt-5 text-sm text-slate-600">
                <b>Important:</b> These results are estimates based on
                historical usage and tariff data stored in the
                application. They are not retailer quotes and may not
                include discounts, eligibility requirements, solar
                exports, controlled load charges, demand charges or
                future tariff changes.
            </div>
        </Page>
    );
}