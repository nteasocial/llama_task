import { ApolloClient, InMemoryCache, HttpLink } from "@apollo/client";

const client = new ApolloClient({
  link: new HttpLink({
    uri: "http://localhost:8000/graphql/", // Replace with your backend's GraphQL endpoint
  }),
  cache: new InMemoryCache(),
});

export default client;
