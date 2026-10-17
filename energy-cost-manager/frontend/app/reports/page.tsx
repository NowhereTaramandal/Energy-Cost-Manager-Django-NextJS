"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import Page from "@/components/Page";
import type { Comparison } from "@/lib/types";

export default function Reports() {
    const [items, setItems] = useState<Comparison[]>([]);

    useEffect(() => {
        api.get("/comparisons/").then((r) => {
            setItems(r.data);
        });
    }, []);


async function downloadAnalytics(id: string) {
    const r = await api.get(
        `/comparisons/${id}/analytics.csv`,
        {
            responseType: "blob"
        }
    );

    const url = URL.createObjectURL(r.data);
    const a = document.createElement("a");

    a.href = url;
    a.download = `usage-analytics-${id}.csv`;

    a.click();

    URL.revokeObjectURL(url);
}

    return (
        <Page
            title="Reports"
            subtitle="Review saved plan comparisons and download usage analytics reports."
        >
            {items.length === 0 ? (
                <div className="card p-6">
                    No comparison reports are available yet.
                </div>
            ) : (
                <div className="card overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead className="bg-slate-50">
                                <tr>
                                    <th className="text-left p-3">
                                        Created
                                    </th>

                                    <th className="text-left p-3">
                                        Usage file
                                    </th>

                                    <th className="text-left p-3">
                                        Plans compared
                                    </th>

                                    <th className="text-left p-3">
                                        Lowest estimated cost
                                    </th>

                                    <th className="text-left p-3">
                                        Annual estimate
                                    </th>

                                    <th className="text-left p-3">
                                        Potential saving
                                    </th>

                                    <th className="p-3"></th>
                                </tr>
                            </thead>

                            <tbody>
                                {items.map((comparison) => {
                                    const best =
                                        comparison.results[0];

                                    const saving =
                                        best?.estimated_annual_saving !=
                                        null
                                            ? Number(
                                                  best.estimated_annual_saving
                                              )
                                            : null;

                                    return (
                                        <tr
                                            className="border-t"
                                            key={comparison.id}
                                        >
                                            <td className="p-3">
                                                {new Date(
                                                    comparison.created_at
                                                ).toLocaleString()}
                                            </td>

                                            <td className="p-3">
                                                {
                                                    comparison.upload_name
                                                }
                                            </td>

                                            <td className="p-3">
                                                {
                                                    comparison.results
                                                        .length
                                                }
                                            </td>

                                            <td className="p-3">
                                                {best ? (
                                                    <>
                                                        <div className="font-semibold">
                                                            {
                                                                best.plan
                                                                    .provider_name
                                                            }
                                                        </div>

                                                        <div className="muted">
                                                            {
                                                                best.plan
                                                                    .name
                                                            }
                                                        </div>

                                                        <div className="text-xs muted">
                                                            {best.plan
                                                                .tariff_type ===
                                                            "tou"
                                                                ? "Time of Use"
                                                                : "Flat Rate"}

                                                            {best.plan
                                                                .plan_reference &&
                                                                ` • ${best.plan.plan_reference}`}
                                                        </div>
                                                    </>
                                                ) : (
                                                    "—"
                                                )}
                                            </td>

                                            <td className="p-3 font-semibold">
                                                {best
                                                    ? `$${Number(
                                                          best.estimated_annual_cost
                                                      ).toFixed(2)}`
                                                    : "—"}
                                            </td>

                                            <td className="p-3">
                                                {saving === null ? (
                                                    "—"
                                                ) : saving > 0 ? (
                                                    <span className="text-emerald-700 font-semibold">
                                                        Save $
                                                        {saving.toFixed(
                                                            2
                                                        )}
                                                    </span>
                                                ) : saving < 0 ? (
                                                    <span className="text-slate-600">
                                                        Costs $
                                                        {Math.abs(
                                                            saving
                                                        ).toFixed(2)}{" "}
                                                        more
                                                    </span>
                                                ) : (
                                                    <span className="text-slate-600">
                                                        No difference
                                                    </span>
                                                )}
                                            </td>

                                            <td className="p-3 text-right">
                                                <div className="flex justify-end gap-2">
                                                    <button
                                                        className="btn btn-secondary"
                                                        onClick={() =>
                                                            downloadAnalytics(comparison.id)
                                                        }
                                                    >
                                                        Download Usage Analytics CSV
                                                    </button>

                                                </div>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            <div className="card p-5 mt-5 text-sm text-slate-600">
                <b>About these reports:</b> Each report represents a
                saved comparison using the historical usage dataset and
                electricity plan information available when the
                comparison was performed. Annual costs are estimates
                based on the covered historical usage period.
            </div>
        </Page>
    );
}