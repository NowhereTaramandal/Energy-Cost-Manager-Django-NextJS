"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const { login } = useAuth();
    const router = useRouter();

    async function submit(e: FormEvent) {
        e.preventDefault();

        // Prevent accidental double submission
        if (loading) return;

        setError("");
        setLoading(true);

        try {
            await login(email, password);

            router.push("/dashboard");
        } catch {
            setError("Invalid email or password.");
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen grid place-items-center p-6">
            <form
                onSubmit={submit}
                className="card p-7 w-full max-w-md"
            >
                <h1 className="text-2xl font-bold">
                    Sign in
                </h1>

                <p className="muted mt-1 mb-5">
                    Continue to Energy Cost Manager
                </p>

                {error && (
                    <p className="bg-red-50 text-red-700 p-3 rounded-lg mb-4">
                        {error}
                    </p>
                )}

                <label className="label">
                    Email
                </label>

                <input
                    className="field mb-4"
                    type="email"
                    value={email}
                    onChange={(e) =>
                        setEmail(e.target.value)
                    }
                    disabled={loading}
                    required
                />

                <label className="label">
                    Password
                </label>

                <input
                    className="field mb-4"
                    type="password"
                    value={password}
                    onChange={(e) =>
                        setPassword(e.target.value)
                    }
                    disabled={loading}
                    required
                />

                <button
                    type="submit"
                    className="btn btn-primary w-full flex items-center justify-center gap-2"
                    disabled={loading}
                >
                    {loading && (
                        <span
                            className="
                                w-4
                                h-4
                                border-2
                                border-white
                                border-t-transparent
                                rounded-full
                                animate-spin
                            "
                        />
                    )}

                    {loading
                        ? "Signing in..."
                        : "Sign in"}
                </button>

                <div className="flex justify-between text-sm mt-4">
                    <Link
                        href="/register"
                        className="text-teal-700"
                    >
                        Create account
                    </Link>

                    <Link
                        href="/forgot-password"
                        className="text-teal-700"
                    >
                        Forgot password?
                    </Link>
                </div>
            </form>
        </div>
    );
}