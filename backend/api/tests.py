import time
import json
import requests
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from unittest.mock import patch, Mock
from graphene.test import Client
from colorama import init, Fore, Style
from app.schema import schema
from .models import CryptoCurrency
from .tasks import update_crypto_prices
from .services.defillama import DeFiLlamaService


init()


class CryptoCurrencyModelTests(TestCase):
    def setUp(self):
        print(f"\n{Fore.CYAN}Setting up Model Tests...{Style.RESET_ALL}")
        self.crypto = CryptoCurrency.objects.create(
            name="Curve DAO Token",
            symbol="CRV",
            price=Decimal("0.58"),
            last_updated=timezone.now()
        )

    def test_model_creation(self):
        print(f"{Fore.GREEN}Testing model creation...{Style.RESET_ALL}")
        self.assertEqual(self.crypto.name, "Curve DAO Token")
        self.assertEqual(self.crypto.symbol, "CRV")
        self.assertEqual(self.crypto.price, Decimal("0.58"))
        self.assertIsNotNone(self.crypto.last_updated)

    def test_model_string_representation(self):
        print(f"{Fore.GREEN}Testing model string representation...{Style.RESET_ALL}")
        self.assertEqual(str(self.crypto), "CRV")

    def test_price_validation(self):
        print(f"{Fore.GREEN}Testing price validation...{Style.RESET_ALL}")
        crypto = CryptoCurrency(
            name="Test Token",
            symbol="TEST",
            price=Decimal("-1.0")
        )

        def clean(self):
            if self.price < 0:
                raise ValidationError("Price cannot be negative")
        CryptoCurrency.clean = clean

        with self.assertRaises(ValidationError):
            crypto.full_clean()

    def test_symbol_uniqueness(self):
        print(f"{Fore.GREEN}Testing symbol uniqueness...{Style.RESET_ALL}")
        with self.assertRaises(Exception):
            CryptoCurrency.objects.create(
                name="Duplicate Token",
                symbol="CRV",
                price=Decimal("1.0")
            )


class CryptoTasksTests(TestCase):
    def setUp(self):
        print(f"\n{Fore.CYAN}Setting up Task Tests...{Style.RESET_ALL}")
        self.crypto1 = CryptoCurrency.objects.create(
            name="Curve DAO",
            symbol="CRV",
            price=Decimal("0.58"),
            last_updated=timezone.now()
        )
        self.crypto2 = CryptoCurrency.objects.create(
            name="Curve USD",
            symbol="crvUSD",
            price=Decimal("1.00"),
            last_updated=timezone.now()
        )

    @patch('api.services.defillama.DeFiLlamaService.get_all_prices')
    def test_successful_price_update(self, mock_get_all_prices):
        print(f"{Fore.GREEN}Testing successful price update...{Style.RESET_ALL}")
        mock_prices = {
            'CRV': Decimal('0.60'),
            'crvUSD': Decimal('1.01')
        }
        mock_get_all_prices.return_value = mock_prices

        result = update_crypto_prices()
        self.assertEqual(result, "Price updates completed")

        # Get fresh instances
        crypto1 = CryptoCurrency.objects.get(symbol='CRV')
        crypto2 = CryptoCurrency.objects.get(symbol='crvUSD')

        self.assertEqual(crypto1.price, Decimal('0.60'))
        self.assertEqual(crypto2.price, Decimal('1.01'))

    @patch('api.services.defillama.DeFiLlamaService.get_all_prices')
    def test_api_error_handling(self, mock_get_all_prices):
        print(f"{Fore.GREEN}Testing API error handling...{Style.RESET_ALL}")
        mock_get_all_prices.side_effect = Exception("API Error")

        with self.assertLogs('api', level='ERROR') as cm:
            result = update_crypto_prices()
            self.assertTrue("Error updating crypto prices" in cm.output[0])
            self.assertTrue(result.startswith("Error:"))

    @patch('api.services.defillama.DeFiLlamaService.get_all_prices')
    def test_partial_update(self, mock_get_all_prices):
        print(f"{Fore.GREEN}Testing partial update...{Style.RESET_ALL}")
        initial_crvusd_price = self.crypto2.price

        mock_prices = {
            'CRV': Decimal('0.65')
        }
        mock_get_all_prices.return_value = mock_prices

        result = update_crypto_prices()
        self.assertEqual(result, "Price updates completed")

        # Get fresh instances
        crypto1 = CryptoCurrency.objects.get(symbol='CRV')
        crypto2 = CryptoCurrency.objects.get(symbol='crvUSD')

        self.assertEqual(crypto1.price, Decimal('0.65'))
        # Should remain unchanged
        self.assertEqual(crypto2.price, initial_crvusd_price)


class GraphQLTests(TestCase):
    def setUp(self):
        print(f"\n{Fore.CYAN}Setting up GraphQL Tests...{Style.RESET_ALL}")
        self.client = Client(schema)
        self.crypto = CryptoCurrency.objects.create(
            name="Curve DAO Token",
            symbol="CRV",
            price=Decimal("0.58"),
            last_updated=timezone.now()
        )

    def test_query_all_cryptocurrencies(self):
        print(f"{Fore.GREEN}Testing query all cryptocurrencies...{Style.RESET_ALL}")
        query = '''
           query {
               allCryptocurrencies {
                   symbol
                   price
                   lastUpdated
               }
           }
       '''
        response = self.client.execute(query)
        self.assertIsNone(response.get('errors'))
        self.assertEqual(len(response['data']['allCryptocurrencies']), 1)

    def test_query_single_cryptocurrency(self):
        print(f"{Fore.GREEN}Testing query single cryptocurrency...{Style.RESET_ALL}")
        query = '''
           query {
               cryptocurrency(symbol: "CRV") {
                   name
                   symbol
                   price
                   lastUpdated
               }
           }
       '''
        response = self.client.execute(query)
        self.assertIsNone(response.get('errors'))
        self.assertEqual(
            response['data']['cryptocurrency']['symbol'],
            'CRV'
        )


class DeFiLlamaServiceTests(TestCase):
    def setUp(self):
        print(f"\n{Fore.CYAN}Setting up DeFiLlama Service Tests...{Style.RESET_ALL}")

    @patch('requests.get')
    def test_successful_price_fetch(self, mock_get):
        print(f"{Fore.GREEN}Testing successful price fetch...{Style.RESET_ALL}")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'coins': {
                'coingecko:curve-dao-token': {'price': 0.60}
            }
        }
        mock_get.return_value = mock_response

        price = DeFiLlamaService.get_crypto_price('CRV')
        self.assertAlmostEqual(float(price), 0.60, places=2)

    @patch('requests.get')
    def test_rate_limiting(self, mock_get):
        print(f"{Fore.GREEN}Testing rate limiting...{Style.RESET_ALL}")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'coins': {
                'coingecko:curve-dao-token': {'price': 0.60}
            }
        }
        mock_get.return_value = mock_response

        start_time = time.time()
        DeFiLlamaService.get_crypto_price("CRV")
        DeFiLlamaService.get_crypto_price("CRV")
        elapsed = time.time() - start_time
        self.assertGreaterEqual(elapsed, 1)

    @patch('requests.get')
    def test_error_handling(self, mock_get):
        print(f"{Fore.GREEN}Testing error handling...{Style.RESET_ALL}")
        mock_get.side_effect = requests.exceptions.RequestException(
            "API Error")
        with self.assertLogs('api.services.defillama', level='ERROR') as cm:
            price = DeFiLlamaService.get_crypto_price("CRV")
            self.assertEqual(price, Decimal('0'))
            self.assertTrue(any("API Error" in msg for msg in cm.output))

    @patch('requests.get')
    def test_invalid_response(self, mock_get):
        print(f"{Fore.GREEN}Testing invalid response handling...{Style.RESET_ALL}")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'invalid': 'response'}
        mock_get.return_value = mock_response

        price = DeFiLlamaService.get_crypto_price("CRV")
        self.assertEqual(price, Decimal('0'))
