import os

import pytest
from fastapi.testclient import TestClient

# app.config validates JWT_SECRET at import time, so set it before the app is
# imported (the app is imported lazily inside the fixtures below).
os.environ.setdefault("JWT_SECRET", "test-secret-" + "x" * 32)


@pytest.fixture(autouse=True)
def reset_state():
    from app import store
    from app.auth import users
    from app.ratelimit import limiter

    store.reset()
    users.reset()
    limiter.reset()  # rate-limit counters must not leak between tests


def _make_client(username: str, password: str, role: str | None) -> TestClient:
    from app.auth import users
    from app.main import app

    c = TestClient(app)
    if role is None:
        return c
    users.create(username, password, role=role)
    r = c.post("/auth/token", data={"username": username, "password": password})
    assert r.status_code == 200, r.text
    c.headers["Authorization"] = f"Bearer {r.json()['access_token']}"
    return c


@pytest.fixture
def anon_client():
    """No credentials."""
    return _make_client("", "", None)


@pytest.fixture
def client():
    """Logged in as an admin, so the pre-existing tests keep working unchanged."""
    return _make_client("admin", "admin-password", "admin")


@pytest.fixture
def user_client():
    """Logged in as a regular (non-admin) user."""
    return _make_client("alice", "alice-password", "user")
