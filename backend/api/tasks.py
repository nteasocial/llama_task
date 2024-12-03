import requests
from celery import shared_task
from datetime import datetime
from .models import CryptoCurrency
import logging
logger = logging.getLogger(__name__)


DEFILLAMA_API_URL = "https://api.llama.fi/simple/price"


@shared_task(bind=True, max_retries=3)
def update_crypto_prices(self):
    try:
        # Get coins to track from database
        coins = CryptoCurrency.objects.all().values_list('symbol', flat=True)

        if not coins:
            return "No cryptocurrencies configured"

        # Format coins for DeFiLlama API
        coins_param = ','.join(coins)

        # Make API request
        response = requests.get(f"{DEFILLAMA_API_URL}/{coins_param}")
        response.raise_for_status()

        price_data = response.json()

        # Update prices in database
        for symbol, data in price_data.items():
            CryptoCurrency.objects.filter(symbol=symbol).update(
                price=data['price'],
                last_updated=datetime.now()
            )

        return f"Updated prices for {len(price_data)} cryptocurrencies"

    except requests.exceptions.RequestException as e:
        self.retry(exc=e, countdown=60)  # Retry after 1 minute
