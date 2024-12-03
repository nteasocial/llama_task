from django.db import models
from django.utils import timezone
from decimal import Decimal


class CryptoCurrency(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, unique=True)
    price = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal('0.00'))
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.symbol
