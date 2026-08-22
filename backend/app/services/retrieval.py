from sqlalchemy import select

from app.config import settings
from app.models.chunk import Chunk
from app.models.knowledge import KnowledgeItem
from app.services.embedding import embed_texts

SIM_THRESHOLD = 0.5


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    return sum(x * y for x, y in zip(a, b))


def search(question: str, db, top_k: int = 5) -> list[tuple[float, Chunk, KnowledgeItem]]:
    q = embed_texts([question])[0]
    stmt = (
        select(Chunk, KnowledgeItem)
        .join(KnowledgeItem, KnowledgeItem.id == Chunk.knowledge_id)
        .where(KnowledgeItem.status == "published")
    )
    if settings.APP_MODE == "public":
        stmt = stmt.where(KnowledgeItem.publish_to_public == True)  # noqa: E712
    rows = db.execute(stmt).all()
    scored = [(_cosine(q, c.embedding), c, item) for c, item in rows]
    scored.sort(key=lambda x: -x[0])
    return scored[:top_k]
