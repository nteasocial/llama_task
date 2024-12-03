"use client";
import React, { useCallback } from "react";
import { useQuery } from "@apollo/client";
import { gql } from "@apollo/client";
import ReactECharts from "echarts-for-react";
import { useState } from "react";

// GraphQL queries remain the same
const GET_PRICES = gql`
  query {
    allCryptocurrencies {
      name
      symbol
      price
      lastUpdated
    }
  }
`;

const GET_SINGLE_CRYPTO = gql`
  query GetCryptocurrency($symbol: String!) {
    cryptocurrency(symbol: $symbol) {
      name
      symbol
      price
      lastUpdated
    }
  }
`;

// Separate PriceStats into a memo'd component for better performance
const PriceStats = React.memo(({ crypto }: { crypto: any }) => (
  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
    <div className="bg-white p-4 rounded-lg shadow">
      <h3 className="text-sm text-gray-500">Current Price</h3>
      <p className="text-xl font-bold">
        ${parseFloat(crypto.price).toFixed(2)}
      </p>
    </div>
    <div className="bg-white p-4 rounded-lg shadow">
      <h3 className="text-sm text-gray-500">Symbol</h3>
      <p className="text-xl font-bold">{crypto.symbol}</p>
    </div>
    <div className="bg-white p-4 rounded-lg shadow">
      <h3 className="text-sm text-gray-500">Name</h3>
      <p className="text-xl font-bold">{crypto.name}</p>
    </div>
    <div className="bg-white p-4 rounded-lg shadow">
      <h3 className="text-sm text-gray-500">Last Updated</h3>
      <p className="text-sm">{new Date(crypto.lastUpdated).toLocaleString()}</p>
    </div>
  </div>
));

PriceStats.displayName = "PriceStats";

// Main component with Next.js 14 optimizations
export default function PriceChart() {
  const [selectedCrypto, setSelectedCrypto] = useState<string | null>(null);
  const [chartType, setChartType] = useState("bar");

  const { loading, error, data } = useQuery(GET_PRICES, {
    pollInterval: 10000,
  });

  // Memoize chart options calculation
  const getChartOption = useCallback(() => {
    if (!data) return {};

    const cryptos = data.allCryptocurrencies;
    return {
      title: {
        text: "Cryptocurrency Prices",
        subtext: selectedCrypto
          ? `Showing details for ${selectedCrypto}`
          : "All Cryptocurrencies",
        left: "center",
      },
      tooltip: {
        trigger: "axis",
        formatter: (params: any) => {
          const crypto = cryptos[params[0].dataIndex];
          return `
            <div class="font-bold">${crypto.name}</div>
            <div>Price: $${parseFloat(crypto.price).toFixed(2)}</div>
            <div class="text-sm">Updated: ${new Date(
              crypto.lastUpdated
            ).toLocaleString()}</div>
          `;
        },
      },
      xAxis: {
        type: "category",
        data: cryptos.map((crypto: { symbol: string }) => crypto.symbol),
        axisLabel: {
          rotate: 45,
        },
      },
      yAxis: {
        type: "value",
        name: "Price (USD)",
        axisLabel: {
          formatter: "${value}",
        },
        splitLine: {
          show: true,
          lineStyle: {
            type: "dashed",
          },
        },
      },
      grid: {
        left: "5%",
        right: "5%",
        bottom: "15%",
        containLabel: true,
      },
      series: [
        {
          data: cryptos.map((crypto: { price: string }) =>
            parseFloat(crypto.price)
          ),
          type: chartType,
          showBackground: chartType === "bar",
          itemStyle: {
            color: function (params: any) {
              const colors = [
                "#5470c6",
                "#91cc75",
                "#fac858",
                "#ee6666",
                "#73c0de",
                "#3ba272",
                "#fc8452",
              ];
              return colors[params.dataIndex % colors.length];
            },
          },
          backgroundStyle: {
            color: "rgba(180, 180, 180, 0.2)",
          },
          label: {
            show: true,
            position: "top",
            formatter: "${c}",
          },
          smooth: chartType === "line",
        },
      ],
    };
  }, [data, selectedCrypto, chartType]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-500 p-4 rounded-lg bg-red-50">
        Error: {error.message}
      </div>
    );
  }

  const cryptos = data.allCryptocurrencies;

  return (
    <div className="w-full space-y-4">
      <div className="flex flex-wrap gap-4 justify-end mb-4">
        <select
          value={chartType}
          onChange={(e) => setChartType(e.target.value)}
          className="px-3 py-2 rounded border bg-white"
        >
          <option value="bar">Bar Chart</option>
          <option value="line">Line Chart</option>
        </select>
      </div>

      <div className="flex flex-wrap gap-2 justify-center mb-6">
        <button
          onClick={() => setSelectedCrypto(null)}
          className={`px-4 py-2 rounded-lg ${
            !selectedCrypto ? "bg-blue-500 text-white" : "bg-gray-200"
          }`}
        >
          All
        </button>
        {cryptos.map((crypto: { symbol: string }) => (
          <button
            key={crypto.symbol}
            onClick={() => setSelectedCrypto(crypto.symbol)}
            className={`px-4 py-2 rounded-lg ${
              selectedCrypto === crypto.symbol
                ? "bg-blue-500 text-white"
                : "bg-gray-200"
            }`}
          >
            {crypto.symbol}
          </button>
        ))}
      </div>

      {selectedCrypto && (
        <PriceStats
          crypto={cryptos.find(
            (c: { symbol: string }) => c.symbol === selectedCrypto
          )}
        />
      )}

      <div className="bg-white p-6 rounded-lg shadow">
        <ReactECharts
          option={getChartOption()}
          className="min-h-[500px]"
          notMerge={true}
        />
      </div>

      <div className="text-center text-sm text-gray-500 mt-4">
        Data updates every 10 seconds
      </div>
    </div>
  );
}
