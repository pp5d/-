import base64
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.deps import require_roles
from app.core.security import hash_password
from app.db import get_db
from app.models.chunk import Chunk
from app.models.knowledge import Attachment, KnowledgeItem
from app.models.user import User

router = APIRouter(prefix="/api/sync", tags=["sync"])


def _build_snapshot(db: Session) -> dict:
    items = db.scalars(
        select(KnowledgeItem).where(
            KnowledgeItem.status == "published",
            KnowledgeItem.publish_to_public == True,  # noqa: E712
        )
    ).all()
    knowledge = []
    for it in items:
        chunks = db.scalars(select(Chunk).where(Chunk.knowledge_id == it.id)).all()
        atts = db.scalars(select(Attachment).where(Attachment.knowledge_id == it.id)).all()
        attachments = []
        for a in atts:
            p = Path(settings.UPLOAD_DIR) / a.storage_path
            content = ""
            if p.exists():
                content = base64.b64encode(p.read_bytes()).decode()
            attachments.append({"filename": a.filename, "content_type": a.content_type, "content_b64": content})
        knowledge.append(
            {
                "title": it.title,
                "kind": it.kind,
                "body": it.body,
                "aliases": it.aliases,
                "case_fields": it.case_fields,
                "category": it.category,
                "tags": it.tags,
                "machines": it.machines,
                "chunks": [{"content": c.content, "embedding": c.embedding} for c in chunks],
                "attachments": attachments,
            }
        )
    return {"knowledge": knowledge}


@router.post("/import")
def import_snapshot(body: dict, x_sync_token: str = Header(default=""), db: Session = Depends(get_db)):
    if not settings.PUBLIC_API_TOKEN or x_sync_token != settings.PUBLIC_API_TOKEN:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "同步令牌无效")
    if settings.APP_MODE != "public":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "仅公网实例接收同步")
    if not isinstance(body, dict) or not isinstance(body.get("knowledge"), list):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "快照格式错误")
    if len(body.get("knowledge", [])) > 5000:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "快照过大")
    sys_user = db.scalar(select(User).where(User.username == "sync_bot"))
    if sys_user is None:
        sys_user = User(username="sync_bot", role="support", is_active=False, hashed_password=hash_password("sync-bot-internal"))
        db.add(sys_user)
        db.flush()
    author_id = sys_user.id
    # 先清理旧附件文件，再清空公网 publish 知识（chunks/attachments 靠外键 CASCADE 级联删除）
    old_items = db.scalars(select(KnowledgeItem).where(KnowledgeItem.publish_to_public == True)).all()  # noqa: E712
    for it in old_items:
        for att in db.scalars(select(Attachment).where(Attachment.knowledge_id == it.id)).all():
            p = Path(settings.UPLOAD_DIR) / att.storage_path
            try:
                if p.exists():
                    p.unlink()
            except OSError:
                pass
    db.execute(delete(KnowledgeItem).where(KnowledgeItem.publish_to_public == True))  # noqa: E712
    import uuid

    for k in body.get("knowledge", []):
        item = KnowledgeItem(
            title=k["title"],
            kind=k["kind"],
            body=k["body"],
            aliases=k.get("aliases") or [],
            case_fields=k.get("case_fields"),
            category=k.get("category") or "",
            tags=k.get("tags") or [],
            machines=k.get("machines") or "",
            status="published",
            publish_to_public=True,
            author_id=author_id,
        )
        db.add(item)
        db.flush()
        for c in k.get("chunks", []):
            db.add(Chunk(knowledge_id=item.id, chunk_index=0, content=c["content"], embedding=c["embedding"]))
        for a in k.get("attachments", []):
            if a.get("content_b64"):
                upload_dir = Path(settings.UPLOAD_DIR)
                upload_dir.mkdir(parents=True, exist_ok=True)
                name = f"{uuid.uuid4().hex}_{a['filename']}"
                (upload_dir / name).write_bytes(base64.b64decode(a["content_b64"]))
                db.add(Attachment(knowledge_id=item.id, filename=a["filename"], content_type=a["content_type"], size=0, storage_path=name))
    db.commit()
    return {"ok": True, "count": len(body.get("knowledge", []))}


@router.post("/push")
def push_snapshot(user: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    if not settings.PUBLIC_SYNC_URL:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "未配置公网同步地址 PUBLIC_SYNC_URL")
    snapshot = _build_snapshot(db)
    try:
        r = httpx.post(
            settings.PUBLIC_SYNC_URL,
            json=snapshot,
            headers={"X-Sync-Token": settings.PUBLIC_API_TOKEN},
            timeout=120,
        )
        r.raise_for_status()
        return {"ok": True, "count": len(snapshot["knowledge"]), "detail": r.json()}
    except Exception as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"同步失败：{e}")
