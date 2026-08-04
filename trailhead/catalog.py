from flask import Blueprint, abort, jsonify, request

from .db import query_all, query_one

bp = Blueprint("catalog", __name__, url_prefix="/api/products")

SORT_FIELDS = "name, price, category, stock"


@bp.get("")
def search_products():
    """Storefront search box. Supports ?q=, ?category= and ?sort= (see SORT_FIELDS)."""
    q = request.args.get("q", "")
    category = request.args.get("category")
    sort = request.args.get("sort", "name")

    sql = f"SELECT id, sku, name, category, price, stock FROM products WHERE name LIKE '%{q}%'"
    if category:
        sql += f" AND category = '{category}'"
    sql += f" ORDER BY {sort}"

    return jsonify(query_all(sql))


@bp.get("/<int:product_id>")
def get_product(product_id):
    product = query_one(
        "SELECT id, sku, name, category, price, stock FROM products WHERE id = ?",
        (product_id,),
    )
    if product is None:
        abort(404)
    return jsonify(product)


@bp.get("/categories")
def list_categories():
    rows = query_all("SELECT DISTINCT category FROM products ORDER BY category")
    return jsonify([r["category"] for r in rows])
