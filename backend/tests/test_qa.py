from app.db import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def _seed():
    db = SessionLocal()
    db.add(User(username="eng1", role="engineer", hashed_password=hash_password("secret123")))
    db.commit()
    db.close()


def test_qa_hit(client, monkeypatch):
    _seed()
    t = client.post("/api/auth/login", json={"username": "eng1", "password": "secret123"}).json()["access_token"]
    h = {"Authorization": f"Bearer {t}"}
    kid = client.post("/api/knowledge", json={"title": "模保原理", "kind": "article", "body": "模具保护通过低压低速合模实现。", "aliases": ["模保"]}, headers=h).json()["id"]
    client.post(f"/api/knowledge/{kid}/submit", headers=h)
    client.post(f"/api/knowledge/{kid}/review", json={"approve": True}, headers=h)
    # 打桩避免真实调用 DeepSeek
    def fake_generate(question, contexts):
        return "模保是模具保护功能，通过低压低速合模实现。"
    monkeypatch.setattr("app.routers.qa.generate", fake_generate)
    r = client.post("/api/qa", json={"question": "模保是什么"}, headers=h)
    assert r.status_code == 200
    data = r.json()
    assert data["hit"] is True
    assert data["answer"]
    assert data["sources"][0]["title"] == "模保原理"


def test_qa_miss(client):
    _seed()
    t = client.post("/api/auth/login", json={"username": "eng1", "password": "secret123"}).json()["access_token"]
    h = {"Authorization": f"Bearer {t}"}
    r = client.post("/api/qa", json={"question": "一个完全无关的问题xyz"}, headers=h)
    assert r.status_code == 200
    assert r.json()["hit"] is False
