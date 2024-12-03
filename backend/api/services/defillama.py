import requests
import time
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class DeFiLlamaService:
    BASE_URL = "https://coins.llama.fi/prices/current"
    _last_request = 0
    _rate_limit = 1

    TOKEN_MAPPING = {
        'CRV': 'coingecko:curve-dao-token',
        'crvUSD': 'coingecko:crvusd',
        'sdCRV': 'ethereum:0xD1b5651E55D4CeeD36251c61c50C889B36F6abB5',
        'ETH': 'coingecko:ethereum',
        'USDC': 'coingecko:usd-coin',
        'USDT': 'coingecko:tether',
        'sCRV': 'ethereum:0xd533a949740bb3306d119cc777fa900ba034cd52'
    }

    @classmethod
    def get_crypto_price(cls, symbol):
        try:

            current = time.time()
            if current - cls._last_request < cls._rate_limit:
                time.sleep(cls._rate_limit - (current - cls._last_request))
            cls._last_request = time.time()

            token_id = cls.TOKEN_MAPPING.get(symbol)
            if not token_id:
                logger.warning(f"No mapping found for {symbol}")
                return Decimal('0')

            url = f"{cls.BASE_URL}/{token_id}"
            logger.info(f"Fetching price from URL: {url}")

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if 'coins' in data and token_id in data['coins'] and 'price' in data['coins'][token_id]:
                price = Decimal(str(data['coins'][token_id]['price']))
                logger.info(f"Price found for {symbol}: {price}")
                return price

            logger.warning(f"No price data found for {symbol}")
            return Decimal('0')

        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {str(e)}")
            return Decimal('0')

    @classmethod
    def get_all_prices(cls):
        try:
            current = time.time()
            if current - cls._last_request < cls._rate_limit:
                time.sleep(cls._rate_limit - (current - cls._last_request))
            cls._last_request = time.time()

            token_ids = ','.join(cls.TOKEN_MAPPING.values())
            url = f"{cls.BASE_URL}/{token_ids}"

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            prices = {}
            reverse_mapping = {v: k for k, v in cls.TOKEN_MAPPING.items()}

            if 'coins' in data:
                for token_id, coin_data in data['coins'].items():
                    symbol = reverse_mapping.get(token_id)
                    if symbol and 'price' in coin_data:
                        prices[symbol] = Decimal(str(coin_data['price']))
                    else:
                        logger.warning(
                            f"No price found for token_id: {token_id}")

            for symbol in cls.TOKEN_MAPPING.keys():
                if symbol not in prices:
                    prices[symbol] = Decimal('0')

            return prices

        except Exception as e:
            logger.error(f"Error fetching all prices: {str(e)}")
            return {symbol: Decimal('0') for symbol in cls.TOKEN_MAPPING}
