
"use client";

import Link from "next/link";
import { useState } from "react";
import {
  BarChart3,
  FileUp,
  Scale,
  Zap,
  Loader2,
} from "lucide-react";

export default function Home() {
  const [loadingButton, setLoadingButton] = useState<string | null>(null);

  function handleNavigation(button: string) {
    setLoadingButton(button);
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-6xl mx-auto px-6 py-8">

        {/* Header */}
        <header className="flex justify-between items-center">
          <div className="flex items-center gap-2 font-bold text-xl">
            <Zap className="text-emerald-400" />
            Energy Cost Manager
          </div>

          <div className="flex gap-3">

            {/* Sign in */}
            <Link
              href="/login"
              onClick={() => handleNavigation("signin")}
              className="btn border border-slate-700 inline-flex items-center gap-2"
            >
              {loadingButton === "signin" ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Loading...
                </>
              ) : (
                "Sign in"
              )}
            </Link>

            {/* Get started */}
            <Link
              href="/register"
              onClick={() => handleNavigation("getstarted")}
              className="btn btn-primary inline-flex items-center gap-2"
            >
              {loadingButton === "getstarted" ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Loading...
                </>
              ) : (
                "Get started"
              )}
            </Link>

          </div>
        </header>

        {/* Main section */}
        <section className="py-24 max-w-4xl">
          <div className="text-emerald-400 font-semibold mb-3">
            Electricity cost analytics
          </div>

          <h1 className="text-5xl md:text-6xl font-bold leading-tight">
            Compare energy plans using your actual usage.
          </h1>

          <p className="text-slate-300 text-xl mt-6 max-w-3xl">
            Upload interval CSV data, analyse consumption patterns,
            estimate annual costs under multiple tariffs, and see
            potential savings with a transparent calculation breakdown.
          </p>

          {/* Create account */}
          <Link
            href="/register"
            onClick={() => handleNavigation("create")}
            className="btn btn-primary mt-8 inline-flex items-center gap-2"
          >
            {loadingButton === "create" ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Loading...
              </>
            ) : (
              "Create account"
            )}
          </Link>
        </section>

        {/* Feature cards */}
        <section className="grid md:grid-cols-3 gap-5 pb-20">
          {[
            [
              FileUp,
              "Upload usage",
              "Import interval electricity CSV data with validation.",
            ],
            [
              BarChart3,
              "Understand consumption",
              "Explore daily, monthly and hourly usage patterns.",
            ],
            [
              Scale,
              "Compare plans",
              "Estimate annual cost, rank plans and calculate potential savings.",
            ],
          ].map(([Icon, title, description]: any) => (
            <div
              className="border border-slate-800 rounded-2xl p-6 bg-slate-900"
              key={title}
            >
              <Icon className="text-emerald-400 mb-4" />
              <h2 className="font-bold text-lg">{title}</h2>
              <p className="text-slate-400 mt-2">{description}</p>
            </div>
          ))}
        </section>

        {/* Footer note */}
        <p className="text-xs text-slate-500 pb-8">
          Estimates depend on the tariff data loaded into the system
          and are not a retailer quote.
        </p>

      </div>
    </main>
  );
}
