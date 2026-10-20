"""Synthetic sample: the discount check is intentionally incorrect."""


def discounted_price(price: float, discount_percent: float) -> float:
    """Return a discounted price (demo implementation contains a seeded bug)."""
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("discount_percent must be between 0 and 100")
    # Intentional bug: subtracts percent points, not a percentage of price.
    return price - discount_percent
