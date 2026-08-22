def _login_as(client, username, password):
    return client.post("/api/auth/login", json={"username": username, "password": password}).json()["access_token"]


def _seed_user(client, username, role, password="secret123"):
    from app.db import SessionLocal
    from app.models.user import User
    from app.core.security import hash_password

    db = SessionLocal()
    db.add(User(username=username, role=role, hashed_password=hash_password(password)))
    db.commit()
    db.close()


def _admin_token(client):
    _seed_user(client, "boss", "admin")
    return _login_as(client, "boss", "secret123")


def test_admin_list_users(client):
    _seed_user(client, "eng1", "engineer")
    token = _admin_token(client)
    r = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    usernames = [u["username"] for u in r.json()]
    assert "eng1" in usernames and "boss" in usernames


def test_non_admin_forbidden(client):
    _seed_user(client, "eng1", "engineer")
    token = _login_as(client, "eng1", "secret123")
    r = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_admin_create_user(client):
    token = _admin_token(client)
    r = client.post("/api/users?role=engineer", json={"username": "eng2", "password": "secret123"}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["role"] == "engineer"


def test_admin_disable_user(client):
    _seed_user(client, "eng1", "engineer")
    token = _admin_token(client)
    uid = client.get("/api/users", headers={"Authorization": f"Bearer {token}"}).json()[0]["id"]
    r = client.patch(f"/api/users/{uid}", json={"is_active": False}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["is_active"] is False
    # 被禁用的用户无法登录
    r2 = client.post("/api/auth/login", json={"username": "eng1", "password": "secret123"})
    assert r2.status_code == 403
