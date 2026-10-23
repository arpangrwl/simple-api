"""In-memory user store (same style as app/store.py).

NOTE: users are lost when the container restarts. The admin is re-created
from env vars on every startup; other users should move to a real database
(SQLite/Postgres) when you outgrow the POC.
"""
from app.auth.security import hash_password

_users: dict[str, dict] = {}


def create(username: str, password: str, role: str = "user") -> dict | None:
    username = username.lower()
    if username in _users:
        return None
    user = {
        "username": username,
        "password_hash": hash_password(password),
        "role": role,
        "disabled": False,
    }
    _users[username] = user
    return user


def get(username: str) -> dict | None:
    return _users.get(username.lower())


def reset() -> None:
    _users.clear()
