from app.db import SessionLocal
from app.models.chunk import Chunk
from app.models.user import User
from app.core.security import hash_password
from app.services.indexing import chunk_text


def _seed():
    db = SessionLocal()
    db.add(User(username="eng1", role="engineer", hashed_password=hash_password("secret123")))
    db.commit()
    db.close()


def test_chunk_text():
    c = chunk_text("第一段内容\n\n第二段内容")
    assert len(c) == 2
    assert "第一段" in c[0]


def test_reindex_creates_chunks(client):
    _seed()
    t = client.post("/api/auth/login", json={"username": "eng1", "password": "secret123"}).json()["access_token"]
    h = {"Authorization": f"Bearer {t}"}
    kid = client.post("/api/knowledge", json={"title": "模保原理", "kind": "article", "body": "模具保护通过低压低速合模实现。", "aliases": ["模保是什么"]}, headers=h).json()["id"]
    client.post(f"/api/knowledge/{kid}/submit", headers=h)
    r = client.post(f"/api/knowledge/{kid}/review", json={"approve": True}, headers=h)
    assert r.status_code == 200
    db = SessionLocal()
    chunks = db.query(Chunk).filter(Chunk.knowledge_id == kid).all()
    assert len(chunks) >= 2  # 正文 1 块 + 别名 1 块
    assert all(len(c.embedding) == 512 for c in chunks)
    db.close()


def test_reindex_empty_body_no_chunks(client):
    _seed()
    t = client.post("/api/auth/login", json={"username": "eng1", "password": "secret123"}).json()["access_token"]
    h = {"Authorization": f"Bearer {t}"}
    kid = client.post("/api/knowledge", json={"title": "空", "kind": "article", "body": ""}, headers=h).json()["id"]
    client.post(f"/api/knowledge/{kid}/submit", headers=h)
    r = client.post(f"/api/knowledge/{kid}/review", json={"approve": True}, headers=h)
    assert r.status_code == 200
    db = SessionLocal()
    assert len(db.query(Chunk).filter(Chunk.knowledge_id == kid).all()) == 0
    db.close()
