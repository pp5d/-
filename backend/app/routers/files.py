import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.core.deps import get_current_user
from app.db import get_db
from app.models.knowledge import Attachment, KnowledgeItem
from app.models.user import User

router = APIRouter(prefix="/api/files", tags=["files"])

ALLOWED = {
    "image": {"jpeg", "png", "gif", "webp", "jpg"},
    "video": {"mp4", "avi", "mov"},
    "pdf": {"pdf"},
}


def _kind_of(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    for kind, exts in ALLOWED.items():
        if ext in exts:
            return kind
    return ""


def _max_of(kind: str) -> int:
    return {"image": settings.MAX_IMAGE_MB, "video": settings.MAX_VIDEO_MB, "pdf": settings.MAX_PDF_MB}[kind]


@router.post("")
def upload_file(
    knowledge_id: int = Query(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.get(KnowledgeItem, knowledge_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "知识不存在")
    if not (user.role in ("engineer", "admin") or item.author_id == user.id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "无权上传附件")
    kind = _kind_of(file.filename or "")
    if not kind:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "不支持的文件类型，仅支持图片/视频/PDF")
    limit = _max_of(kind) * 1024 * 1024
    content = b""
    while True:
        part = file.file.read(1024 * 1024)  # 每次读 1MB
        if not part:
            break
        content += part
        if len(content) > limit:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"文件超过 {_max_of(kind)}MB 限制")
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    storage_name = f"{uuid.uuid4().hex}.{file.filename.rsplit('.', 1)[-1].lower()}"
    storage_path = upload_dir / storage_name
    storage_path.write_bytes(content)
    att = Attachment(
        knowledge_id=knowledge_id,
        filename=file.filename or storage_name,
        content_type=kind,
        size=len(content),
        storage_path=str(storage_path),
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    return {"id": att.id, "filename": att.filename, "content_type": att.content_type, "size": att.size}


@router.get("/{att_id}/download")
def download_file(att_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    att = db.get(Attachment, att_id)
    if att is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "附件不存在")
    item = db.get(KnowledgeItem, att.knowledge_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "知识不存在")
    if user.role == "support":
        if item.status != "published":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "无权下载")
        if settings.APP_MODE == "public" and not item.publish_to_public:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "无权下载")
    import os
    if not os.path.exists(att.storage_path):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "文件已丢失")
    return FileResponse(att.storage_path, filename=att.filename)
