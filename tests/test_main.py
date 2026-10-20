def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "Hello from FastAPI"}


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
