# Trailhead Outfitters — Shop API

Backend for the Trailhead Outfitters storefront and ops dashboard. Small Flask + SQLite
service that powers product search, carts/checkout, and order history.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed.py          # creates trailhead.db with demo data
python wsgi.py                  # http://localhost:5050
```

## Endpoints

| Method | Path | Used by |
| --- | --- | --- |
| GET | `/health` | load balancer |
| GET | `/api/products?q=&category=&sort=` | storefront search box |
| GET | `/api/products/<id>` | product page |
| GET | `/api/products/categories` | nav menu |
| POST | `/api/cart/quote` | cart drawer (live totals) |
| POST | `/api/orders` | checkout |
| GET | `/api/orders/recent?limit=` | ops dashboard |
| GET | `/api/customers/<id>/orders` | account → order history |

Example quote:

```bash
curl -s localhost:5050/api/cart/quote -H 'content-type: application/json' \
  -d '{"items":[{"product_id":12,"quantity":1}],"promo_code":"WELCOME10"}'
```

## Project layout

```
trailhead/
  __init__.py   app factory
  catalog.py    product search + detail
  orders.py     cart quote, checkout, order history
  pricing.py    subtotal / promo / tax / shipping rules
  db.py         sqlite helpers
  schema.sql
scripts/seed.py demo data generator
tests/          pytest
```

## Tests

```bash
pytest
```

## Team

Commerce squad — Priya Raman (lead), Marcus Lee, Dana Okafor, Sam Torres.
