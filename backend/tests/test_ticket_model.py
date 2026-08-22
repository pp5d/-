from app.db import SessionLocal
from app.models.ticket import TICKET_STATUSES, Ticket
from app.models.user import User


def test_create_ticket():
    db = SessionLocal()
    u = User(username="eng1", role="engineer", hashed_password="x")
    db.add(u)
    db.commit()
    db.refresh(u)
    t = Ticket(question="E012 报警怎么处理", asker_id=u.id)
    db.add(t)
    db.commit()
    db.refresh(t)
    assert t.id is not None
    assert t.status == "open"
    assert TICKET_STATUSES == ("open", "answered", "closed")
    db.close()
