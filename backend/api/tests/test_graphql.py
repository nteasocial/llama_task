import pytest
from graphene_django.utils.testing import GraphQLTestCase
from api.models import CryptoCurrency
import json


@pytest.mark.graphql
class TestCryptoGraphQL(GraphQLTestCase):
    GRAPHQL_URL = "/graphql"

    def setUp(self):
        self.crypto = CryptoCurrency.objects.create(
            name="Curve DAO",
            symbol="CRV",
            price=1.23
        )

    def test_query_all_cryptocurrencies(self):
        """Test querying all cryptocurrencies"""
        response = self.query(
            '''
            query {
                allCryptocurrencies {
                    name
                    symbol
                    price
                    lastUpdated
                }
            }
            '''
        )

        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        crypto_data = content['data']['allCryptocurrencies'][0]

        assert len(content['data']['allCryptocurrencies']) == 1
        assert crypto_data['name'] == "Curve DAO"
        assert crypto_data['symbol'] == "CRV"
        assert float(crypto_data['price']) == 1.23

    def test_create_cryptocurrency_mutation(self):
        """Test creating a new cryptocurrency"""
        response = self.query(
            '''
            mutation {
                createCryptocurrency(
                    name: "Curve USD",
                    symbol: "crvUSD"
                ) {
                    cryptocurrency {
                        name
                        symbol
                    }
                }
            }
            '''
        )

        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        crypto = content['data']['createCryptocurrency']['cryptocurrency']

        assert crypto['name'] == "Curve USD"
        assert crypto['symbol'] == "crvUSD"

    def test_query_single_cryptocurrency(self):
        """Test querying a single cryptocurrency by symbol"""
        response = self.query(
            '''
            query {
                cryptocurrency(symbol: "CRV") {
                    name
                    symbol
                    price
                }
            }
            '''
        )

        self.assertResponseNoErrors(response)
        content = json.loads(response.content)
        crypto = content['data']['cryptocurrency']

        assert crypto['symbol'] == "CRV"
        assert float(crypto['price']) == 1.23
