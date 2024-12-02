from api.models import CryptoCurrency
from api.tasks import update_crypto_prices
result = update_crypto_prices()
print(result)

cryptos = CryptoCurrency.objects.all()
for crypto in cryptos:
    print(f"{crypto.symbol}: ${crypto.price} (Updated: {crypto.last_updated})")
