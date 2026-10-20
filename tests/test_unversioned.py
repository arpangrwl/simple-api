def test_unversioned_behaves_like_current_version(client):
    created = client.post("/items", json={"name": "Pen", "price": 2, "category": "office"})
    assert created.status_code == 201
    assert created.json()["category"] == "office"
    assert client.get("/v2/items/1").json() == created.json()


def test_unversioned_has_no_deprecation_headers(client):
    r = client.get("/items")
    assert r.status_code == 200
    assert "Deprecation" not in r.headers


def test_unversioned_routes_hidden_from_docs(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert "/items" not in paths
    assert "/v1/items" in paths and "/v2/items" in paths
