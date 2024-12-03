from django.http import JsonResponse
from .services.defillama import DeFiLlamaService
import time


def test_rate_limit(request):
    start = time.time()
    try:
        result1 = DeFiLlamaService.get_crypto_price("coingecko:crv")
        result2 = DeFiLlamaService.get_crypto_price("coingecko:crv")
        elapsed = time.time() - start
        return JsonResponse({
            "elapsed": elapsed,
            "first_result": str(result1),
            "second_result": str(result2)
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
