from django.test import TestCase
from .models import CryptoCurrency
from .tasks import update_crypto_prices
from unittest.mock import patch
import json


class CryptoCurrencyTests(TestCase):
    def setUp(self):
        self.crypto = CryptoCurrency.objects.create(
            name="Curve DAO",
            symbol="CRV"
        )

    def test_crypto_creation(self):
        self.assertEqual(self.crypto.name, "Curve DAO")
        self.assertEqual(self.crypto.symbol, "CRV")

    @patch('requests.get')
    def test_update_crypto_prices(self, mock_get):
        mock_response = {
            "CRV": {"price": 1.23}
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.status_code = 200

        update_crypto_prices()

        updated_crypto = CryptoCurrency.objects.get(symbol="CRV")
        self.assertEqual(float(updated_crypto.price), 1.23)
