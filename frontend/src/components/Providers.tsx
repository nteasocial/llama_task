"use client";
import { ApolloClient, ApolloProvider, InMemoryCache } from "@apollo/client";
import { useState } from "react";

const client = new ApolloClient({
  uri: process.env.NEXT_PUBLIC_GRAPHQL_URL || "http://localhost:8000/graphql/",
  cache: new InMemoryCache(),
});

export function Providers({ children }: { children: React.ReactNode }) {
  const [error, setError] = useState<Error | null>(null);

  if (error) {
    return (
      <div className="p-4 bg-red-50 text-red-500">
        Error connecting to GraphQL server: {error.message}
      </div>
    );
  }

  return <ApolloProvider client={client}>{children}</ApolloProvider>;
}
