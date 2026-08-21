from datetime import datetime, timezone

from flask import Blueprint, abort, jsonify, request

from .db import get_db, query_one
from .pricing import price_cart

bp = Blueprint("orders", __name__, url_prefix="/api")


def _load_cart(payload):
    lines = []
    for entry in payload.get("items", []):
        product = query_one(
            "SELECT id, price, stock FROM products WHERE id = ?",
            (entry["product_id"],),
        )
        if product is None:
            abort(400, description=f"unknown product {entry['product_id']}")
        lines.append(
            {
                "product_id": product["id"],
                "unit_price": product["price"],
                "quantity": int(entry.get("quantity", 1)),
            }
        )

    promo = None
    code = payload.get("promo_code")
    if code:
        promo = query_one(
            "SELECT code, percent_off FROM promo_codes WHERE code = ? AND active = 1",
            (code.upper(),),
        )
    return lines, promo


@bp.post("/cart/quote")
def quote():
    lines, promo = _load_cart(request.get_json(force=True))
    return jsonify(price_cart(lines, promo))


@bp.post("/orders")
def place_order():
    payload = request.get_json(force=True)
    lines, promo = _load_cart(payload)
    if not lines:
        abort(400, description="cart is empty")
    totals = price_cart(lines, promo)

    db = get_db()
    cur = db.execute(
        "INSERT INTO orders (customer_id, promo_code, subtotal, discount, tax, shipping, total, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            payload["customer_id"],
            promo["code"] if promo else None,
            totals["subtotal"],
            totals["discount"],
            totals["tax"],
            totals["shipping"],
            totals["total"],
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
        ),
    )
    order_id = cur.lastrowid
    db.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
        [(order_id, l["product_id"], l["quantity"], l["unit_price"]) for l in lines],
    )
    db.commit()
    return jsonify(id=order_id, **totals), 201
