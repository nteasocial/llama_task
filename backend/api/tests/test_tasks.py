import pytest
from unittest.mock import patch
from api.models import CryptoCurrency
from api.tasks import update_crypto_prices
from django.utils import timezone


@pytest.mark.django_db
class TestCryptoTasks:
    def setup_method(self):
        self.crypto = CryptoCurrency.objects.create(
            name="Curve DAO",
            symbol="CRV",
            price=0.0,
            last_updated=timezone.now()
        )

    @patch('requests.get')
    def test_update_crypto_prices_task(self, mock_get):
        mock_response = {
            "CRV": {"price": 1.23}
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.status_code = 200

        update_crypto_prices()

        crypto = CryptoCurrency.objects.get(symbol="CRV")
        assert float(crypto.price) == 1.23
