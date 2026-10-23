from datetime import UTC, datetime, timedelta

import jwt

from app import config
from app.auth import users


# ---------- login ----------
def test_login_returns_bearer_token(anon_client):
    users.create("bob", "bob-password")
    r = anon_client.post("/auth/token", data={"username": "bob", "password": "bob-password"})
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer" and body["access_token"]


def test_login_wrong_password(anon_client):
    users.create("bob", "bob-password")
    r = anon_client.post("/auth/token", data={"username": "bob", "password": "nope"})
    assert r.status_code == 401


def test_login_unknown_user(anon_client):
    r = anon_client.post("/auth/token", data={"username": "ghost", "password": "whatever1"})
    assert r.status_code == 401


def test_login_username_is_case_insensitive(anon_client):
    users.create("Bob", "bob-password")
    r = anon_client.post("/auth/token", data={"username": "BOB", "password": "bob-password"})
    assert r.status_code == 200


# ---------- authentication on protected routes ----------
def test_items_require_token(anon_client):
    for path in ["/items", "/v1/items", "/v2/items"]:
        assert anon_client.get(path).status_code == 401


def test_public_routes_need_no_token(anon_client):
    assert anon_client.get("/health").status_code == 200
    assert anon_client.get("/").status_code == 200


def test_garbage_token_rejected(anon_client):
    r = anon_client.get("/v2/items", headers={"Authorization": "Bearer not.a.jwt"})
    assert r.status_code == 401


def test_expired_token_rejected(anon_client):
    users.create("bob", "bob-password")
    expired = jwt.encode(
        {"sub": "bob", "exp": datetime.now(UTC) - timedelta(minutes=1)},
        config.JWT_SECRET,
        algorithm="HS256",
    )
    r = anon_client.get("/v2/items", headers={"Authorization": f"Bearer {expired}"})
    assert r.status_code == 401


def test_token_signed_with_wrong_secret_rejected(anon_client):
    users.create("bob", "bob-password")
    forged = jwt.encode(
        {"sub": "bob", "exp": datetime.now(UTC) + timedelta(minutes=5)},
        "some-other-secret-that-is-long-enough-123",
        algorithm="HS256",
    )
    r = anon_client.get("/v2/items", headers={"Authorization": f"Bearer {forged}"})
    assert r.status_code == 401


def test_unsigned_alg_none_token_rejected(anon_client):
    users.create("bob", "bob-password")
    none_token = jwt.encode({"sub": "bob"}, key=None, algorithm="none")
    r = anon_client.get("/v2/items", headers={"Authorization": f"Bearer {none_token}"})
    assert r.status_code == 401


def test_token_for_deleted_or_disabled_user_rejected(user_client):
    assert user_client.get("/v2/items").status_code == 200
    users.get("alice")["disabled"] = True
    assert user_client.get("/v2/items").status_code == 401


# ---------- authorization (roles) ----------
def test_regular_user_can_read_but_not_create(user_client, client):
    client.post("/v2/items", json={"name": "Pen", "price": 2})
    assert user_client.get("/v2/items").status_code == 200
    r = user_client.post("/v2/items", json={"name": "Hack", "price": 1})
    assert r.status_code == 403


def test_regular_user_cannot_create_on_any_route(user_client):
    for path in ["/items", "/v1/items", "/v2/items"]:
        assert user_client.post(path, json={"name": "X", "price": 1}).status_code == 403


def test_me_endpoint(user_client):
    assert user_client.get("/auth/me").json() == {"username": "alice", "role": "user"}


# ---------- admin user management ----------
def test_admin_can_create_user_who_can_then_login(client, anon_client):
    r = client.post("/auth/users", json={"username": "carol", "password": "carol-password"})
    assert r.status_code == 201 and r.json() == {"username": "carol", "role": "user"}
    assert "password" not in r.text
    login = anon_client.post("/auth/token", data={"username": "carol", "password": "carol-password"})
    assert login.status_code == 200


def test_duplicate_username_conflict(client):
    body = {"username": "carol", "password": "carol-password"}
    assert client.post("/auth/users", json=body).status_code == 201
    assert client.post("/auth/users", json=body).status_code == 409


def test_regular_user_cannot_create_users(user_client):
    r = user_client.post("/auth/users", json={"username": "evil", "password": "evil-password"})
    assert r.status_code == 403


def test_anonymous_cannot_create_users(anon_client):
    r = anon_client.post("/auth/users", json={"username": "evil", "password": "evil-password"})
    assert r.status_code == 401


def test_weak_password_rejected(client):
    r = client.post("/auth/users", json={"username": "carol", "password": "short"})
    assert r.status_code == 422
