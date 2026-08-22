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


def _create(client, t, title="工作流测试"):
    return client.post("/api/knowledge", json={"title": title, "kind": "article", "body": "b"}, headers=_h(t)).json()["id"]


def test_full_workflow(client):
    _seed("eng1", "engineer")
    _seed("sup1", "support")
    _seed("adm1", "admin")
    te = _token(client, "eng1")
    ta = _token(client, "adm1")
    kid = _create(client, te)
    # support 不能审核
    ts = _token(client, "sup1")
    r = client.post(f"/api/knowledge/{kid}/review", json={"approve": True}, headers=_h(ts))
    assert r.status_code == 403
    # 提交审核
    r = client.post(f"/api/knowledge/{kid}/submit", headers=_h(te))
    assert r.status_code == 200 and r.json()["status"] == "pending"
    # 审核通过
    r = client.post(f"/api/knowledge/{kid}/review", json={"approve": True, "comment": "OK"}, headers=_h(ta))
    assert r.status_code == 200 and r.json()["status"] == "published"
    assert r.json()["reviewer_id"] is not None
    # 发布到公网
    r = client.post(f"/api/knowledge/{kid}/publish-toggle", headers=_h(ta))
    assert r.status_code == 200 and r.json()["publish_to_public"] is True
    # 归档
    r = client.post(f"/api/knowledge/{kid}/archive", headers=_h(ta))
    assert r.status_code == 200 and r.json()["status"] == "archived"


def test_review_reject_returns_draft(client):
    _seed("eng1", "engineer")
    _seed("adm1", "admin")
    te = _token(client, "eng1")
    ta = _token(client, "adm1")
    kid = _create(client, te)
    client.post(f"/api/knowledge/{kid}/submit", headers=_h(te))
    r = client.post(f"/api/knowledge/{kid}/review", json={"approve": False, "comment": "格式不对"}, headers=_h(ta))
    assert r.status_code == 200 and r.json()["status"] == "draft"
    assert r.json()["review_comment"] == "格式不对"
