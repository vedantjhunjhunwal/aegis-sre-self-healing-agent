from payment_client import calculate_retry_delay


def test_retry_delay_is_not_zero():
    assert calculate_retry_delay(1) > 0


def test_retry_delay_is_bounded():
    assert calculate_retry_delay(10) <= 2.0


def test_retry_delay_increases():
    assert calculate_retry_delay(1) < calculate_retry_delay(3)
