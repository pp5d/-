from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import auth, files, knowledge, qa, stats, sync, tickets, users

app = FastAPI(title="AIQA - 注塑机上位机智能问答系统")
app.include_router(auth.router)
app.include_router(knowledge.router)
app.include_router(files.router)
app.include_router(qa.router)
app.include_router(tickets.router)
app.include_router(sync.router)
app.include_router(stats.router)
if settings.APP_MODE == "full":
    app.include_router(users.router)

_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "服务器内部错误，请稍后重试"})


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": settings.APP_MODE}
