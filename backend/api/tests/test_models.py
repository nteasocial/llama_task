import pytest
from django.utils import timezone
from decimal import Decimal
from api.models import CryptoCurrency


@pytest.mark.django_db
class TestCryptoCurrencyModel:
    @pytest.fixture(autouse=True)
    def setup_crypto(self):
        self.crypto = CryptoCurrency.objects.create(
            name="Curve DAO",
            symbol="CRV",
            price=Decimal('1.23'),
            last_updated=timezone.now()
        )

    def test_crypto_creation(self):
        assert self.crypto.name == "Curve DAO"
        assert self.crypto.symbol == "CRV"
        assert float(self.crypto.price) == 1.23

    def test_crypto_str_representation(self):
        assert str(self.crypto) == "Curve DAO (CRV)"

    def test_crypto_price_decimal_places(self):
        self.crypto.price = Decimal('1.23456789')
        self.crypto.save()
        assert float(self.crypto.price) == 1.23456789
