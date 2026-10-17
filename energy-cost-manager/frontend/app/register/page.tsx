
"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import api from "@/lib/api";

export default function Register() {
    const [f, setF] = useState({
        first_name: "",
        last_name: "",
        email: "",
        username: "",
        password: "",
        confirm_password: ""
    });

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const r = useRouter();

    const change = (k: string, v: string) =>
        setF({ ...f, [k]: v });

    async function submit(e: FormEvent) {
        e.preventDefault();

        if (loading) return;

        setError("");
        setLoading(true);

        try {
            await api.post("/auth/register/", f);

            // Registration successful — redirect to login.
            r.push("/login");

        } catch (e: any) {
            setError(
                JSON.stringify(
                    e.response?.data || "Registration failed"
                )
            );

            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen grid place-items-center p-6">
            <form
                onSubmit={submit}
                className="card p-7 w-full max-w-lg"
                aria-busy={loading}
            >
                <h1 className="text-2xl font-bold mb-5">
                    Create account
                </h1>

                {error && (
                    <p className="bg-red-50 text-red-700 p-3 rounded-lg mb-4 text-sm">
                        {error}
                    </p>
                )}

                <div className="grid grid-cols-2 gap-3">
                    <div>
                        <label className="label">
                            First name
                        </label>

                        <input
                            className="field"
                            value={f.first_name}
                            onChange={e =>
                                change("first_name", e.target.value)
                            }
                        />
                    </div>

                    <div>
                        <label className="label">
                            Last name
                        </label>

                        <input
                            className="field"
                            value={f.last_name}
                            onChange={e =>
                                change("last_name", e.target.value)
                            }
                        />
                    </div>
                </div>

                <label className="label mt-3">
                    Email
                </label>

                <input
                    className="field"
                    type="email"
                    value={f.email}
                    onChange={e =>
                        change("email", e.target.value)
                    }
                    required
                />

                <label className="label mt-3">
                    Username
                </label>

                <input
                    className="field"
                    value={f.username}
                    onChange={e =>
                        change("username", e.target.value)
                    }
                    required
                />

                <label className="label mt-3">
                    Password
                </label>

                <input
                    className="field"
                    type="password"
                    value={f.password}
                    onChange={e =>
                        change("password", e.target.value)
                    }
                    required
                />

                <label className="label mt-3">
                    Confirm password
                </label>

                <input
                    className="field mb-5"
                    type="password"
                    value={f.confirm_password}
                    onChange={e =>
                        change("confirm_password", e.target.value)
                    }
                    required
                />

                {/* Registration button with loading state */}
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
                            Creating account...
                        </>
                    ) : (
                        "Create account"
                    )}
                </button>

                <p className="text-sm mt-4">
                    Already registered?{" "}
                    <Link
                        href="/login"
                        className="text-teal-700"
                    >
                        Sign in
                    </Link>
                </p>
            </form>
        </div>
    );
}
