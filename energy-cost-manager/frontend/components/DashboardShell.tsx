
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import {
    BarChart3,
    FileText,
    Gauge,
    History,
    Lightbulb,
    LogOut,
    Scale,
    Upload,
    User,
    WalletCards,
    Zap,
} from "lucide-react";

import { useAuth } from "./AuthProvider";

const items = [
    ["/dashboard", Gauge, "Dashboard"],
    ["/upload", Upload, "Upload CSV"],
    ["/usage", BarChart3, "Usage Analytics"],
    ["/plans", WalletCards, "Energy Plans"],
    ["/compare", Scale, "Compare Plans"],
    ["/recommendations", Lightbulb, "Recommendations"],
    ["/reports", FileText, "Reports"],
    ["/history", History, "History"],
    ["/profile", User, "Profile"],
] as const;

export default function DashboardShell({
    children,
}: {
    children: React.ReactNode;
}) {
    const path = usePathname();
    const { user, logout } = useAuth();

    return (
        <div className="min-h-screen md:flex">
            <aside className="w-full md:w-64 bg-slate-950 text-white p-5 md:min-h-screen">
                <Link
                    href="/dashboard"
                    className="flex items-center gap-2 font-bold text-lg mb-7"
                >
                    <Zap className="text-emerald-400" />
                    Energy Cost Manager
                </Link>

                <nav className="grid grid-cols-2 md:grid-cols-1 gap-1">
                    {items.map(([href, Icon, label]) => (
                        <Link
                            key={href}
                            href={href}
                            className={`flex gap-2 items-center p-2.5 rounded-lg text-sm ${
                                path === href
                                    ? "bg-emerald-600"
                                    : "hover:bg-slate-800 text-slate-300"
                            }`}
                        >
                            <Icon size={17} />
                            {label}
                        </Link>
                    ))}
                </nav>

                <div className="mt-8 pt-4 border-t border-slate-800 text-sm">
                    <div className="text-slate-400 truncate mb-2">
                        {user?.email}
                    </div>

                    <button
                        onClick={logout}
                        className="flex gap-2 items-center hover:text-emerald-300"
                    >
                        <LogOut size={16} />
                        Sign out
                    </button>
                </div>
            </aside>

            <main className="flex-1 p-5 md:p-8 max-w-[1400px] mx-auto w-full">
                {children}
            </main>
        </div>
    );
}
