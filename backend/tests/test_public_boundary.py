import io

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


def _create_and_publish(client, t, publish=False):
    kid = client.post("/api/knowledge", json={"title": "公网测试", "kind": "article", "body": "正文"}, headers=_h(t)).json()["id"]
    client.post(f"/api/knowledge/{kid}/submit", headers=_h(t))
    client.post(f"/api/knowledge/{kid}/review", json={"approve": True}, headers=_h(t))
    if publish:
        client.post(f"/api/knowledge/{kid}/publish-toggle", headers=_h(t))
    return kid


def test_public_support_cannot_read_unpublished_public(client, monkeypatch):
    monkeypatch.setattr(settings, "APP_MODE", "public")
    _seed("eng1", "engineer")
    _seed("sup1", "support")
    te = _token(client, "eng1")
    ts = _token(client, "sup1")
    kid = _create_and_publish(client, te, publish=False)
    r = client.get(f"/api/knowledge/{kid}", headers=_h(ts))
    assert r.status_code == 403


def test_public_support_cannot_edit_draft(client, monkeypatch):
    monkeypatch.setattr(settings, "APP_MODE", "public")
    _seed("sup1", "support")
    ts = _token(client, "sup1")
    kid = client.post("/api/knowledge", json={"title": "草稿", "kind": "article", "body": "b"}, headers=_h(ts)).json()["id"]
    r = client.put(f"/api/knowledge/{kid}", json={"body": "改"}, headers=_h(ts))
    assert r.status_code == 403


def test_edit_published_returns_draft(client):
    _seed("eng1", "engineer")
    te = _token(client, "eng1")
    kid = _create_and_publish(client, te, publish=False)
    r = client.put(f"/api/knowledge/{kid}", json={"body": "改"}, headers=_h(te))
    assert r.status_code == 200
    assert r.json()["status"] == "draft"


def test_support_cannot_download_unpublished_attachment(client):
    _seed("eng1", "engineer")
    _seed("sup1", "support")
    te = _token(client, "eng1")
    ts = _token(client, "sup1")
    kid = client.post("/api/knowledge", json={"title": "附件测试", "kind": "article", "body": "b"}, headers=_h(te)).json()["id"]
    # eng1 给草稿上传附件（未发布）
    files = {"file": ("图.jpg", io.BytesIO(b"\xff\xd8\xff fake"), "image/jpeg")}
    r = client.post(f"/api/files?knowledge_id={kid}", files=files, headers=_h(te))
    assert r.status_code == 200
    aid = r.json()["id"]
    # support 无法下载未发布知识的附件
    r2 = client.get(f"/api/files/{aid}/download", headers=_h(ts))
    assert r2.status_code == 403


def test_support_cannot_upload_to_others_knowledge(client):
    _seed("eng1", "engineer")
    _seed("sup1", "support")
    te = _token(client, "eng1")
    ts = _token(client, "sup1")
    kid = client.post("/api/knowledge", json={"title": "上传越权", "kind": "article", "body": "b"}, headers=_h(te)).json()["id"]
    files = {"file": ("图.jpg", io.BytesIO(b"\xff\xd8\xff fake"), "image/jpeg")}
    r = client.post(f"/api/files?knowledge_id={kid}", files=files, headers=_h(ts))
    assert r.status_code == 403
