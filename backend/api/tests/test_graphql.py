import pytest
from graphene.test import Client
from django.test import TestCase
from django.utils import timezone
from api.schema import schema
from api.models import CryptoCurrency
from decimal import Decimal


@pytest.mark.django_db
class TestCryptoGraphQL(TestCase):
    def setUp(self):
        self.client = Client(schema)
        self.crypto = CryptoCurrency.objects.create(
            name="Curve DAO",
            symbol="CRV",
            price=Decimal('1.23'),
            last_updated=timezone.now()  
        )

    def test_query_all_cryptocurrencies(self):
        query = '''
            query {
                allCryptocurrencies {
                    name
                    symbol
                    price
                }
            }
        '''
        response = self.client.execute(query)
        assert 'errors' not in response
        assert len(response['data']['allCryptocurrencies']) == 1
        assert response['data']['allCryptocurrencies'][0]['symbol'] == 'CRV'

    def test_create_cryptocurrency_mutation(self):
        mutation = '''
            mutation {
                createCryptocurrency(
                    name: "Curve USD",
                    symbol: "crvUSD",
                    price: "1.0"
                ) {
                    cryptocurrency {
                        name
                        symbol
                        price
                    }
                }
            }
        '''
        response = self.client.execute(mutation)
        assert 'errors' not in response
        assert response['data']['createCryptocurrency']['cryptocurrency']['symbol'] == 'crvUSD'
