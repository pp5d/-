from app.config import settings
from app.db import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def _seed(username, role):
    db = SessionLocal()
    db.add(User(username=username, role=role, hashed_password=hash_password("secret123")))
    db.commit()
    db.close()


def _token(client, username):
    return client.post("/api/auth/login", json={"username": username, "password": "secret123"}).json()["access_token"]


def _h(t):
    return {"Authorization": f"Bearer {t}"}


def test_import_requires_token(client):
    r = client.post("/api/sync/import", json={"knowledge": []}, headers={"X-Sync-Token": "wrong"})
    assert r.status_code == 401


def test_import_ok(client, monkeypatch):
    monkeypatch.setattr(settings, "PUBLIC_API_TOKEN", "test-token")
    r = client.post("/api/sync/import", json={"knowledge": []}, headers={"X-Sync-Token": "test-token"})
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_push_requires_admin(client):
    _seed("eng1", "engineer")
    t = _token(client, "eng1")
    r = client.post("/api/sync/push", headers=_h(t))
    assert r.status_code == 403
