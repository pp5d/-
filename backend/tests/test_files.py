import io

from app.db import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def _seed():
    db = SessionLocal()
    db.add(User(username="eng1", role="engineer", hashed_password=hash_password("secret123")))
    db.commit()
    db.close()


def _token(client):
    return client.post("/api/auth/login", json={"username": "eng1", "password": "secret123"}).json()["access_token"]


def test_upload_image_and_download(client):
    _seed()
    t = _token(client)
    h = {"Authorization": f"Bearer {t}"}
    kid = client.post("/api/knowledge", json={"title": "t", "kind": "article", "body": "b"}, headers=h).json()["id"]
    files = {"file": ("报警图.jpg", io.BytesIO(b"\xff\xd8\xff fakejpg"), "image/jpeg")}
    r = client.post(f"/api/files?knowledge_id={kid}", files=files, headers=h)
    assert r.status_code == 200
    aid = r.json()["id"]
    assert r.json()["content_type"] == "image"
    r2 = client.get(f"/api/files/{aid}/download", headers=h)
    assert r2.status_code == 200


def test_upload_rejects_wrong_type(client):
    _seed()
    t = _token(client)
    h = {"Authorization": f"Bearer {t}"}
    kid = client.post("/api/knowledge", json={"title": "t", "kind": "article", "body": "b"}, headers=h).json()["id"]
    files = {"file": ("脚本.exe", io.BytesIO(b"MZ"), "application/octet-stream")}
    r = client.post(f"/api/files?knowledge_id={kid}", files=files, headers=h)
    assert r.status_code == 400
