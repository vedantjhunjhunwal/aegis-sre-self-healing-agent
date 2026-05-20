from payment_client import charge_with_retry


def create_order(order_id, amount):
    charge_with_retry(order_id, amount)
    return {
        "order_id": order_id,
        "status": "confirmed",
    }
