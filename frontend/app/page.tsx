"use client";
import PriceChart from "@/components/PeriodCharts";

export default function Home() {
  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center">
          Crypto Price Tracker
        </h1>
        <div className="bg-white rounded-lg shadow-lg p-6">
          <PriceChart />
        </div>
      </div>
    </main>
  );
}
