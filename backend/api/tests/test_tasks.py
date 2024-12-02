import pytest
from unittest.mock import patch
from api.models import CryptoCurrency
from api.tasks import update_crypto_prices


@pytest.mark.tasks
class TestCryptoTasks:
    @pytest.fixture
    def setup_cryptos(self):
        CryptoCurrency.objects.create(name="Curve DAO", symbol="CRV")
        CryptoCurrency.objects.create(name="Curve USD", symbol="crvUSD")
        CryptoCurrency.objects.create(
            name="Staked Curve USD", symbol="scrvUSD")

    @patch('requests.get')
    def test_update_crypto_prices_task(self, mock_get, setup_cryptos):
        """Test if price update task updates all cryptocurrencies"""
        mock_response = {
            "CRV": {"price": 1.23},
            "crvUSD": {"price": 0.99},
            "scrvUSD": {"price": 1.01}
        }
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.status_code = 200

        update_crypto_prices()

        crv = CryptoCurrency.objects.get(symbol="CRV")
        crvusd = CryptoCurrency.objects.get(symbol="crvUSD")
        scrvusd = CryptoCurrency.objects.get(symbol="scrvUSD")

        assert float(crv.price) == 1.23
        assert float(crvusd.price) == 0.99
        assert float(scrvusd.price) == 1.01

    @patch('requests.get')
    def test_api_rate_limit_handling(self, mock_get, setup_cryptos):
        """Test handling of API rate limits"""
        mock_get.return_value.status_code = 429  # Rate limit status

        result = update_crypto_prices()
        assert "Rate limited" in result or "Error" in result

    @patch('requests.get')
    def test_api_error_handling(self, mock_get, setup_cryptos):
        """Test handling of API errors"""
        mock_get.return_value.status_code = 500

        result = update_crypto_prices()
        assert "Error" in result
