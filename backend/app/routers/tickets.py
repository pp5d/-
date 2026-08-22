from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db import get_db
from app.models.knowledge import KnowledgeItem
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket import TicketAnswer, TicketCreate, TicketOut

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketOut])
def list_tickets(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(Ticket).order_by(Ticket.id.desc())
    if user.role == "support":
        stmt = stmt.where(Ticket.asker_id == user.id)
    return db.scalars(stmt).all()


@router.post("", response_model=TicketOut)
def create_ticket(body: TicketCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = Ticket(question=body.question, asker_id=user.id)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.post("/{ticket_id}/answer", response_model=TicketOut)
def answer_ticket(ticket_id: int, body: TicketAnswer, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role not in ("engineer", "admin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "无权答复")
    t = db.get(Ticket, ticket_id)
    if t is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "工单不存在")
    t.answer = body.answer
    t.assignee_id = user.id
    t.status = "answered"
    t.answered_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(t)
    return t


@router.post("/{ticket_id}/close", response_model=TicketOut)
def close_ticket(ticket_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role not in ("engineer", "admin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "无权关闭")
    t = db.get(Ticket, ticket_id)
    if t is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "工单不存在")
    t.status = "closed"
    db.commit()
    db.refresh(t)
    return t


@router.post("/{ticket_id}/to-knowledge", response_model=TicketOut)
def to_knowledge(ticket_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role not in ("engineer", "admin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "无权操作")
    t = db.get(Ticket, ticket_id)
    if t is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "工单不存在")
    if not t.answer:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "请先答复再沉淀")
    if t.knowledge_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "该工单已沉淀为知识")
    item = KnowledgeItem(
        title=t.question[:200],
        kind="qa",
        body=t.answer,
        aliases=[t.question] if t.question else [],
        category="",
        tags=[],
        machines="",
        author_id=user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    t.knowledge_id = item.id
    db.commit()
    db.refresh(t)
    return t
