"use client";
import { useQuery } from "@apollo/client";
import { gql } from "@apollo/client";
import ReactECharts from "echarts-for-react";

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

export default function PriceChart() {
  const { loading, error, data } = useQuery(GET_PRICES, {
    pollInterval: 30000,
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  const option = {
    title: {
      text: "Cryptocurrency Prices",
    },
    tooltip: {
      trigger: "axis",
    },
    xAxis: {
      type: "category",
      data: data.allCryptocurrencies.map(
        (crypto: { symbol: any }) => crypto.symbol
      ),
    },
    yAxis: {
      type: "value",
      name: "Price (USD)",
    },
    series: [
      {
        data: data.allCryptocurrencies.map((crypto: { price: string }) =>
          parseFloat(crypto.price)
        ),
        type: "bar",
        showBackground: true,
        backgroundStyle: {
          color: "rgba(180, 180, 180, 0.2)",
        },
      },
    ],
  };

  return (
    <div className="w-full p-4">
      <ReactECharts option={option} className="min-h-[400px]" />
    </div>
  );
}
