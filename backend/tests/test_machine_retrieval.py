from app.db import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def _seed():
    db = SessionLocal()
    db.add(User(username="eng1", role="engineer", hashed_password=hash_password("secret123")))
    db.commit()
    db.close()


def _publish(client, title, body, machines, aliases):
    t = client.post("/api/auth/login", json={"username": "eng1", "password": "secret123"}).json()["access_token"]
    h = {"Authorization": f"Bearer {t}"}
    kid = client.post("/api/knowledge", json={"title": title, "kind": "article", "body": body, "machines": machines, "aliases": aliases}, headers=h).json()["id"]
    client.post(f"/api/knowledge/{kid}/submit", headers=h)
    client.post(f"/api/knowledge/{kid}/review", json={"approve": True}, headers=h)
    return kid


def test_machine_weighting(client):
    _seed()
    _publish(client, "A5 合模参数", "A5 机型的合模压力设定说明。", "A5", ["A5 合模"])
    _publish(client, "A6 合模参数", "A6 机型的合模压力设定说明。", "A6", ["A6 合模"])
    from app.db import SessionLocal
    from app.services.retrieval import search
    db = SessionLocal()
    results = search("合模压力怎么设定", db, machine="A5")
    db.close()
    assert len(results) > 0
    # 指定 A5 时，A5 的知识应排在最前
    assert "A5" in results[0][2].machines
