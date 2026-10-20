def test_list_items_empty(client):
    r = client.get("/v1/items")
    assert r.status_code == 200
    assert r.json() == []


def test_create_item_has_no_category(client):
    r = client.post("/v1/items", json={"name": "Book", "price": 12.5})
    assert r.status_code == 201
    assert r.json() == {"id": 1, "name": "Book", "price": 12.5}


def test_get_item(client):
    client.post("/v1/items", json={"name": "Pen", "price": 2})
    r = client.get("/v1/items/1")
    assert r.status_code == 200
    assert r.json()["name"] == "Pen"


def test_get_missing_item_returns_404(client):
    assert client.get("/v1/items/999").status_code == 404


def test_create_item_invalid_price(client):
    r = client.post("/v1/items", json={"name": "Bad", "price": -5})
    assert r.status_code == 422


def test_deprecation_headers_present(client):
    r = client.get("/v1/items")
    assert r.headers["Deprecation"] == "true"
    assert "Sunset" in r.headers
    assert "successor-version" in r.headers["Link"]


def test_v1_marked_deprecated_in_openapi(client):
    schema = client.get("/openapi.json").json()
    assert schema["paths"]["/v1/items"]["get"]["deprecated"] is True
