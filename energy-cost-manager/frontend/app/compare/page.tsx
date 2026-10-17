"use client";

import { FormEvent, useEffect, useState } from "react";
import api from "@/lib/api";
import Page from "@/components/Page";
import type { Comparison, Plan, Upload } from "@/lib/types";

export default function Compare() {
    const [uploads, setUploads] = useState<Upload[]>([]);
    const [plans, setPlans] = useState<Plan[]>([]);
    const [upload, setUpload] = useState("");
    const [current, setCurrent] = useState("");
    const [result, setResult] = useState<Comparison | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        Promise.all([
            api.get("/uploads/"),
            api.get("/plans/")
        ]).then(([u, p]) => {
            const ready = u.data.filter(
                (x: Upload) => x.status === "ready"
            );

            setUploads(ready);
            setPlans(p.data);

            if (ready[0]) {
                setUpload(ready[0].id);
            }
        });
    }, []);

    async function submit(e: FormEvent) {
        e.preventDefault();
        setLoading(true);

        try {
            const r = await api.post("/compare/", {
                upload_id: upload,
                current_plan_id: current || null
            });

            setResult(r.data);
        } finally {
            setLoading(false);
        }
    }

    return (
        <Page
            title="Compare plans"
            subtitle="Apply every active tariff to the selected historical usage dataset."
        >
            <form
                onSubmit={submit}
                className="card p-5 grid md:grid-cols-[1fr_1fr_auto] gap-4 items-end mb-6"
            >
                {/* Usage dataset */}
                <div>
                    <label className="label">
                        Usage dataset
                    </label>

                    <select
                        className="field"
                        value={upload}
                        onChange={(e) => setUpload(e.target.value)}
                        required
                    >
                        <option value="">Choose…</option>

                        {uploads.map((u) => (
                            <option
                                key={u.id}
                                value={u.id}
                            >
                                {u.original_name}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Current electricity plan */}
                <div>
                    <label className="label">
                        Current plan (optional, for savings)
                    </label>

                    <select
                        className="field"
                        value={current}
                        onChange={(e) => setCurrent(e.target.value)}
                    >
                        <option value="">
                            Not specified
                        </option>

                        {plans.map((p) => (
                            <option
                                key={p.id}
                                value={p.id}
                            >
                                {p.provider_name} — {p.name} —{" "}
                                {p.tariff_type === "tou"
                                    ? "Time of Use"
                                    : "Flat Rate"}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Compare button */}
                <button
                    className="btn btn-primary"
                    disabled={loading}
                >
                    {loading
                        ? "Calculating…"
                        : "Compare plans"}
                </button>
            </form>

            {result &&
    result.skipped_plans &&
    result.skipped_plans.length > 0 && (
        <div className="mb-4 rounded-xl border border-amber-200 bg-amber-50 p-4">
            <div className="font-semibold text-amber-900">
                ⚠ {result.skipped_plans.length} active{" "}
                {result.skipped_plans.length === 1
                    ? "plan could"
                    : "plans could"}{" "}
                not be calculated.
            </div>

            <div className="text-sm text-amber-800 mt-1">
                The remaining valid plans were compared normally.
            </div>

            <div className="mt-3 space-y-2">
                {result.skipped_plans.map((p) => (
                    <div
                        key={p.plan_id}
                        className="text-sm"
                    >
                        <b>
                            {p.provider} — {p.plan}
                        </b>

                        <div className="text-amber-800">
                            {p.reason}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )}


            {/* Comparison results */}
            {result && (
                <div className="card overflow-hidden">
                    <div className="p-5">
                        <h2 className="font-bold text-xl">
                            Comparison results
                        </h2>

                        <p className="muted text-sm">
                            Annual estimates are annualised from the
                            covered historical period.
                        </p>
                    </div>

                    <div className="mt-4 rounded-lg border border-blue-200 bg-blue-50 p-4">
                        <p className="text-sm font-semibold text-blue-900">
                                What does Historical Cost mean?
                        </p>

                        <p className="mt-2 text-sm leading-relaxed text-blue-800">
                            Historical cost is how much your electricity would have
                            cost under each plan during the period covered by your
                            uploaded data. It includes the cost of electricity you
                            used and the daily supply charges.
                        </p>

    <p className="mt-2 text-sm text-blue-700">
        This is an estimate based on your past electricity usage,
        not necessarily the amount you actually paid.
    </p>
</div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead className="bg-slate-50">
                                <tr>
                                    {[
                                        "Rank",
                                        "Provider / Plan",
                                        "Historical cost",
                                        "Annual estimate",
                                        "Potential saving"
                                    ].map((h) => (
                                        <th
                                            className="text-left p-3"
                                            key={h}
                                        >
                                            {h}
                                        </th>
                                    ))}
                                </tr>
                            </thead>

                            <tbody>
                                {result.results.map((x) => (
                                    <tr
                                        className="border-t"
                                        key={x.id}
                                    >
                                        {/* Rank */}
                                        <td className="p-3 font-bold">
                                            #{x.rank}
                                        </td>

                                        {/* Provider and plan */}
                                        <td className="p-3">
                                            <div className="font-semibold">
                                                {x.plan.provider_name}
                                            </div>

                                            <div className="muted">
                                                {x.plan.name}
                                            </div>

                                            <div className="text-xs mt-1">
                                                {x.plan.tariff_type === "tou"
                                                    ? "Time of Use"
                                                    : "Flat Rate"}

                                                {x.plan.plan_reference &&
                                                    ` • ${x.plan.plan_reference}`}
                                            </div>
                                        </td>

                                        {/* Historical cost */}
                                        <td className="p-3">
                                            $
                                            {Number(
                                                x.historical_cost
                                            ).toFixed(2)}
                                        </td>

                                        {/* Annual estimate */}
                                        <td className="p-3 font-semibold">
                                            $
                                            {Number(
                                                x.estimated_annual_cost
                                            ).toFixed(2)}
                                        </td>

                                        {/* Potential saving */}
                                        <td className="p-3">
                                            {x.estimated_annual_saving == null ? (
                                                "—"
                                            ) : Number(x.estimated_annual_saving) > 0 ? (
                                                <span className="font-semibold text-emerald-700">
                                                    Save $
                                                    {Number(
                                                        x.estimated_annual_saving
                                                    ).toFixed(2)}
                                                </span>
                                            ) : Number(x.estimated_annual_saving) < 0 ? (
                                                <span className="text-slate-600">
                                                    Costs $
                                                    {Math.abs(
                                                        Number(x.estimated_annual_saving)
                                                    ).toFixed(2)}{" "}
                                                    more
                                                </span>
                                            ) : (
                                                <span className="text-slate-600">
                                                    No difference
                                                </span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </Page>
    );
}