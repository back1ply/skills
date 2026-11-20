"""Order helpers used by the billing service."""


def line_total(item):
    """Return price times quantity for one order line."""
    return item["price"] * item["qty"]
