from datetime import datetime

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


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
