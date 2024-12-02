from django.db import models
from django.utils import timezone


class CryptoCurrency(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=30, decimal_places=18)
    last_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Cryptocurrencies"

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    def update_price(self, new_price):
        self.price = new_price
        self.last_updated = timezone.now()
        self.save()
