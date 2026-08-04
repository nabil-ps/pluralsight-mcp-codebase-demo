import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_all(sql, args=()):
    return [dict(row) for row in get_db().execute(sql, args).fetchall()]


def query_one(sql, args=()):
    row = get_db().execute(sql, args).fetchone()
    return dict(row) if row else None


def init_db(path):
    schema = (Path(__file__).parent / "schema.sql").read_text()
    conn = sqlite3.connect(path)
    conn.executescript(schema)
    conn.commit()
    return conn
