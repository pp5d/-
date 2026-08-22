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


def test_full_ticket_flow(client):
    _seed("sup1", "support")
    _seed("eng1", "engineer")
    ts = _token(client, "sup1")
    te = _token(client, "eng1")
    # support 建单
    r = client.post("/api/tickets", json={"question": "E012 报警怎么处理"}, headers=_h(ts))
    assert r.status_code == 200
    tid = r.json()["id"]
    assert r.json()["status"] == "open"
    # support 不能答复
    assert client.post(f"/api/tickets/{tid}/answer", json={"answer": "x"}, headers=_h(ts)).status_code == 403
    # engineer 答复
    r = client.post(f"/api/tickets/{tid}/answer", json={"answer": "检查模具保护行程开关"}, headers=_h(te))
    assert r.status_code == 200
    assert r.json()["status"] == "answered"
    # 沉淀为知识
    r = client.post(f"/api/tickets/{tid}/to-knowledge", headers=_h(te))
    assert r.status_code == 200
    assert r.json()["knowledge_id"] is not None


def test_support_only_sees_own(client):
    _seed("sup1", "support")
    _seed("sup2", "support")
    ts1 = _token(client, "sup1")
    ts2 = _token(client, "sup2")
    client.post("/api/tickets", json={"question": "q1"}, headers=_h(ts1))
    r = client.get("/api/tickets", headers=_h(ts2))
    assert r.status_code == 200
    assert all(x["question"] != "q1" for x in r.json())
