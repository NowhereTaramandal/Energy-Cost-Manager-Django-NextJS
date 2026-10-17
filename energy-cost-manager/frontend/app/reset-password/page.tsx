
"use client";

import { FormEvent, Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2 } from "lucide-react";
import api from "@/lib/api";

function ResetForm() {
    const q = useSearchParams();
    const router = useRouter();

    const [p, setP] = useState("");
    const [msg, setMsg] = useState("");
    const [loading, setLoading] = useState(false);

    async function submit(e: FormEvent) {
        e.preventDefault();

        if (loading) return;

        setMsg("");
        setLoading(true);

        try {
            // Keep the existing backend endpoint and request fields.
            await api.post("/auth/reset-password/", {
                uid: q.get("uid"),
                token: q.get("token"),
                password: p
            });

            // Redirect only when Django confirms success.
            router.replace("/login");

        } catch (e: any) {
            setMsg(
                e.response?.data?.detail ||
                "Password reset failed. Please request a new reset link."
            );
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen grid place-items-center p-6">
            <form
                onSubmit={submit}
                className="card p-7 max-w-md w-full"
                aria-busy={loading}
            >
                <h1 className="text-2xl font-bold mb-4">
                    Choose new password
                </h1>

                {msg && (
                    <p
                        role="alert"
                        className="mb-3 rounded-lg bg-red-50 p-3 text-sm text-red-700"
                    >
                        {msg}
                    </p>
                )}

                <input
                    className="field mb-4"
                    type="password"
                    minLength={8}
                    value={p}
                    onChange={(e) => setP(e.target.value)}
                    required
                    disabled={loading}
                    autoComplete="new-password"
                    aria-label="New password"
                />

                <button
                    type="submit"
                    className="btn btn-primary w-full inline-flex items-center justify-center gap-2"
                    disabled={loading}
                >
                    {loading ? (
                        <>
                            <Loader2
                                size={18}
                                className="animate-spin"
                            />
                            Resetting password...
                        </>
                    ) : (
                        "Reset password"
                    )}
                </button>
            </form>
        </div>
    );
}
export default function Reset() {
    return (
        <Suspense fallback={
            <div className="min-h-screen grid place-items-center p-6">
                <p>Loading password reset form...</p>
            </div>
        }>
            <ResetForm />
        </Suspense>
    );
}
