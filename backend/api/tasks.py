import logging
from decimal import Decimal
from django.utils import timezone
from celery import shared_task
from .models import CryptoCurrency
from .services.defillama import DeFiLlamaService

logger = logging.getLogger(__name__)


@shared_task
def update_crypto_prices():
    try:
        prices = DeFiLlamaService.get_all_prices()

        default_cryptos = [
            {"name": "Curve DAO", "symbol": "CRV"},
            {"name": "Curve USD", "symbol": "crvUSD"},
            {"name": "Stake DAO CRV", "symbol": "sdCRV"},
            {"name": "Ethereum", "symbol": "ETH"},
            {"name": "Stable CRV", "symbol": "sCRV"}
        ]

        for crypto_data in default_cryptos:
            symbol = crypto_data["symbol"]
            crypto, _ = CryptoCurrency.objects.get_or_create(
                symbol=symbol,
                defaults={
                    "name": crypto_data["name"],
                    "price": Decimal('0')
                }
            )
            if symbol in prices:
                crypto.price = prices[symbol]
                crypto.last_updated = timezone.now()
                crypto.save()
                logger.info(f"Updated price for {symbol}: {prices[symbol]}")
            else:
                logger.warning(f"No price found for {symbol}")

        return "Price updates completed"
    except Exception as e:
        error_msg = f"Error updating crypto prices: {str(e)}"
        logger.error(error_msg)
        return f"Error: {str(e)}"
