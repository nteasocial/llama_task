from api.tasks import update_crypto_prices


def run_task():
    result = update_crypto_prices()
    print(f"Task result: {result}")


if __name__ == "__main__":
    run_task()
