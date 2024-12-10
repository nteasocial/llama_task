# api/tasks.py
from celery import shared_task
import requests
from django.utils import timezone
import logging
from .models import CryptoCurrency

logger = logging.getLogger(__name__)


@shared_task
def update_crypto_prices():
    print("\n=== STARTING PRICE UPDATE ===")
    try:
        # Make API request
        api_url = "https://coins.llama.fi/prices/current/coingecko:ethereum,coingecko:curve-dao-token,ethereum:0xf939e0a03fb07f59a73314e73794be0e57ac1b4e,ethereum:0xD1b5651E55D4CeeD36251c61c50C889B36F6abB5,ethereum:0xC25a3A3b969415c80451098fa907EC722572917F"

        print(f"1. Making API request to: {api_url}")
        response = requests.get(api_url)
        data = response.json()
        print(f"2. API Response: {data}")

        if 'coins' not in data:
            print("No 'coins' in API response!")
            return

        # Map API data to our database entries
        mappings = [
            {
                'symbol': 'ETH',
                'name': 'Ethereum',
                'api_id': 'coingecko:ethereum'
            },
            {
                'symbol': 'CRV',
                'name': 'Curve DAO',
                'api_id': 'coingecko:curve-dao-token'
            },
            {
                'symbol': 'crvUSD',
                'name': 'Curve USD',
                'api_id': 'ethereum:0xf939e0a03fb07f59a73314e73794be0e57ac1b4e'
            },
            {
                'symbol': 'sdCRV',
                'name': 'Stake DAO CRV',
                'api_id': 'ethereum:0xD1b5651E55D4CeeD36251c61c50C889B36F6abB5'
            },
            {
                'symbol': 'sCRV',
                'name': 'Stable CRV',
                'api_id': 'ethereum:0xC25a3A3b969415c80451098fa907EC722572917F'
            }
        ]

        update_time = timezone.now()

        # Update each cryptocurrency
        for mapping in mappings:
            try:
                if mapping['api_id'] in data['coins']:
                    new_price = float(
                        data['coins'][mapping['api_id']]['price'])
                    print(f"3. Got price for {mapping['symbol']}: {new_price}")

                    # Get or create the cryptocurrency entry
                    crypto, created = CryptoCurrency.objects.get_or_create(
                        symbol=mapping['symbol'],
                        defaults={
                            'name': mapping['name'],
                            'price': 0,
                            'last_updated': update_time
                        }
                    )

                    # Update with new price
                    old_price = crypto.price
                    crypto.price = new_price
                    crypto.last_updated = update_time
                    crypto.save()

                    print(
                        f"4. Updated {mapping['symbol']}: {old_price} -> {new_price}")
                else:
                    print(f"No price found for {mapping['symbol']}")
            except Exception as e:
                print(f"Error updating {mapping['symbol']}: {str(e)}")

        # Print final state
        print("\nFinal state of cryptocurrencies:")
        for crypto in CryptoCurrency.objects.all():
            print(f"{crypto.symbol}: {crypto.price} (Updated: {crypto.last_updated})")

    except Exception as e:
        print(f"Task error: {str(e)}")
        logger.error(f"Task error: {str(e)}", exc_info=True)

    print("=== PRICE UPDATE COMPLETED ===\n")


@shared_task
def initialize_crypto_prices():
    print("Initializing cryptocurrencies...")
    update_crypto_prices()
    return "Initialization completed"
