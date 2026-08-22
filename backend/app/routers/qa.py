from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.qa import QaIn, QaOut, QaSource
from app.services.llm import generate
from app.services.retrieval import SIM_THRESHOLD, search

router = APIRouter(prefix="/api/qa", tags=["qa"])


@router.post("", response_model=QaOut)
def ask(body: QaIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    results = search(body.question, db)
    if not results or results[0][0] < SIM_THRESHOLD:
        return QaOut(answer="知识库中暂未找到相关答案，请尝试换一种问法，或联系工程师处理。", sources=[], hit=False)
    contexts = [c.content for _, c, _ in results]
    answer = generate(body.question, contexts)
    seen = set()
    sources = []
    for _, _, item in results:
        if item.id not in seen:
            seen.add(item.id)
            sources.append(QaSource(id=item.id, title=item.title))
    return QaOut(answer=answer, sources=sources, hit=True)
