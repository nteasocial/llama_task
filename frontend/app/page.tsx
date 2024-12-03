"use client";

import { Providers } from "../src/components/Providers";
import PriceCharts from "../src/components/PeriodCharts";

export default function Home() {
  return (
    <Providers>
      <main className="min-h-screen p-8 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Crypto Price Tracker</h1>
          <PriceCharts />
        </div>
      </main>
    </Providers>
  );
}
