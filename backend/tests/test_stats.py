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


def test_ticket_response_includes_closed(client):
    from app.db import SessionLocal
    from app.models.ticket import Ticket

    db = SessionLocal()
    db.add(User(username="sup1", role="support", hashed_password=hash_password("secret123")))
    db.add(User(username="eng1", role="engineer", hashed_password=hash_password("secret123")))
    db.commit()
    ts = client.post("/api/auth/login", json={"username": "sup1", "password": "secret123"}).json()["access_token"]
    te = client.post("/api/auth/login", json={"username": "eng1", "password": "secret123"}).json()["access_token"]
    h_s = {"Authorization": f"Bearer {ts}"}
    h_e = {"Authorization": f"Bearer {te}"}
    tid = client.post("/api/tickets", json={"question": "q"}, headers=h_s).json()["id"]
    client.post(f"/api/tickets/{tid}/answer", json={"answer": "a"}, headers=h_e)
    client.post(f"/api/tickets/{tid}/close", headers=h_e)
    ta = _admin_token(client)
    r = client.get("/api/stats/ticket-response", headers={"Authorization": f"Bearer {ta}"})
    assert r.status_code == 200
    assert r.json()["answered_count"] == 1
    db.close()
