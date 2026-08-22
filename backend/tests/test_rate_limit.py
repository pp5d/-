from app.config import settings
from app.db import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def test_rate_limit(client, monkeypatch):
    monkeypatch.setattr(settings, "QA_RATE_LIMIT", 2)
    db = SessionLocal()
    db.add(User(username="eng1", role="engineer", hashed_password=hash_password("secret123")))
    db.commit()
    db.close()
    t = client.post("/api/auth/login", json={"username": "eng1", "password": "secret123"}).json()["access_token"]
    h = {"Authorization": f"Bearer {t}"}
    # 前两次未命中（会建单），第三次触发限流
    for _ in range(2):
        client.post("/api/qa", json={"question": "q1"}, headers=h)
    r = client.post("/api/qa", json={"question": "q2"}, headers=h)
    assert r.status_code == 429
