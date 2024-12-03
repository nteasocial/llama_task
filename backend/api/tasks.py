import requests
from celery import shared_task
from datetime import datetime
from .models import CryptoCurrency
import logging

logger = logging.getLogger(__name__)
DEFILLAMA_API_URL = "https://coins.llama.fi/prices/current"


@shared_task(bind=True, max_retries=3, rate_limit='60/h')
def update_crypto_prices(self):
    try:
        coins = CryptoCurrency.objects.all().values_list('symbol', flat=True)
        if not coins:
            return "No cryptocurrencies configured"

        coins_param = ','.join(
            [f'coingecko:{symbol.lower()}' for symbol in coins])

        response = requests.get(f"{DEFILLAMA_API_URL}?coins={coins_param}")
        response.raise_for_status()

        data = response.json().get('coins', {})
        updated_count = 0

        for full_symbol, price_data in data.items():
            symbol = full_symbol.split(':')[1].upper()
            price = price_data.get('price')
            if price:
                CryptoCurrency.objects.filter(symbol=symbol).update(
                    price=price,
                    last_updated=datetime.now()
                )
                updated_count += 1

        return f"Updated {updated_count} cryptocurrency prices"

    except requests.exceptions.RequestException as e:
        logger.error(f"API Error: {str(e)}")
        self.retry(exc=e, countdown=60)  # Retry after 1 minute
