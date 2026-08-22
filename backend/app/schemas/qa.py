from pydantic import BaseModel, Field


class QaIn(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    allow_free: bool = False


class QaSource(BaseModel):
    id: int
    title: str


class QaOut(BaseModel):
    answer: str
    sources: list[QaSource]
    hit: bool
