"""Create and seed a local trailhead.db with realistic demo data.

    python scripts/seed.py              # ~400 customers, ~15k orders
    python scripts/seed.py --orders 50000
"""
import argparse
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from trailhead.db import init_db  # noqa: E402
from trailhead.pricing import price_cart  # noqa: E402

PRODUCTS = [
    ("TH-1001", "Ridgeline 2P Backpacking Tent", "tents", 289.00),
    ("TH-1002", "Summit 1P Ultralight Tent", "tents", 349.95),
    ("TH-1003", "Basecamp 6P Family Tent", "tents", 419.00),
    ("TH-1004", "Tent Footprint - 2P", "tents", 39.95),
    ("TH-2001", "Alpine 20F Down Sleeping Bag", "sleep", 229.00),
    ("TH-2002", "Trail 40F Synthetic Sleeping Bag", "sleep", 89.99),
    ("TH-2003", "Insulated Sleeping Pad", "sleep", 129.95),
    ("TH-2004", "Inflatable Camp Pillow", "sleep", 34.95),
    ("TH-3001", "Traverse 65L Pack", "packs", 259.00),
    ("TH-3002", "Daytripper 28L Pack", "packs", 119.00),
    ("TH-3003", "Hydration Reservoir 3L", "packs", 36.95),
    ("TH-3004", "Pack Rain Cover", "packs", 24.95),
    ("TH-4001", "Waterproof Hiking Boot", "footwear", 179.95),
    ("TH-4002", "Trail Runner", "footwear", 139.00),
    ("TH-4003", "Merino Hiking Sock (2-pack)", "footwear", 26.95),
    ("TH-4004", "Camp Sandal", "footwear", 54.95),
    ("TH-5001", "Storm Shell Rain Jacket", "apparel", 199.00),
    ("TH-5002", "Packable Down Vest", "apparel", 129.00),
    ("TH-5003", "Sun Hoodie", "apparel", 59.95),
    ("TH-5004", "Convertible Hiking Pant", "apparel", 79.95),
    ("TH-5005", "Fleece Beanie", "apparel", 22.95),
    ("TH-6001", "Two-Burner Camp Stove", "cooking", 149.95),
    ("TH-6002", "Canister Backpacking Stove", "cooking", 49.95),
    ("TH-6003", "Titanium Cook Pot 900ml", "cooking", 54.95),
    ("TH-6004", "Fuel Canister 230g", "cooking", 7.95),
    ("TH-6005", "Insulated Camp Mug", "cooking", 19.95),
    ("TH-6006", "Long-Handle Spork", "cooking", 10.10),
    ("TH-7001", "Rechargeable Headlamp", "electronics", 49.95),
    ("TH-7002", "Solar Lantern", "electronics", 34.95),
    ("TH-7003", "Power Bank 20000mAh", "electronics", 59.95),
    ("TH-7004", "Satellite Messenger", "electronics", 299.95),
    ("TH-8001", "Trekking Poles (pair)", "accessories", 89.95),
    ("TH-8002", "Water Filter Squeeze", "accessories", 37.95),
    ("TH-8003", "First Aid Kit", "accessories", 29.95),
    ("TH-8004", "Bear Canister", "accessories", 84.95),
    ("TH-8005", "Paracord 50ft", "accessories", 9.95),
    ("TH-8006", "Trail Map Case", "accessories", 14.95),
    ("TH-8007", "Carabiner Set", "accessories", 18.95),
]

PROMOS = [("TRAIL15", 15.0, 1), ("WELCOME10", 10.0, 1), ("SUMMER20", 20.0, 0)]

FIRST = ["Avery", "Jordan", "Riley", "Morgan", "Casey", "Quinn", "Rowan", "Skyler",
         "Harper", "Emerson", "Finley", "Hayden", "Reese", "Sage", "Tatum", "Blake"]
LAST = ["Nguyen", "Garcia", "Patel", "Kim", "Johnson", "Martinez", "Okafor", "Silva",
        "Chen", "Kowalski", "Haddad", "Larsen", "Moreau", "Rossi", "Tanaka", "Walsh"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="trailhead.db")
    parser.add_argument("--customers", type=int, default=400)
    parser.add_argument("--orders", type=int, default=15000)
    args = parser.parse_args()

    rng = random.Random(42)
    conn = init_db(args.db)
    start = datetime(2025, 1, 1)

    conn.executemany(
        "INSERT INTO products (sku, name, category, price, stock) VALUES (?, ?, ?, ?, ?)",
        [(sku, name, cat, price, rng.randint(0, 250)) for sku, name, cat, price in PRODUCTS],
    )
    conn.executemany("INSERT INTO promo_codes VALUES (?, ?, ?)", PROMOS)

    customers = []
    for i in range(1, args.customers + 1):
        first, last = rng.choice(FIRST), rng.choice(LAST)
        customers.append((
            f"{first} {last}",
            f"{first.lower()}.{last.lower()}{i}@example.com",
            rng.choices(["standard", "plus", "pro"], weights=[80, 15, 5])[0],
            (start + timedelta(days=rng.randint(0, 300))).isoformat(),
        ))
    conn.executemany(
        "INSERT INTO customers (name, email, tier, created_at) VALUES (?, ?, ?, ?)", customers
    )

    prices = {i + 1: p[3] for i, p in enumerate(PRODUCTS)}
    promos = {code: {"code": code, "percent_off": pct} for code, pct, _ in PROMOS}
    for _ in range(args.orders):
        # a few "power" customers place a lot of orders (B2B / outfitter accounts)
        cust = rng.randint(1, 12) if rng.random() < 0.25 else rng.randint(1, args.customers)
        picks = rng.sample(sorted(prices), rng.randint(1, 4))
        lines = [{"product_id": p, "unit_price": prices[p], "quantity": rng.randint(1, 3)} for p in picks]
        code = rng.choice([None, None, None, "TRAIL15", "WELCOME10"])
        totals = price_cart(lines, promos.get(code))
        created = start + timedelta(minutes=rng.randint(0, 60 * 24 * 660))
        cur = conn.execute(
            "INSERT INTO orders (customer_id, status, promo_code, subtotal, discount, tax, shipping, total, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (cust, rng.choice(["placed", "shipped", "shipped", "delivered"]), code,
             totals["subtotal"], totals["discount"], totals["tax"], totals["shipping"],
             totals["total"], created.isoformat(timespec="seconds")),
        )
        conn.executemany(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
            [(cur.lastrowid, l["product_id"], l["quantity"], l["unit_price"]) for l in lines],
        )

    conn.commit()
    counts = {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
              for t in ("customers", "products", "orders", "order_items")}
    print(f"seeded {args.db}: {counts}")


if __name__ == "__main__":
    main()
