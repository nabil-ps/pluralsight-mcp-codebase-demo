from datetime import datetime, timezone

from flask import Blueprint, abort, jsonify, request

from .db import get_db, query_all, query_one
from .pricing import price_cart

bp = Blueprint("orders", __name__, url_prefix="/api")


def _hydrate(order):
    """Attach customer and line items (with product details) to an order row."""
    order["customer"] = query_one(
        "SELECT id, name, email, tier FROM customers WHERE id = ?",
        (order["customer_id"],),
    )
    items = query_all(
        "SELECT id, product_id, quantity, unit_price FROM order_items WHERE order_id = ?",
        (order["id"],),
    )
    for item in items:
        item["product"] = query_one(
            "SELECT id, sku, name, category FROM products WHERE id = ?",
            (item["product_id"],),
        )
    order["items"] = items
    return order


@bp.get("/orders/recent")
def recent_orders():
    """Ops dashboard feed: most recent orders, fully expanded."""
    limit = min(int(request.args.get("limit", 50)), 500)
    orders = query_all(
        "SELECT * FROM orders ORDER BY created_at DESC LIMIT ?", (limit,)
    )
    return jsonify([_hydrate(o) for o in orders])


@bp.get("/customers/<int:customer_id>/orders")
def customer_orders(customer_id):
    """Order history page for the account screen."""
    # TODO(marcus): outfitter accounts are timing out here (>2s). Probably need
    # Redis in front of this - revisit after the holiday freeze.
    if query_one("SELECT id FROM customers WHERE id = ?", (customer_id,)) is None:
        abort(404)
    orders = query_all(
        "SELECT * FROM orders WHERE customer_id = ? ORDER BY created_at DESC",
        (customer_id,),
    )
    return jsonify([_hydrate(o) for o in orders])


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
