def _reg(client, username):
    from app.db import SessionLocal
    from app.models.user import User
    from app.core.security import hash_password
    db = SessionLocal()
    db.add(User(username=username, role="engineer", hashed_password=hash_password("secret123")))
    db.commit()
    db.close()


def _token(client, username):
    return client.post("/api/auth/login", json={"username": username, "password": "secret123"}).json()["access_token"]


def _h(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_and_get(client):
    _reg(client, "eng1")
    t = _token(client, "eng1")
    r = client.post("/api/knowledge", json={"title": "模保原理", "kind": "article", "body": "正文", "aliases": ["模保是什么"]}, headers=_h(t))
    assert r.status_code == 200
    kid = r.json()["id"]
    assert r.json()["status"] == "draft"
    r2 = client.get(f"/api/knowledge/{kid}", headers=_h(t))
    assert r2.status_code == 200
    assert r2.json()["title"] == "模保原理"


def test_list_shows_draft_to_engineer(client):
    _reg(client, "eng1")
    t = _token(client, "eng1")
    client.post("/api/knowledge", json={"title": "草稿", "kind": "qa", "body": "b"}, headers=_h(t))
    r = client.get("/api/knowledge", headers=_h(t))
    assert r.status_code == 200
    assert any(x["title"] == "草稿" for x in r.json())


def test_update_increments_version_and_requires_author(client):
    _reg(client, "eng1")
    _reg(client, "eng2")
    t1 = _token(client, "eng1")
    t2 = _token(client, "eng2")
    kid = client.post("/api/knowledge", json={"title": "t", "kind": "qa", "body": "b"}, headers=_h(t1)).json()["id"]
    r = client.put(f"/api/knowledge/{kid}", json={"body": "新正文"}, headers=_h(t1))
    assert r.status_code == 200
    assert r.json()["version"] == 2
    # 非作者且非 admin 无权改
    r2 = client.put(f"/api/knowledge/{kid}", json={"body": "x"}, headers=_h(t2))
    assert r2.status_code == 403
