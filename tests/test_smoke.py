def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_search_returns_products(client):
    resp = client.get("/api/products?q=Tent")
    assert resp.status_code == 200
    assert resp.get_json()[0]["name"] == "Test Tent"
