"use client";

import dynamic from "next/dynamic";

const PriceTracker = dynamic(() => import("../src/components/PeriodCharts"), {
  ssr: false,
});

export default function Home() {
  return (
    <main className="min-h-screen">
      <PriceTracker />
    </main>
  );
}
