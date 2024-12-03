import pytest
from graphene.test import Client
from django.test import TestCase
from decimal import Decimal
from django.utils import timezone
from api.schema import schema
from api.models import CryptoCurrency


@pytest.mark.django_db
class TestCryptoGraphQL(TestCase):
    def setUp(self):
        self.client = Client(schema)
        # Clear any existing data
        CryptoCurrency.objects.all().delete()

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
        cryptos = response['data']['allCryptocurrencies']
        assert len(cryptos) == 1
        assert cryptos[0]['symbol'] == 'CRV'
        assert float(cryptos[0]['price']) == 1.23

    def test_create_cryptocurrency_mutation(self):
        mutation = '''
            mutation {
                createCryptocurrency(
                    name: "Curve USD"
                    symbol: "crvUSD"
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
        data = response['data']
        assert data is not None
        assert data['createCryptocurrency']['cryptocurrency']['symbol'] == 'crvUSD'
