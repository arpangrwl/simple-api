def test_create_item_default_category(client):
    r = client.post("/v2/items", json={"name": "Book", "price": 12.5})
    assert r.status_code == 201
    assert r.json() == {"id": 1, "name": "Book", "price": 12.5, "category": "general"}


def test_create_item_with_category(client):
    r = client.post("/v2/items", json={"name": "Pen", "price": 2, "category": "office"})
    assert r.status_code == 201
    assert r.json()["category"] == "office"


def test_filter_by_category(client):
    client.post("/v2/items", json={"name": "Pen", "price": 2, "category": "office"})
    client.post("/v2/items", json={"name": "Apple", "price": 1, "category": "food"})
    r = client.get("/v2/items", params={"category": "food"})
    assert [i["name"] for i in r.json()] == ["Apple"]


def test_get_missing_item_returns_404(client):
    assert client.get("/v2/items/999").status_code == 404


def test_create_item_missing_name(client):
    r = client.post("/v2/items", json={"price": 5})
    assert r.status_code == 422


def test_no_deprecation_headers(client):
    r = client.get("/v2/items")
    assert "Deprecation" not in r.headers


def test_v2_not_deprecated_in_openapi(client):
    schema = client.get("/openapi.json").json()
    assert not schema["paths"]["/v2/items"]["get"].get("deprecated", False)


def test_item_created_in_v1_is_visible_in_v2(client):
    client.post("/v1/items", json={"name": "Book", "price": 10})
    r = client.get("/v2/items/1")
    assert r.json()["category"] == "general"
