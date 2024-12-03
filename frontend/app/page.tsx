"use client";

import PriceChart from "@/components/PeriodCharts";

export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-2xl font-bold mb-8">Crypto Price Tracker</h1>
      <PriceChart />
    </main>
  );
}
