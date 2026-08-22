### Task 2: 后端骨架（FastAPI + 配置 + 健康检查）

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`（空文件）
- Create: `backend/app/config.py`
- Create: `backend/app/db.py`
- Create: `backend/app/main.py`
- Create: `backend/tests/__init__.py`（空文件）
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_health.py`

**Interfaces:**
- Consumes: Task 1 的 `DATABASE_URL`。
- Produces: `app.config.settings`（全局 Settings 单例）；`app.db.Base`（SQLAlchemy DeclarativeBase）、`app.db.get_db`（FastAPI 依赖）；`GET /api/health` 返回 `{"status": "ok", "mode": ...}`；测试夹具 `client`（httpx TestClient）与 `reset_db`（每个测试前重建全部表）。

- [ ] **Step 1: 创建 requirements.txt**

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy==2.0.36
psycopg[binary]==3.2.3
alembic==1.14.0
pydantic==2.10.4
pydantic-settings==2.7.0
PyJWT==2.10.1
bcrypt==4.2.1
python-multipart==0.0.20
pytest==8.3.4
httpx==0.28.1
```

- [ ] **Step 2: 创建 app/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_MODE: str = "full"  # full=内网全功能 | public=公网只读问答
    DATABASE_URL: str = "postgresql+psycopg://aiqa:aiqa_dev_password@localhost:5432/aiqa"
    SECRET_KEY: str = "please-change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    DEEPSEEK_API_KEY: str = ""
    PUBLIC_API_TOKEN: str = ""
    UPLOAD_DIR: str = "./data/uploads"
    MAX_IMAGE_MB: int = 10
    MAX_VIDEO_MB: int = 100
    MAX_PDF_MB: int = 50

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 3: 创建 app/db.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 4: 创建 app/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(title="AIQA - 注塑机上位机智能问答系统")

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
```

- [ ] **Step 5: 创建测试基础设施 tests/conftest.py**

```python
import os

os.environ["DATABASE_URL"] = "postgresql+psycopg://aiqa:aiqa_dev_password@localhost:5432/aiqa_test"
os.environ["APP_MODE"] = "full"
os.environ["SECRET_KEY"] = "test-secret"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db import Base, get_db
from app.main import app

ADMIN_ENGINE = create_engine(
    "postgresql+psycopg://aiqa:aiqa_dev_password@localhost:5432/postgres",
    isolation_level="AUTOCOMMIT",
)
with ADMIN_ENGINE.connect() as conn:
    try:
        conn.execute(text("CREATE DATABASE aiqa_test"))
    except Exception:
        pass  # 已存在

engine = create_engine(os.environ["DATABASE_URL"])
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

- [ ] **Step 6: 创建 tests/test_health.py**

```python
def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["mode"] == "full"
```

- [ ] **Step 7: 安装依赖并运行测试**

Run: `cd backend && D:\Python312\python.exe -m venv .venv`
Run: `cd backend && .venv\Scripts\python.exe -m pip install -r requirements.txt`
Run: `cd backend && .venv\Scripts\python.exe -m pytest tests/test_health.py -v`
Expected: 1 passed。

- [ ] **Step 8: Commit**

```bash
git add backend/
git commit -m "feat: 后端骨架与健康检查"
```

---
---


