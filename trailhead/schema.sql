DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS promo_codes;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,
    tier        TEXT NOT NULL DEFAULT 'standard',
    created_at  TEXT NOT NULL
);

CREATE TABLE products (
    id        INTEGER PRIMARY KEY,
    sku       TEXT NOT NULL UNIQUE,
    name      TEXT NOT NULL,
    category  TEXT NOT NULL,
    price     REAL NOT NULL,
    stock     INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE promo_codes (
    code         TEXT PRIMARY KEY,
    percent_off  REAL NOT NULL,
    active       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE orders (
    id           INTEGER PRIMARY KEY,
    customer_id  INTEGER NOT NULL REFERENCES customers (id),
    status       TEXT NOT NULL DEFAULT 'placed',
    promo_code   TEXT,
    subtotal     REAL NOT NULL,
    discount     REAL NOT NULL DEFAULT 0,
    tax          REAL NOT NULL,
    shipping     REAL NOT NULL,
    total        REAL NOT NULL,
    created_at   TEXT NOT NULL
);

CREATE TABLE order_items (
    id          INTEGER PRIMARY KEY,
    order_id    INTEGER NOT NULL REFERENCES orders (id),
    product_id  INTEGER NOT NULL REFERENCES products (id),
    quantity    INTEGER NOT NULL,
    unit_price  REAL NOT NULL
);
