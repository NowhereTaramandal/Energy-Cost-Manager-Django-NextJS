"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import Page from "@/components/Page";
import type { Comparison } from "@/lib/types";

export default function History() {
    const [items, setItems] = useState<Comparison[]>([]);

    useEffect(() => {
        api.get("/comparisons/").then((r) => {
            setItems(r.data);
        });
    }, []);

    return (
        <Page
            title="Comparison history"
            subtitle="Review previously calculated electricity plan comparisons."
        >
            <div className="space-y-4">
                {items.map((comparison) => {
                    const best = comparison.results[0];

                    return (
                        <div
                            className="card p-5"
                            key={comparison.id}
                        >
                            <div className="flex justify-between gap-4">
                                <div>
                                    <div className="font-bold">
                                        {comparison.upload_name}
                                    </div>

                                    <div className="text-sm muted">
                                        {new Date(
                                            comparison.created_at
                                        ).toLocaleString()}
                                    </div>
                                </div>

                                <div className="text-right">
                                    <div className="text-sm muted">
                                        Lowest estimated annual cost
                                    </div>

                                    <div className="font-bold">
                                        {best
                                            ? `$${Number(
                                                  best.estimated_annual_cost
                                              ).toFixed(2)}`
                                            : "—"}
                                    </div>
                                </div>
                            </div>

                            <div className="mt-4 grid sm:grid-cols-3 gap-2">
                                {comparison.results
                                    .slice(0, 3)
                                    .map((result) => {
                                        const snapshot =
                                            result.plan_snapshot;

                                        const hasSnapshot =
                                            snapshot &&
                                            snapshot.provider_name &&
                                            snapshot.plan_name;

                                        const providerName =
                                            hasSnapshot
                                                ? snapshot.provider_name
                                                : result.plan
                                                      .provider_name;

                                        const planName =
                                            hasSnapshot
                                                ? snapshot.plan_name
                                                : result.plan.name;

                                        const tariffType =
                                            hasSnapshot
                                                ? snapshot.tariff_type
                                                : result.plan
                                                      .tariff_type;

                                        const planReference =
                                            hasSnapshot
                                                ? snapshot.plan_reference
                                                : result.plan
                                                      .plan_reference;

                                        return (
                                            <div
                                                key={result.id}
                                                className="bg-slate-50 rounded-lg p-3 text-sm"
                                            >
                                                <div className="font-bold">
                                                    #{result.rank}{" "}
                                                    {providerName}
                                                </div>

                                                <div>
                                                    {planName}
                                                </div>

                                                <div className="text-xs muted mt-1">
                                                    {tariffType ===
                                                    "tou"
                                                        ? "Time of Use"
                                                        : "Flat Rate"}

                                                    {planReference &&
                                                        ` • ${planReference}`}
                                                </div>

                                                <div className="font-semibold mt-2">
                                                    $
                                                    {Number(
                                                        result.estimated_annual_cost
                                                    ).toFixed(
                                                        2
                                                    )}
                                                    /yr
                                                </div>
                                            </div>
                                        );
                                    })}
                            </div>
                        </div>
                    );
                })}

                {!items.length && (
                    <div className="card p-6 muted">
                        No comparisons yet.
                    </div>
                )}
            </div>
        </Page>
    );
}