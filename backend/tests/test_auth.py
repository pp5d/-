import pytest

from app.config import settings
from app.db import SessionLocal
from app.models.user import User


def _make_user(username="eng1", role="engineer", password="secret123"):
    from app.core.security import hash_password

    db = SessionLocal()
    db.add(User(username=username, role=role, hashed_password=hash_password(password)))
    db.commit()
    db.close()


def test_register_public_mode(client, monkeypatch):
    monkeypatch.setattr(settings, "APP_MODE", "public")
    r = client.post("/api/auth/register", json={"username": "sale1", "password": "secret123", "phone": "13800000000"})
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["role"] == "support"
    assert data["access_token"]


def test_register_forbidden_in_full_mode(client):
    r = client.post("/api/auth/register", json={"username": "sale2", "password": "secret123"})
    assert r.status_code == 403


def test_register_duplicate_username(client, monkeypatch):
    monkeypatch.setattr(settings, "APP_MODE", "public")
    client.post("/api/auth/register", json={"username": "sale3", "password": "secret123"})
    r = client.post("/api/auth/register", json={"username": "sale3", "password": "secret123"})
    assert r.status_code == 400


def test_login_ok(client):
    _make_user(password="secret123")
    r = client.post("/api/auth/login", json={"username": "eng1", "password": "secret123"})
    assert r.status_code == 200
    assert r.json()["user"]["role"] == "engineer"


def test_login_wrong_password(client):
    _make_user(password="secret123")
    r = client.post("/api/auth/login", json={"username": "eng1", "password": "wrong1"})
    assert r.status_code == 401


def test_login_disabled_account(client):
    from app.core.security import hash_password

    db = SessionLocal()
    db.add(User(username="eng2", role="engineer", hashed_password=hash_password("secret123"), is_active=False))
    db.commit()
    db.close()
    r = client.post("/api/auth/login", json={"username": "eng2", "password": "secret123"})
    assert r.status_code == 403


def test_me_requires_token(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_me_ok(client):
    _make_user(password="secret123")
    token = client.post("/api/auth/login", json={"username": "eng1", "password": "secret123"}).json()["access_token"]
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["username"] == "eng1"
