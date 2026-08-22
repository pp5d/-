from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.qa import QaIn, QaOut, QaSource
from app.services.llm import generate, generate_free
from app.services.retrieval import SIM_THRESHOLD, search

router = APIRouter(prefix="/api/qa", tags=["qa"])


@router.post("", response_model=QaOut)
def ask(body: QaIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    results = search(body.question, db)
    if results and results[0][0] >= SIM_THRESHOLD:
        contexts = [c.content for _, c, _ in results]
        answer = generate(body.question, contexts)
        seen = set()
        sources = []
        for _, _, item in results:
            if item.id not in seen:
                seen.add(item.id)
                sources.append(QaSource(id=item.id, title=item.title))
        return QaOut(answer=answer, sources=sources, hit=True)
    if body.allow_free:
        return QaOut(answer=generate_free(body.question), sources=[], hit=False)
    return QaOut(answer="知识库中暂未找到相关答案。", sources=[], hit=False)
