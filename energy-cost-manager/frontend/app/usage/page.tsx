"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import Page from "@/components/Page";
import StatCard from "@/components/StatCard";
import UsageCharts from "@/components/UsageCharts";
import type { Analytics, Upload } from "@/lib/types";
import Link from "next/link";

export default function Usage() {
    const [uploads, setUploads] = useState<Upload[]>([]);
    const [selected, setSelected] = useState("");
    const [data, setData] = useState<Analytics | null>(null);

    useEffect(() => {
        api.get("/uploads/").then((r) => {
            const ready = r.data.filter(
                (x: Upload) => x.status === "ready"
            );

            setUploads(ready);

            if (ready[0]) {
                setSelected(ready[0].id);
            }
        });
    }, []);

    useEffect(() => {
        if (selected) {
            api.get(
                `/uploads/${selected}/analytics/`
            ).then((r) => setData(r.data));
        }
    }, [selected]);

    const peakHoursText =
        data && data.peak_hours.length > 0
            ? data.peak_hours
                  .map(
                      (hour) =>
                          `${String(hour).padStart(2, "0")}:00`
                  )
                  .join(", ")
            : "—";

    return (
        <Page
            title="Usage analytics"
            subtitle="Explore consumption by day, month and hour."
        >
            <div className="card p-4 mb-5 max-w-xl">
                <label className="label">
                    Usage dataset
                </label>

                <select
                    className="field"
                    value={selected}
                    onChange={(e) =>
                        setSelected(e.target.value)
                    }
                >
                    <option value="">
                        Choose upload
                    </option>

                    {uploads.map((u) => (
                        <option
                            value={u.id}
                            key={u.id}
                        >
                            {u.original_name}
                        </option>
                    ))}
                </select>
            </div>

            {data && (
                <>
                    <div className="grid sm:grid-cols-3 gap-4 mb-5">
                        <StatCard
                            label="Total consumption"
                            value={`${data.total_kwh.toFixed(2)} kWh`}
                        />

                        <StatCard
                            label="Average daily"
                            value={`${data.average_daily_kwh.toFixed(2)} kWh`}
                        />

                        <StatCard
                            label="Peak average hour(s)"
                            value={peakHoursText}
                        />
                    </div>

                    <UsageCharts data={data} />

                    <div className="card mt-5 p-5">
                        <h3 className="font-bold mb-3">
                            Monthly totals
                        </h3>

                        <div className="grid sm:grid-cols-3 lg:grid-cols-6 gap-3">
                            {data.monthly.map((m) => (
                                <div
                                    key={m.month}
                                    className="bg-slate-50 p-3 rounded-xl"
                                >
                                    <div className="text-xs muted">
                                        {m.month}
                                    </div>

                                    <div className="font-bold">
                                        {m.kwh.toFixed(1)} kWh
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Navigate to plan comparison after analysis */}
                    <div className="card mt-5 p-5">
                        <h3 className="text-xl font-bold mb-2">
                            Your electricity usage analysis is ready!
                        </h3>

                        <p className="text-slate-600 mb-4">
                            Now that you have analysed your electricity
                            consumption, you can compare available electricity
                            plans to find the most cost-effective option
                            based on your usage.
                        </p>

                        <Link
                            href="/compare"
                            className="btn btn-primary inline-flex items-center justify-center gap-2"
                        >
                            Compare Electricity Plans →
                        </Link>
                    </div>
                </>
            )}
        </Page>
    );
}