from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.deps import get_current_user
from app.db import get_db
from app.models.knowledge import KINDS, KnowledgeItem
from app.models.user import User
from app.schemas.knowledge import KnowledgeCreate, KnowledgeOut, KnowledgeUpdate

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


def _can_edit(user: User, item: KnowledgeItem) -> bool:
    return user.role in ("engineer", "admin") or item.author_id == user.id


@router.get("", response_model=list[KnowledgeOut])
def list_knowledge(
    kind: str | None = None,
    category: str | None = None,
    status: str | None = None,
    q: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(KnowledgeItem)
    if user.role == "support":
        stmt = stmt.where(KnowledgeItem.status == "published")
        if settings.APP_MODE == "public":
            stmt = stmt.where(KnowledgeItem.publish_to_public == True)  # noqa: E712
    if kind:
        stmt = stmt.where(KnowledgeItem.kind == kind)
    if category:
        stmt = stmt.where(KnowledgeItem.category == category)
    if status:
        stmt = stmt.where(KnowledgeItem.status == status)
    if q:
        stmt = stmt.where(KnowledgeItem.title.contains(q))
    stmt = stmt.order_by(KnowledgeItem.id.desc())
    return db.scalars(stmt).all()


@router.get("/{item_id}", response_model=KnowledgeOut)
def get_knowledge(item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.get(KnowledgeItem, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "知识不存在")
    if user.role == "support" and item.status != "published":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "该知识未发布")
    return item


@router.post("", response_model=KnowledgeOut)
def create_knowledge(body: KnowledgeCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if body.kind not in KINDS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"类型必须是 {KINDS}")
    item = KnowledgeItem(
        title=body.title,
        kind=body.kind,
        body=body.body,
        aliases=body.aliases,
        case_fields=body.case_fields,
        category=body.category,
        tags=body.tags,
        machines=body.machines,
        author_id=user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=KnowledgeOut)
def update_knowledge(item_id: int, body: KnowledgeUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.get(KnowledgeItem, item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "知识不存在")
    if not _can_edit(user, item):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "无权修改")
    data = body.model_dump(exclude_unset=True)
    if "kind" in data and data["kind"] not in KINDS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"类型必须是 {KINDS}")
    for k, v in data.items():
        setattr(item, k, v)
    item.version += 1
    db.commit()
    db.refresh(item)
    return item
