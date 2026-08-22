from app.db import SessionLocal
from app.models.knowledge import KINDS, STATUSES, Attachment, KnowledgeItem
from app.models.user import User


def _make_user(username="eng1", role="engineer"):
    db = SessionLocal()
    u = User(username=username, role=role, hashed_password="x")
    db.add(u)
    db.commit()
    db.refresh(u)
    db.close()
    return u.id


def test_create_knowledge_item():
    uid = _make_user()
    db = SessionLocal()
    item = KnowledgeItem(
        title="模保功能原理",
        kind="article",
        body="## 原理\n模具保护通过低压低速合模实现...",
        aliases=["模保是什么", "模具保护"],
        tags=["模保", "合模"],
        category="运动控制",
        machines="A5/A6",
        author_id=uid,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    assert item.id is not None
    assert item.status == "draft"
    assert item.version == 1
    assert item.aliases == ["模保是什么", "模具保护"]
    assert item.publish_to_public is False
    db.close()


def test_attachment():
    uid = _make_user("eng2")
    db = SessionLocal()
    item = KnowledgeItem(title="t", kind="qa", body="b", author_id=uid)
    db.add(item)
    db.commit()
    db.refresh(item)
    att = Attachment(
        knowledge_id=item.id, filename="报警图.jpg", content_type="image", size=1024, storage_path="uploads/abc.jpg"
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    assert att.id is not None
    db.close()


def test_constants():
    assert KINDS == ("qa", "article", "case", "code")
    assert STATUSES == ("draft", "pending", "published", "archived")
