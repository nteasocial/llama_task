import pytest
from unittest.mock import patch
import requests
from django.utils import timezone
from decimal import Decimal
from api.models import CryptoCurrency
from api.tasks import update_crypto_prices


@pytest.mark.django_db
class TestCryptoTasks:
    @pytest.fixture(autouse=True)
    def setup_crypto(self, django_db_setup):
        CryptoCurrency.objects.all().delete()
        self.crypto = CryptoCurrency.objects.create(
            name="Curve DAO",
            symbol="CRV",
            price=Decimal('0.0'),
            last_updated=timezone.now()
        )

    @patch('requests.get')
    def test_update_crypto_prices_task(self, mock_get):
        mock_response = {
            'coins': {
                'coingecko:crv': {
                    'price': 1.23,
                }
            }
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.status_code = 200

        update_crypto_prices()
        updated_crypto = CryptoCurrency.objects.get(symbol="CRV")
        assert float(updated_crypto.price) == 1.23

    @patch('requests.get')
    def test_api_rate_limit_handling(self, mock_get):
        class MockResponse:
            status_code = 429  # Rate limit status code

        mock_get.return_value = MockResponse()
        mock_get.side_effect = requests.exceptions.RequestException(
            "Rate limit exceeded")

        with pytest.raises(requests.exceptions.RequestException):
            update_crypto_prices()

    def test_no_cryptocurrencies(self):
        CryptoCurrency.objects.all().delete()
        result = update_crypto_prices()
        assert result == "No cryptocurrencies configured"
