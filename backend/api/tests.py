import time
import json
import requests
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from unittest.mock import patch, Mock
from graphene.test import Client
from app.schema import schema
from .models import CryptoCurrency
from .tasks import update_crypto_prices
from .services.defillama import DeFiLlamaService


class CryptoCurrencyModelTests(TestCase):
    def setUp(self):
        self.crypto = CryptoCurrency.objects.create(
            name="Curve DAO Token",
            symbol="CRV",
            price=Decimal("0.58"),
            last_updated=timezone.now()
        )

    def test_model_creation(self):
        self.assertEqual(self.crypto.name, "Curve DAO Token")
        self.assertEqual(self.crypto.symbol, "CRV")
        self.assertEqual(self.crypto.price, Decimal("0.58"))
        self.assertIsNotNone(self.crypto.last_updated)

    def test_model_string_representation(self):
        self.assertEqual(str(self.crypto), "CRV")

    def test_price_validation(self):
        with self.assertRaises(ValidationError):
            crypto = CryptoCurrency(
                name="Test Token",
                symbol="TEST",
                price=Decimal("-1.0")
            )
            crypto.full_clean()

    def test_symbol_uniqueness(self):
        with self.assertRaises(Exception):
            CryptoCurrency.objects.create(
                name="Duplicate Token",
                symbol="CRV",
                price=Decimal("1.0")
            )


class CryptoTasksTests(TestCase):
    def setUp(self):
        self.crypto1 = CryptoCurrency.objects.create(
            name="Curve DAO Token",
            symbol="CRV",
            price=Decimal("0.58")
        )
        self.crypto2 = CryptoCurrency.objects.create(
            name="Curve USD",
            symbol="crvUSD",
            price=Decimal("1.00")
        )

    @patch('requests.get')
    def test_successful_price_update(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'coins': {
                'coingecko:crv': {'price': 0.60},
                'coingecko:crvusd': {'price': 1.01}
            }
        }
        mock_get.return_value = mock_response

        result = update_crypto_prices()
        self.assertIn("Price update completed", result)

        self.crypto1.refresh_from_db()
        self.crypto2.refresh_from_db()
        self.assertEqual(self.crypto1.price, Decimal("0.60"))
        self.assertEqual(self.crypto2.price, Decimal("1.01"))

    @patch('requests.get')
    def test_api_error_handling(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException(
            "API Error")
        with self.assertLogs(level='ERROR') as cm:
            update_crypto_prices()
            self.assertIn("API Error", cm.output[0])

    def test_no_cryptocurrencies(self):
        CryptoCurrency.objects.all().delete()
        result = update_crypto_prices()
        self.assertEqual(result, "Price update completed")

    @patch('requests.get')
    def test_rate_limiting(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'coins': {}}
        mock_get.return_value = mock_response

        for _ in range(3):
            update_crypto_prices()
        self.assertLessEqual(mock_get.call_count, 3)

    @patch('requests.get')
    def test_partial_update(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'coins': {
                'coingecko:crv': {'price': 0.65}
            }
        }
        mock_get.return_value = mock_response

        update_crypto_prices()
        self.crypto1.refresh_from_db()
        self.crypto2.refresh_from_db()
        self.assertEqual(self.crypto1.price, Decimal("0.65"))
        self.assertEqual(self.crypto2.price, Decimal("1.00"))


class GraphQLTests(TestCase):
    def setUp(self):
        self.client = Client(schema)

    def test_create_cryptocurrency(self):
        mutation = '''
            mutation {
                createCryptocurrency(name: "Test", symbol: "TEST") {
                    cryptocurrency { 
                        name
                        symbol
                        price
                    }
                }
            }
        '''
        response = self.client.execute(mutation)
        self.assertIsNone(response.get('errors'))
        self.assertEqual(
            response['data']['createCryptocurrency']['cryptocurrency']['symbol'],
            'TEST'
        )

    def test_query_cryptocurrencies(self):
        CryptoCurrency.objects.create(
            name="Test Coin",
            symbol="TEST",
            price=Decimal("1.0")
        )
        query = '''
            query {
                allCryptocurrencies {
                    symbol
                    price
                }
            }
        '''
        response = self.client.execute(query)
        self.assertIsNone(response.get('errors'))
        self.assertEqual(len(response['data']['allCryptocurrencies']), 1)


class DeFiLlamaServiceTests(TestCase):
    @patch('api.services.defillama.requests.get')
    def test_rate_limiting(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'coins': {}}
        mock_get.return_value = mock_response

        start_time = time.time()
        DeFiLlamaService.get_crypto_price("CRV")
        DeFiLlamaService.get_crypto_price("CRV")
        elapsed = time.time() - start_time
        self.assertGreaterEqual(elapsed, 1)
