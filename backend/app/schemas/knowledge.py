from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    kind: str = "article"
    body: str = ""
    aliases: list[str] = []
    case_fields: dict | None = None
    category: str = ""
    tags: list[str] = []
    machines: str = ""


class KnowledgeUpdate(BaseModel):
    title: str | None = None
    kind: str | None = None
    body: str | None = None
    aliases: list[str] | None = None
    case_fields: dict | None = None
    category: str | None = None
    tags: list[str] | None = None
    machines: str | None = None


class KnowledgeOut(BaseModel):
    id: int
    title: str
    kind: str
    body: str
    aliases: list
    case_fields: dict | None
    status: str
    category: str
    tags: list
    machines: str
    version: int
    publish_to_public: bool
    view_count: int
    author_id: int
    reviewer_id: int | None
    review_comment: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
