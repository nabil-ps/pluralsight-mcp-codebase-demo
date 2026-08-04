import pytest

from trailhead import create_app
from trailhead.db import init_db


@pytest.fixture
def app(tmp_path):
    db_path = tmp_path / "test.db"
    conn = init_db(db_path)
    conn.execute(
        "INSERT INTO products (sku, name, category, price, stock)"
        " VALUES ('TH-0001', 'Test Tent', 'tents', 100.00, 5)"
    )
    conn.commit()
    conn.close()
    return create_app({"DATABASE": str(db_path), "TESTING": True})


@pytest.fixture
def client(app):
    return app.test_client()
