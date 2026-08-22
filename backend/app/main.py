from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, files, knowledge, users

app = FastAPI(title="AIQA - 注塑机上位机智能问答系统")
app.include_router(auth.router)
app.include_router(knowledge.router)
app.include_router(files.router)
if settings.APP_MODE == "full":
    app.include_router(users.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": settings.APP_MODE}
