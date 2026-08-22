from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class TicketCreate(BaseModel):
    question: str = Field(min_length=1, max_length=1000)

    @field_validator("question")
    @classmethod
    def strip_question(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("问题不能为空")
        return v


class TicketAnswer(BaseModel):
    answer: str = Field(min_length=1)


class TicketOut(BaseModel):
    id: int
    question: str
    status: str
    asker_id: int
    assignee_id: int | None
    answer: str
    knowledge_id: int | None
    created_at: datetime
    updated_at: datetime
    answered_at: datetime | None

    model_config = {"from_attributes": True}
