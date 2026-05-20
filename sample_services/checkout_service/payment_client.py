import time


class PaymentGatewayTimeout(Exception):
    pass


def calculate_retry_delay(attempt):
    return 0


def charge_gateway(order_id, amount):
    # Simulated flaky gateway. In production this would call an external payment service.
    raise PaymentGatewayTimeout("payment gateway timeout")


def charge_with_retry(order_id, amount, max_attempts=3):
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            return charge_gateway(order_id, amount)
        except PaymentGatewayTimeout as exc:
            last_error = exc
            delay = calculate_retry_delay(attempt)
            time.sleep(delay)

    raise last_error
