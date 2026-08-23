from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db import get_db
from app.models.knowledge import KnowledgeItem
from app.models.ticket import Ticket
from app.models.user import User

router = APIRouter(prefix="/api/stats", tags=["stats"], dependencies=[Depends(require_roles("admin"))])


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    knowledge_total = db.scalar(select(func.count()).select_from(KnowledgeItem)) or 0
    knowledge_published = db.scalar(select(func.count()).select_from(KnowledgeItem).where(KnowledgeItem.status == "published")) or 0
    knowledge_pending = db.scalar(select(func.count()).select_from(KnowledgeItem).where(KnowledgeItem.status == "pending")) or 0
    ticket_total = db.scalar(select(func.count()).select_from(Ticket)) or 0
    ticket_open = db.scalar(select(func.count()).select_from(Ticket).where(Ticket.status == "open")) or 0
    ticket_answered = db.scalar(select(func.count()).select_from(Ticket).where(Ticket.status == "answered")) or 0
    user_total = db.scalar(select(func.count()).select_from(User)) or 0
    return {
        "knowledge_total": knowledge_total,
        "knowledge_published": knowledge_published,
        "knowledge_pending": knowledge_pending,
        "ticket_total": ticket_total,
        "ticket_open": ticket_open,
        "ticket_answered": ticket_answered,
        "user_total": user_total,
    }


@router.get("/top-questions")
def top_questions(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Ticket.question, func.count().label("cnt"))
        .group_by(Ticket.question)
        .order_by(func.count().desc())
        .limit(10)
    ).all()
    return [{"question": q, "count": c} for q, c in rows]


@router.get("/knowledge-usage")
def knowledge_usage(db: Session = Depends(get_db)):
    rows = db.execute(
        select(KnowledgeItem.id, KnowledgeItem.title, KnowledgeItem.view_count)
        .where(KnowledgeItem.status == "published")
        .order_by(KnowledgeItem.view_count.desc())
        .limit(10)
    ).all()
    return [{"id": i, "title": t, "view_count": v} for i, t, v in rows]


@router.get("/ticket-response")
def ticket_response(db: Session = Depends(get_db)):
    answered = db.execute(
        select(Ticket.created_at, Ticket.answered_at).where(Ticket.status == "answered", Ticket.answered_at.isnot(None))
    ).all()
    durations = [(a - c).total_seconds() for c, a in answered if a and c]
    avg_seconds = (sum(durations) / len(durations)) if durations else 0
    return {"answered_count": len(answered), "avg_response_seconds": round(avg_seconds, 1)}
