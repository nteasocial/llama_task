import pytest
from django.utils import timezone
from api.models import CryptoCurrency


@pytest.mark.django_db 
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
        assert crypto.name == "Curve DAO"
        assert crypto.symbol == "CRV"
        assert float(crypto.price) == 1.23

    def test_crypto_str_representation(self, crypto):
        assert str(crypto) == "Curve DAO (CRV)"

    def test_crypto_price_decimal_places(self, crypto):
        crypto.price = 1.23456789
        crypto.save()
        assert float(crypto.price) == 1.23456789
