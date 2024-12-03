"use client";

import React from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/Card";
import { useQuery } from "@apollo/client";
import dynamic from "next/dynamic";
import { Skeleton } from "../components/ui/Skeleton";
import { CRYPTO_PRICES_QUERY } from "@/lib/graphql";

const ReactECharts = dynamic(() => import("echarts-for-react"), {
  ssr: false,
  loading: () => <Skeleton className="w-full h-96" />,
});

const PriceChart = () => {
  const { loading, error, data } = useQuery(CRYPTO_PRICES_QUERY, {
    pollInterval: 60000,
  });

  if (loading) return <Skeleton className="w-full h-96" />;
  if (error)
    return (
      <div className="text-red-500">Error loading data: {error.message}</div>
    );

  const chartOptions = {
    // ... rest of your chart options
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Cryptocurrency Prices</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-96">
          <ReactECharts
            option={chartOptions}
            style={{ height: "100%", width: "100%" }}
          />
        </div>
        <div className="mt-4 text-sm text-gray-500">
          Last updated:{" "}
          {new Date(data.cryptocurrencies[0].lastUpdated).toLocaleString()}
        </div>
      </CardContent>
    </Card>
  );
};

export default PriceChart;
