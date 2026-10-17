"use client";

import { FormEvent, useEffect, useState } from "react";
import api from "@/lib/api";
import Page from "@/components/Page";
import type { Upload } from "@/lib/types";
import Link from "next/link";

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [items, setItems] = useState<Upload[]>([]);
    const [msg, setMsg] = useState("");
    const [uploadSuccess, setUploadSuccess] = useState(false);
    const [dataWarning, setDataWarning] = useState("");

    const load = () =>
        api.get("/uploads/").then((r) => setItems(r.data));

    useEffect(() => {
        load().catch(() => {});
    }, []);

    function handleFileChange(
        e: React.ChangeEvent<HTMLInputElement>
    ) {
        const selectedFile = e.target.files?.[0] || null;

        setFile(selectedFile);
        setUploadSuccess(false);
        setDataWarning("");

        if (selectedFile) {
            setMsg(
                `✓ ${selectedFile.name} selected and ready to upload.`
            );
        } else {
            setMsg("");
        }
    }

    async function submit(e: FormEvent) {
        e.preventDefault();

        if (!file) {
            return;
        }

        const fileName = file.name;

        setMsg("Uploading and processing…");
        setUploadSuccess(false);
        setDataWarning("");

        const fd = new FormData();
        fd.append("file", file);

        try {
            const r = await api.post(
                "/uploads/",
                fd,
                {
                    headers: {
                        "Content-Type": "multipart/form-data"
                    }
                }
            );

            if (r.data.status === "ready") {
                setMsg(
                    `✓ ${fileName} uploaded and processed successfully.`
                );
                setUploadSuccess(true);
                setDataWarning(r.data.data_quality_warning || "");
            } else {
                setMsg(
                    `Processing failed: ${r.data.error_message}`
                );
                setUploadSuccess(false);
            }

            await load();

        } catch (e: any) {
            setMsg(
                e.response?.data?.file ||
                "Upload failed"
            );
            setUploadSuccess(false);
        }
    }

    async function remove(id: string) {
        await api.delete(`/uploads/${id}/`);
        await load();
    }
    const isDuplicateTimestampError =
    msg.toLowerCase().includes("unique constraint failed") ||
    msg.toLowerCase().includes("duplicate timestamp");

    return (
        <Page
            title="Upload electricity usage"
            subtitle="Use a CSV containing timestamp + usage_kwh, or date + time + usage_kwh."
        >
            <div className="card p-6 mb-6">
                <form onSubmit={submit}>
                    <label className="label">
                        CSV file
                    </label>

                    <input
                        type="file"
                        accept=".csv,text/csv"
                        className="field"
                        onChange={handleFileChange}
                        required
                    />

                    {/* File selection / upload message */}
                    {msg && (
                        <div className="mt-3 text-sm font-medium">
                            {msg}
                        </div>
                    )}
                    {/* Warning for potentially incomplete CSV data */}
                    {dataWarning && (
                        <div
                            role="alert"
                            className="mt-3 rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900"
                        >
                            <p className="font-semibold mb-2">
                                ⚠ Incomplete electricity usage data
                            </p>

                            <p>{dataWarning}</p>

                            <p className="mt-2">
                                You can still analyse your electricity usage
                                and compare electricity plans. However,
                                the annual cost estimates should be treated
                                as provisional because some readings may
                                be missing.
                            </p>
                        </div>
                    )}
                    {/* Customer-friendly explanation for duplicate timestamp errors */}
                    {isDuplicateTimestampError && (
                        <div className="mt-3 rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">
                            <p className="font-semibold mb-2">
                                What does this error mean?
                            </p>

                            <p>
                                Some electricity readings have been identified
                                as having the same date and time. The system
                                requires each reading to have a unique timestamp.
                            </p>

                            <p className="mt-2">
                                This may happen because the CSV contains repeated
                                timestamps or because of daylight-saving time
                                differences.
                            </p>

                            <p className="mt-3 font-semibold">
                                What can you do?
                            </p>

                            <p>
                                Check the date and time columns in your CSV file.
                                If the readings appear correct, the file may
                                require additional timezone handling.
                            </p>
                        </div>
                    )}

                    {/* <div className="mt-4">
                        <button
                            className="btn btn-primary"
                            disabled={!file}
                        >
                            Upload & process
                        </button>
                    </div> */}
                    <div className="mt-4 flex flex-col items-start gap-3">
                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={!file}
                        >
                            Upload & process
                        </button>

                        {uploadSuccess && (
                            <Link
                                href="/usage"
                                className="btn btn-primary inline-flex items-center gap-2"
                            >
                                Go to Analytics →
                            </Link>
                        )}
                    </div>
                </form>

                <div className="bg-slate-50 rounded-xl p-4 mt-5 text-sm">
                    <div className="font-semibold">
                        Accepted example
                    </div>

                    <pre className="mt-2 overflow-x-auto">
{`date,time,usage_kwh
2026-01-01,00:00,0.32
2026-01-01,00:30,0.25`}
                    </pre>
                </div>
            </div>

            <div className="card overflow-hidden">
                <div className="p-5 font-bold">
                    Upload history
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead className="bg-slate-50">
                            <tr>
                                {[
                                    "File",
                                    "Status",
                                    "Readings",
                                    "Total kWh",
                                    "Interval",
                                    "Uploaded",
                                    ""
                                ].map((h) => (
                                    <th
                                        key={h}
                                        className="text-left p-3"
                                    >
                                        {h}
                                    </th>
                                ))}
                            </tr>
                        </thead>

                        <tbody>
                            {items.map((x) => (
                                <tr
                                    key={x.id}
                                    className="border-t"
                                >
                                    <td className="p-3">
                                        {x.original_name}
                                    </td>

                                    <td className="p-3">
                                        {x.status}
                                    </td>

                                    <td className="p-3">
                                        {x.reading_count}
                                    </td>

                                    <td className="p-3">
                                        {x.total_kwh}
                                    </td>

                                    <td className="p-3">
                                        {x.interval_minutes
                                            ? `${x.interval_minutes} min`
                                            : "—"}
                                    </td>

                                    <td className="p-3">
                                        {new Date(
                                            x.created_at
                                        ).toLocaleString()}
                                    </td>

                                    <td className="p-3">
                                        <button
                                            className="text-red-600"
                                            onClick={() =>
                                                remove(x.id)
                                            }
                                        >
                                            Delete
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </Page>
    );
}