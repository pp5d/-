from app.config import settings
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


def test_import_requires_token(client):
    r = client.post("/api/sync/import", json={"knowledge": []}, headers={"X-Sync-Token": "wrong"})
    assert r.status_code == 401


def test_import_ok(client, monkeypatch):
    monkeypatch.setattr(settings, "PUBLIC_API_TOKEN", "test-token")
    monkeypatch.setattr(settings, "APP_MODE", "public")
    r = client.post("/api/sync/import", json={"knowledge": []}, headers={"X-Sync-Token": "test-token"})
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_push_requires_admin(client):
    _seed("eng1", "engineer")
    t = _token(client, "eng1")
    r = client.post("/api/sync/push", headers=_h(t))
    assert r.status_code == 403


def test_import_nonempty_creates_sync_user(client, monkeypatch):
    monkeypatch.setattr(settings, "PUBLIC_API_TOKEN", "test-token")
    monkeypatch.setattr(settings, "APP_MODE", "public")
    snapshot = {
        "knowledge": [
            {
                "title": "同步知识",
                "kind": "article",
                "body": "正文",
                "aliases": ["别名"],
                "case_fields": None,
                "category": "",
                "tags": [],
                "machines": "",
                "chunks": [{"content": "正文", "embedding": [0.1] * 512}],
                "attachments": [],
            }
        ]
    }
    r = client.post("/api/sync/import", json=snapshot, headers={"X-Sync-Token": "test-token"})
    assert r.status_code == 200
    assert r.json()["count"] == 1
    from app.db import SessionLocal
    from app.models.knowledge import KnowledgeItem
    from sqlalchemy import select
    db = SessionLocal()
    item = db.scalar(select(KnowledgeItem).where(KnowledgeItem.title == "同步知识"))
    assert item is not None
    assert item.publish_to_public is True
    db.close()
