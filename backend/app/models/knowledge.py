from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

KINDS = ("qa", "article", "case", "code")
STATUSES = ("draft", "pending", "published", "archived")


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    kind: Mapped[str] = mapped_column(String(16), default="article")
    body: Mapped[str] = mapped_column(Text, default="")
    aliases: Mapped[list] = mapped_column(JSON, default=list)
    case_fields: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="draft", index=True)
    category: Mapped[str] = mapped_column(String(64), default="")
    tags: Mapped[list] = mapped_column(JSON, default=list)
    machines: Mapped[str] = mapped_column(String(200), default="")
    version: Mapped[int] = mapped_column(Integer, default=1)
    publish_to_public: Mapped[bool] = mapped_column(Boolean, default=False)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    review_comment: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    knowledge_id: Mapped[int] = mapped_column(ForeignKey("knowledge_items.id", ondelete="CASCADE"))
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(16))  # image | video | pdf
    size: Mapped[int] = mapped_column(Integer)
    storage_path: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
