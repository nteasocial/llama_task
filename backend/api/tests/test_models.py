import pytest
from api.models import CryptoCurrency
from django.utils import timezone


@pytest.mark.models
class TestCryptoCurrencyModel:
    @pytest.fixture
    def crypto(self):
        return CryptoCurrency.objects.create(
            name="Curve DAO",
            symbol="CRV",
            price=1.23,
            last_updated=timezone.now()
        )

    def test_crypto_creation(self, crypto):
        """Test if cryptocurrency model is created with correct fields"""
        assert crypto.name == "Curve DAO"
        assert crypto.symbol == "CRV"
        assert float(crypto.price) == 1.23
        assert crypto.last_updated is not None

    def test_crypto_str_representation(self, crypto):
        """Test string representation of model"""
        assert str(crypto) == "Curve DAO (CRV)"

    def test_crypto_price_decimal_places(self, crypto):
        """Test price field accepts correct decimal places"""
        crypto.price = 1.23456789
        crypto.save()
        crypto.refresh_from_db()
        assert float(crypto.price) == 1.23456789
