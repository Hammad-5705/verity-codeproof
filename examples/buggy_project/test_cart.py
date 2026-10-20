"""Expected behavior for the deliberately buggy demo module."""

from cart import discounted_price


def test_discount_is_a_percentage_of_the_original_price():
    assert discounted_price(100, 20) == 80
