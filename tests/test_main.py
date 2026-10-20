import pytest
from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def reset_state():
    main.items.clear()
    main.next_id = 1


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "Hello from FastAPI"}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_items_empty():
    r = client.get("/items")
    assert r.status_code == 200
    assert r.json() == []


def test_create_item():
    r = client.post("/items", json={"name": "Book", "price": 12.5})
    assert r.status_code == 201
    assert r.json() == {"id": 1, "name": "Book", "price": 12.5}


def test_get_item_after_create():
    client.post("/items", json={"name": "Pen", "price": 2})
    r = client.get("/items/1")
    assert r.status_code == 200
    assert r.json()["name"] == "Pen"


def test_get_missing_item_returns_404():
    r = client.get("/items/999")
    assert r.status_code == 404


def test_create_item_invalid_price():
    r = client.post("/items", json={"name": "Bad", "price": -5})
    assert r.status_code == 422


def test_create_item_missing_name():
    r = client.post("/items", json={"price": 5})
    assert r.status_code == 422
