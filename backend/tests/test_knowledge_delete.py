from app.db import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def _reg(username):
    db = SessionLocal()
    db.add(User(username=username, role="engineer", hashed_password=hash_password("secret123")))
    db.commit()
    db.close()


def _token(client, username):
    return client.post("/api/auth/login", json={"username": username, "password": "secret123"}).json()["access_token"]


def _h(t):
    return {"Authorization": f"Bearer {t}"}


def test_delete_draft(client):
    _reg("eng1")
    t = _token(client, "eng1")
    kid = client.post("/api/knowledge", json={"title": "删我", "kind": "qa", "body": "b"}, headers=_h(t)).json()["id"]
    r = client.delete(f"/api/knowledge/{kid}", headers=_h(t))
    assert r.status_code == 200
    assert client.get(f"/api/knowledge/{kid}", headers=_h(t)).status_code == 404


def test_delete_published_forbidden(client):
    _reg("eng1")
    t = _token(client, "eng1")
    kid = client.post("/api/knowledge", json={"title": "已发布", "kind": "qa", "body": "b"}, headers=_h(t)).json()["id"]
    client.post(f"/api/knowledge/{kid}/submit", headers=_h(t))
    client.post(f"/api/knowledge/{kid}/review", json={"approve": True}, headers=_h(t))
    r = client.delete(f"/api/knowledge/{kid}", headers=_h(t))
    assert r.status_code == 400
