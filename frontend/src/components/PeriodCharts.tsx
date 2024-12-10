"use client";

import React, { useCallback, useState } from "react";
import { useQuery } from "@apollo/client";
import { gql } from "@apollo/client";
import ReactECharts from "echarts-for-react";
import { Card, CardContent } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import {
  BarChart2,
  LineChart,
  TrendingUp,
  Clock,
  RefreshCcw,
  AlertCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Cryptocurrency {
  name: string;
  symbol: string;
  price: string;
  lastUpdated: string;
}

interface CryptoStatsProps {
  crypto: Cryptocurrency;
  previousPrice?: string;
}

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

const calculatePriceChange = (
  currentPrice: string,
  previousPrice?: string
): string => {
  if (!previousPrice) return "0.00";
  const change =
    ((parseFloat(currentPrice) - parseFloat(previousPrice)) /
      parseFloat(previousPrice)) *
    100;
  return change.toFixed(2);
};

const CryptoStats: React.FC<CryptoStatsProps> = React.memo(
  ({ crypto, previousPrice }) => {
    const priceChange = calculatePriceChange(crypto.price, previousPrice);
    const stats = [
      {
        label: "Current Price",
        value: `$${parseFloat(crypto.price).toFixed(2)}`,
        icon: <TrendingUp className="w-4 h-4 text-emerald-500" />,
        trend: `${parseFloat(priceChange) >= 0 ? "+" : ""}${priceChange}%`,
        trendColor:
          parseFloat(priceChange) >= 0 ? "text-emerald-500" : "text-red-500",
      },
      {
        label: "Symbol / Name",
        value: crypto.symbol,
        secondary: crypto.name,
      },
      {
        label: "Last Updated",
        value: new Date(crypto.lastUpdated).toLocaleTimeString(),
        icon: <Clock className="w-4 h-4 text-violet-500" />,
        secondary: new Date(crypto.lastUpdated).toLocaleDateString(),
      },
    ];

    return (
      <div className="flex flex-row gap-4 mb-6">
        {stats.map((stat, index) => (
          <Card
            key={index}
            className="flex-1 hover:shadow-lg transition-all duration-200 bg-white/50 backdrop-blur-sm border-2 border-gray-100"
          >
            <CardContent className="p-4">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-500">
                    {stat.label}
                  </p>
                  <h3
                    className={cn(
                      "mt-2 text-xl font-bold",
                      index === 0 ? "text-emerald-600" : "text-gray-900"
                    )}
                  >
                    {stat.value}
                  </h3>
                  {stat.secondary && (
                    <p className="mt-1 text-sm text-gray-600">
                      {stat.secondary}
                    </p>
                  )}
                </div>
                {stat.icon && <div>{stat.icon}</div>}
              </div>
              {stat.trend && (
                <div
                  className={cn("mt-2 text-sm font-medium", stat.trendColor)}
                >
                  {stat.trend} from last update
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }
);

CryptoStats.displayName = "CryptoStats";

const ChartTypeButton: React.FC<{
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}> = ({ active, onClick, icon, label }) => (
  <Button
    onClick={onClick}
    aria-pressed={active}
    role="button"
    className={cn(
      "relative px-4 py-2 transition-all duration-200",
      "border-2",
      active
        ? "border-violet-500 bg-violet-50 text-violet-700 shadow-sm"
        : "border-gray-200 bg-white text-gray-700 hover:border-violet-200 hover:bg-violet-50/50"
    )}
  >
    <div className="flex items-center gap-2">
      {icon}
      {label}
    </div>
  </Button>
);

const CryptoButton: React.FC<{
  symbol: string;
  active: boolean;
  onClick: () => void;
}> = ({ symbol, active, onClick }) => (
  <Button
    onClick={onClick}
    aria-pressed={active}
    role="button"
    className={cn(
      "min-w-[80px] transition-all duration-200",
      "border-2 shadow-sm font-medium",
      active
        ? "border-emerald-500 bg-emerald-50 text-emerald-700"
        : "border-gray-200 bg-white text-gray-700 hover:border-emerald-200 hover:bg-emerald-50/50"
    )}
  >
    {symbol}
  </Button>
);

const ErrorFallback: React.FC<{ message: string }> = ({ message }) => (
  <Card className="bg-red-50 border-2 border-red-100">
    <CardContent className="p-6">
      <div className="flex flex-col items-center gap-4">
        <AlertCircle className="w-8 h-8 text-red-500" />
        <p className="text-red-600">{message}</p>
        <Button
          onClick={() => window.location.reload()}
          className="border-2 border-red-500 bg-red-50 text-red-700 hover:bg-red-100"
        >
          Retry
        </Button>
      </div>
    </CardContent>
  </Card>
);

export default function PriceTracker() {
  const [selectedCrypto, setSelectedCrypto] = useState<string | null>(null);
  const [chartType, setChartType] = useState<"bar" | "line">("bar");
  const [previousPrices, setPreviousPrices] = useState<Record<string, string>>(
    {}
  );

  const { loading, error, data } = useQuery(GET_PRICES, {
    pollInterval: 10000,
    onCompleted: (newData) => {
      if (data?.allCryptocurrencies) {
        const newPrices: Record<string, string> = {};
        data.allCryptocurrencies.forEach((crypto: Cryptocurrency) => {
          newPrices[crypto.symbol] = crypto.price;
        });
        setPreviousPrices(newPrices);
      }
    },
  });

  const getChartOption = useCallback(() => {
    if (!data?.allCryptocurrencies?.length) {
      return {
        title: {
          text: "Cryptocurrency Prices",
          left: "center",
        },
        xAxis: {
          type: "category",
          data: [],
        },
        yAxis: {
          type: "value",
        },
        series: [
          {
            data: [],
            type: chartType,
          },
        ],
      };
    }

    const cryptos = data.allCryptocurrencies;
    const colors = {
      bar: {
        gradient: new Array(cryptos.length).fill(0).map((_, i) => ({
          offset: 0,
          color: `rgba(59, 130, 246, ${0.7 + (i * 0.3) / cryptos.length})`,
        })),
      },
      line: {
        gradient: [
          { offset: 0, color: "rgba(16, 185, 129, 0.1)" },
          { offset: 1, color: "rgba(16, 185, 129, 0.6)" },
        ],
      },
    };

    return {
      title: {
        text: "Cryptocurrency Prices",
        subtext: selectedCrypto
          ? `Showing details for ${selectedCrypto}`
          : "All Cryptocurrencies",
        left: "center",
        top: 20,
        textStyle: {
          fontFamily: "Inter, sans-serif",
          fontSize: 24,
          fontWeight: 600,
          color: "#111827",
        },
        subtextStyle: {
          fontSize: 14,
          color: "#6B7280",
        },
      },
      tooltip: {
        trigger: "axis",
        backgroundColor: "rgba(255, 255, 255, 0.9)",
        borderColor: "#E5E7EB",
        borderWidth: 1,
        padding: [16, 16],
        textStyle: {
          color: "#111827",
        },
        formatter: (params: any) => {
          const crypto = cryptos[params[0].dataIndex];
          const priceChange = calculatePriceChange(
            crypto.price,
            previousPrices[crypto.symbol]
          );
          return `
          <div style="padding: 8px;">
            <div style="font-weight: bold; margin-bottom: 4px;">${
              crypto.name
            }</div>
            <div style="color: #059669;">$${parseFloat(crypto.price).toFixed(
              2
            )}</div>
            <div style="color: ${
              parseFloat(priceChange) >= 0 ? "#059669" : "#DC2626"
            };">
              ${parseFloat(priceChange) >= 0 ? "+" : ""}${priceChange}%
            </div>
            <div style="font-size: 12px; color: #6B7280; margin-top: 4px;">
              ${new Date(crypto.lastUpdated).toLocaleString()}
            </div>
          </div>
        `;
        },
      },
      xAxis: {
        type: "category",
        data: cryptos.map((crypto: { symbol: any }) => crypto.symbol),
        axisLabel: {
          rotate: 45,
          fontFamily: "Inter, sans-serif",
          color: "#4B5563",
        },
        axisLine: {
          lineStyle: {
            color: "#E5E7EB",
          },
        },
      },
      yAxis: {
        type: "value",
        name: "Price (USD)",
        nameTextStyle: {
          color: "#6B7280",
          padding: [0, 0, 8, 0],
        },
        axisLabel: {
          formatter: (value: number) => `$${value}`,
          fontFamily: "Inter, sans-serif",
          color: "#4B5563",
        },
        splitLine: {
          lineStyle: {
            type: "dashed",
            color: "#E5E7EB",
          },
        },
      },
      grid: {
        left: "5%",
        right: "5%",
        bottom: "15%",
        top: "20%",
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
              return {
                type: "linear",
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: colors[chartType].gradient,
              };
            },
            borderRadius: chartType === "bar" ? [4, 4, 0, 0] : 0,
          },
          backgroundStyle: {
            color: "rgba(240, 240, 240, 0.2)",
          },
          label: {
            show: true,
            position: "top",
            formatter: (params: any) => `$${params.value}`,
            fontFamily: "Inter, sans-serif",
            color: "#111827",
          },
          smooth: chartType === "line",
          areaStyle:
            chartType === "line"
              ? {
                  opacity: 0.8,
                  color: {
                    type: "linear",
                    x: 0,
                    y: 0,
                    x2: 0,
                    y2: 1,
                    colorStops: colors.line.gradient,
                  },
                }
              : undefined,
        },
      ],
    };
  }, [data?.allCryptocurrencies, selectedCrypto, chartType, previousPrices]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[600px] bg-gray-50/30">
        <div className="flex flex-col items-center gap-4">
          <RefreshCcw className="w-8 h-8 text-violet-500 animate-spin" />
          <p className="text-gray-600">Loading cryptocurrency data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return <ErrorFallback message={error.message} />;
  }

  const cryptos = data.allCryptocurrencies;
  const selectedCryptoData = selectedCrypto
    ? cryptos.find((c: Cryptocurrency) => c.symbol === selectedCrypto)
    : null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 via-blue-50 to-emerald-50 p-6 space-y-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col gap-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <h1 className="text-3xl font-bold text-gray-900">
              Crypto Price Tracker
            </h1>
            <div className="flex gap-2">
              <ChartTypeButton
                active={chartType === "bar"}
                onClick={() => setChartType("bar")}
                icon={<BarChart2 className="w-4 h-4" />}
                label="Bar Chart"
              />
              <ChartTypeButton
                active={chartType === "line"}
                onClick={() => setChartType("line")}
                icon={<LineChart className="w-4 h-4" />}
                label="Line Chart"
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <CryptoButton
              symbol="All"
              active={!selectedCrypto}
              onClick={() => setSelectedCrypto(null)}
            />
            {cryptos.map((crypto: Cryptocurrency) => (
              <CryptoButton
                key={crypto.symbol}
                symbol={crypto.symbol}
                active={selectedCrypto === crypto.symbol}
                onClick={() => setSelectedCrypto(crypto.symbol)}
              />
            ))}
          </div>

          {selectedCryptoData && (
            <CryptoStats
              crypto={selectedCryptoData}
              previousPrice={previousPrices[selectedCryptoData.symbol]}
            />
          )}

          <Card className="shadow-lg bg-white/50 backdrop-blur-sm border-2 border-gray-100">
            <CardContent className="p-6">
              <ReactECharts
                option={getChartOption()}
                className="min-h-[600px]"
                notMerge={true}
                showLoading={loading}
                opts={{ renderer: "canvas" }}
                onEvents={{
                  click: (params: any) => {
                    const crypto = cryptos[params.dataIndex];
                    if (crypto) {
                      setSelectedCrypto(crypto.symbol);
                    }
                  },
                }}
              />
            </CardContent>
          </Card>

          <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
            <RefreshCcw className="w-4 h-4" />
            <span>Data updates automatically every 10 seconds</span>
          </div>
        </div>
      </div>
    </div>
  );
}
