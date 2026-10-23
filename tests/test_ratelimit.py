from app import config
from app.auth import users


def _bad_login(c):
    return c.post("/auth/token", data={"username": "ghost", "password": "whatever1"})


def test_login_is_rate_limited(anon_client):
    limit = int(config.LOGIN_RATE_LIMIT.split("/")[0])
    for _ in range(limit):
        assert _bad_login(anon_client).status_code == 401  # wrong password, but allowed
    assert _bad_login(anon_client).status_code == 429       # attempt limit+1 is blocked


def test_correct_password_is_also_blocked_once_limited(anon_client):
    """An attacker who burned the quota can't get a free guess in afterwards."""
    users.create("bob", "bob-password")
    limit = int(config.LOGIN_RATE_LIMIT.split("/")[0])
    for _ in range(limit):
        _bad_login(anon_client)
    r = anon_client.post("/auth/token", data={"username": "bob", "password": "bob-password"})
    assert r.status_code == 429


def test_health_is_never_rate_limited(anon_client):
    for _ in range(300):  # well over DEFAULT_RATE_LIMIT
        assert anon_client.get("/health").status_code == 200


def test_default_limit_applies_to_other_routes(client):
    limit = int(config.DEFAULT_RATE_LIMIT.split("/")[0])
    codes = [client.get("/v2/items").status_code for _ in range(limit + 5)]
    assert codes[:limit].count(200) >= limit - 2  # the fixture's own login used a few
    assert codes[-1] == 429
