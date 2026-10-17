"use client";

import {
    ResponsiveContainer,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
    BarChart,
    Bar
} from "recharts";

import type { Analytics } from "@/lib/types";

export default function UsageCharts({
    data
}: {
    data: Analytics;
}) {
    return (
        <div className="grid xl:grid-cols-2 gap-5">

            {/* Daily consumption chart */}
            <div className="card p-5">
                <h3 className="font-bold mb-4">
                    Daily consumption
                </h3>

                <div className="h-72">
                    <ResponsiveContainer
                        width="100%"
                        height="100%"
                    >
                        <AreaChart data={data.daily}>
                            <CartesianGrid
                                strokeDasharray="3 3"
                            />

                            <XAxis
                                dataKey="date"
                                tick={{ fontSize: 11 }}
                            />

                            <YAxis />

                            <Tooltip />

                            <Area
                                type="monotone"
                                dataKey="kwh"
                                fillOpacity={0.18}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Hourly consumption chart */}
            <div className="card p-5">
                <h3 className="font-bold mb-1">
                    Average usage by hour
                </h3>

                <p className="muted text-sm mb-4">
                    Hours without readings are shown as no data.
                </p>

                <div className="h-72">
                    <ResponsiveContainer
                        width="100%"
                        height="100%"
                    >
                        <BarChart data={data.hourly}>
                            <CartesianGrid
                                strokeDasharray="3 3"
                            />

                            <XAxis
                                dataKey="hour"
                                tickFormatter={(hour) =>
                                    `${String(hour).padStart(2, "0")}:00`
                                }
                            />

                            <YAxis />

                            <Tooltip
                                labelFormatter={(hour) =>
                                    `${String(hour).padStart(2, "0")}:00`
                                }
                                formatter={(value) => [
                                    value == null
                                        ? "No data"
                                        : `${Number(value).toFixed(3)} kWh`,
                                    "Average consumption"
                                ]}
                            />

                            <Bar
                                dataKey="average_kwh"
                                name="Average consumption"
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

        </div>
    );
}