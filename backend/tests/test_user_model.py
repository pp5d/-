from app.models.user import User
from app.db import SessionLocal


def test_create_user():
    db = SessionLocal()
    u = User(username="eng1", role="engineer", hashed_password="x")
    db.add(u)
    db.commit()
    db.refresh(u)
    assert u.id is not None
    assert u.is_active is True
    assert u.role == "engineer"
    db.close()


def test_username_unique():
    db = SessionLocal()
    db.add(User(username="dup", role="support", hashed_password="x"))
    db.commit()
    db.add(User(username="dup", role="support", hashed_password="x"))
    try:
        db.commit()
        assert False, "应抛出唯一约束异常"
    except Exception:
        db.rollback()
    db.close()
