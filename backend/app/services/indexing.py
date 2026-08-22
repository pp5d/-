from sqlalchemy import delete

from app.models.chunk import Chunk
from app.models.knowledge import KnowledgeItem
from app.services.embedding import embed_texts


def chunk_text(text: str, max_len: int = 500) -> list[str]:
    paragraphs = [p.strip() for p in (text or "").split("\n") if p.strip()]
    chunks: list[str] = []
    for p in paragraphs:
        while len(p) > max_len:
            chunks.append(p[:max_len])
            p = p[max_len:]
        chunks.append(p)
    if not chunks:
        chunks = [(text or "")[:max_len]]
    return chunks


def reindex_knowledge(item: KnowledgeItem, db) -> None:
    db.execute(delete(Chunk).where(Chunk.knowledge_id == item.id))
    texts = [t for t in (chunk_text(item.body) + list(item.aliases or [])) if t.strip()]
    if not texts:
        return
    try:
        vectors = embed_texts(texts)
    except Exception:
        return
    for i, (t, v) in enumerate(zip(texts, vectors)):
        db.add(Chunk(knowledge_id=item.id, chunk_index=i, content=t, embedding=v))
