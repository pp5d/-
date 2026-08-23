from app.db import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def _admin_token(client):
    db = SessionLocal()
    db.add(User(username="adm", role="admin", hashed_password=hash_password("secret123")))
    db.commit()
    db.close()
    return client.post("/api/auth/login", json={"username": "adm", "password": "secret123"}).json()["access_token"]


def test_overview_requires_admin(client):
    r = client.get("/api/stats/overview")
    assert r.status_code == 401


def test_overview_ok(client):
    t = _admin_token(client)
    r = client.get("/api/stats/overview", headers={"Authorization": f"Bearer {t}"})
    assert r.status_code == 200
    assert "knowledge_total" in r.json()


def test_top_questions_ok(client):
    t = _admin_token(client)
    r = client.get("/api/stats/top-questions", headers={"Authorization": f"Bearer {t}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)
