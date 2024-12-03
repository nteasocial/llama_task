import requests
import time
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class DeFiLlamaService:
    COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
    _last_request = 0
    _rate_limit = 1

    @classmethod
    def get_crypto_price(cls, symbol):
        try:
            current = time.time()
            if current - cls._last_request < cls._rate_limit:
                time.sleep(cls._rate_limit)
            cls._last_request = time.time()

            coingecko_response = requests.get(cls.COINGECKO_URL)
            coingecko_response.raise_for_status()
            coingecko_data = coingecko_response.json()
            for coin in coingecko_data:
                if coin["symbol"].upper() == symbol.upper():
                    return Decimal(coin["current_price"])

            # If no data found, return 0
            logger.warning(f"No data found for {symbol}")
            return Decimal('0')

        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {str(e)}")
            return Decimal('0')
