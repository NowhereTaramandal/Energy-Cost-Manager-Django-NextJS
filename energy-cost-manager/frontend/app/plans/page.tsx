"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import Page from "@/components/Page";
import type { Plan } from "@/lib/types";

export default function Plans() {
    const [plans, setPlans] = useState<Plan[]>([]);

    useEffect(() => {
        api.get("/plans/").then((r) => setPlans(r.data));
    }, []);

    return (
        <Page
            title="Energy plans"
            subtitle="Electricity plans and tariff information currently available for comparison."
        >
            <div className="grid lg:grid-cols-2 xl:grid-cols-3 gap-5">
                {plans.map((p) => (
                    <div className="card p-5" key={p.id}>
                        {/* Provider */}
                        <div className="text-sm text-teal-700 font-semibold">
                            {p.provider_name}
                        </div>

                        {/* Plan name */}
                        <h2 className="text-xl font-bold">
                            {p.name}
                        </h2>

                        {/* Tariff type badge */}
                        <div className="mt-2">
                            <span className="inline-block bg-slate-100 rounded-full px-3 py-1 text-xs font-semibold">
                                {p.tariff_type === "tou"
                                    ? "Time of Use"
                                    : "Flat Rate"}
                            </span>
                        </div>

                        {/* Description */}
                        <p className="muted text-sm mt-3">
                            {p.description}
                        </p>

                        {/* Main plan information */}
                        <div className="mt-4 text-sm space-y-1">
                            <div>
                                <b>Supply charge:</b>{" "}
                                ${Number(
                                    p.daily_supply_charge
                                ).toFixed(2)}
                                /day
                            </div>

                            {p.plan_reference && (
                                <div>
                                    <b>Plan reference:</b>{" "}
                                    {p.plan_reference}
                                </div>
                            )}

                            {p.distributor && (
                                <div>
                                    <b>Distributor:</b>{" "}
                                    {p.distributor}
                                </div>
                            )}

                            {p.effective_from && (
                                <div>
                                    <b>Effective from:</b>{" "}
                                    {p.effective_from}
                                </div>
                            )}
                        </div>

                        {/* Tariff rates */}
                        <div className="mt-4 space-y-2">
                            <div className="font-semibold text-sm">
                                Usage rates
                            </div>

                            {p.rates.map((r) => (
                                <div
                                    key={r.id}
                                    className="bg-slate-50 rounded-lg p-3 text-sm flex justify-between gap-3"
                                >
                                    <span>
                                        {r.name}

                                        {r.start_time &&
                                            ` (${r.start_time.slice(
                                                0,
                                                5
                                            )}–${r.end_time?.slice(
                                                0,
                                                5
                                            )})`}
                                    </span>

                                    <b className="whitespace-nowrap">
                                        $
                                        {Number(
                                            r.price_per_kwh
                                        ).toFixed(4)}
                                        /kWh
                                    </b>
                                </div>
                            ))}
                        </div>

                        {/* Source information */}
                        {p.source_url && (
                            <div className="mt-4 pt-4 border-t text-sm">
                                <a
                                    href={p.source_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-teal-700 font-semibold hover:underline"
                                >
                                    View plan source ↗
                                </a>

                                {p.source_checked_at && (
                                    <div className="muted text-xs mt-1">
                                        Source checked:{" "}
                                        {p.source_checked_at}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </Page>
    );
}