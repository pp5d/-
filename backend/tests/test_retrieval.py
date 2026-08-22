from app.db import SessionLocal
from app.models.chunk import Chunk
from app.models.knowledge import KnowledgeItem
from app.models.user import User
from app.core.security import hash_password
from app.services.retrieval import search


def _seed():
    db = SessionLocal()
    db.add(User(username="eng1", role="engineer", hashed_password=hash_password("secret123")))
    db.commit()
    db.close()


def _publish_knowledge(client, title, body, aliases):
    t = client.post("/api/auth/login", json={"username": "eng1", "password": "secret123"}).json()["access_token"]
    h = {"Authorization": f"Bearer {t}"}
    kid = client.post("/api/knowledge", json={"title": title, "kind": "article", "body": body, "aliases": aliases}, headers=h).json()["id"]
    client.post(f"/api/knowledge/{kid}/submit", headers=h)
    client.post(f"/api/knowledge/{kid}/review", json={"approve": True}, headers=h)
    return kid


def test_search_finds_relevant(client):
    _seed()
    _publish_knowledge(client, "模保原理", "模具保护通过低压低速合模实现，防止压坏模具。", ["模保是什么", "模具保护"])
    _publish_knowledge(client, "顶出原理", "顶出机构把制品从模具中顶出。", ["顶出", "脱模"])
    db = SessionLocal()
    results = search("模保报警怎么处理", db)
    db.close()
    assert len(results) > 0
    assert "模保" in results[0][2].title
