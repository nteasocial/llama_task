import {
  ApolloClient,
  InMemoryCache,
  defaultDataIdFromObject,
} from "@apollo/client";

export const client = new ApolloClient({
  uri: "http://localhost:8000/graphql/",
  cache: new InMemoryCache({
    typePolicies: {
      Query: {
        fields: {
          allCryptocurrencies: {
            merge: false, // Don't merge with existing data
          },
        },
      },
    },
  }),
  defaultOptions: {
    watchQuery: {
      fetchPolicy: "network-only",
      nextFetchPolicy: "cache-first",
    },
  },
});
