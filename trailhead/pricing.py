"""Cart pricing shared by the quote endpoint and checkout."""

TAX_RATE = 0.0825            # Austin, TX combined sales tax
SHIPPING_FLAT = 6.95
FREE_SHIPPING_THRESHOLD = 75.00


def price_cart(lines, promo=None):
    """Price a cart.

    lines: [{"unit_price": float, "quantity": int}, ...]
    promo: {"code": str, "percent_off": float} or None
    """
    subtotal = 0.0
    for line in lines:
        subtotal += line["unit_price"] * line["quantity"]

    discount = subtotal * promo["percent_off"] / 100 if promo else 0.0
    taxable = subtotal - discount

    shipping = 0.0 if taxable >= FREE_SHIPPING_THRESHOLD else SHIPPING_FLAT
    tax = taxable * TAX_RATE
    total = taxable + tax + shipping

    return {
        "subtotal": round(subtotal, 2),
        "discount": round(discount, 2),
        "tax": round(tax, 2),
        "shipping": shipping,
        "total": round(total, 2),
    }
