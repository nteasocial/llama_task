from celery import shared_task
from .models import CryptoCurrency
from .services.defillama import DeFiLlamaService
from celery.schedules import crontab # type: ignore
from celery.decorators import periodic_task # type: ignore
import time


@shared_task
def update_crypto_prices():
    default_cryptos = [
        {"name": "Curve DAO", "symbol": "CRV"},
        {"name": "Curve USD", "symbol": "crvUSD"},
        {"name": "Stake DAO CRV", "symbol": "sdCRV"},
        {"name": "Ethereum", "symbol": "ETH"},
        {"name": "Stable CRV", "symbol": "sCRV"}
    ]

    for crypto_data in default_cryptos:
        crypto, _ = CryptoCurrency.objects.get_or_create(
            symbol=crypto_data["symbol"],
            defaults={"name": crypto_data["name"], "price": 0}
        )
        crypto.price = DeFiLlamaService.get_crypto_price(crypto.symbol)
        crypto.save()

    return "Price updates completed"


@periodic_task(run_every=crontab(minute='*/30'))
def scheduled_update_crypto_prices():
    update_crypto_prices.delay()
