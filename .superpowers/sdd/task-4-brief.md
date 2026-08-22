### Task 4: 认证接口（注册/登录/me）

**Files:**
- Create: `backend/app/core/__init__.py`（空文件）
- Create: `backend/app/core/security.py`
- Create: `backend/app/core/deps.py`
- Create: `backend/app/schemas/__init__.py`（空文件）
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/routers/__init__.py`（空文件）
- Create: `backend/app/routers/auth.py`
- Modify: `backend/app/main.py`（挂载 auth 路由）
- Create: `backend/tests/test_auth.py`

**Interfaces:**
- Consumes: Task 2 的 `settings`、`get_db`；Task 3 的 `User`。
- Produces:
  - `app.core.security.hash_password(plain: str) -> str` / `verify_password(plain: str, hashed: str) -> bool` / `create_access_token(user_id: int, role: str) -> str` / `decode_token(token: str) -> dict`
  - `app.core.deps.get_current_user`（FastAPI 依赖，返回 `User`，401 未登录/失效/禁用）/ `require_roles(*roles)`（返回依赖，403 无权）
  - `app.schemas.user.UserCreate{username, password, phone}`、`UserOut{id, username, phone, role, group_name, is_active, created_at}`、`Token{access_token, token_type, user}`
  - 接口：`POST /api/auth/register`（仅 `APP_MODE=public` 可用，403 否则；角色固定 `support`）、`POST /api/auth/login`、`GET /api/auth/me`

- [ ] **Step 1: 写失败测试 tests/test_auth.py**

```python
import pytest

from app.config import settings
from app.db import SessionLocal
from app.models.user import User


def _make_user(username="eng1", role="engineer", password="secret123"):
    from app.core.security import hash_password

    db = SessionLocal()
    db.add(User(username=username, role=role, hashed_password=hash_password(password)))
    db.commit()
    db.close()


def test_register_public_mode(client, monkeypatch):
    monkeypatch.setattr(settings, "APP_MODE", "public")
    r = client.post("/api/auth/register", json={"username": "sale1", "password": "secret123", "phone": "13800000000"})
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["role"] == "support"
    assert data["access_token"]


def test_register_forbidden_in_full_mode(client):
    r = client.post("/api/auth/register", json={"username": "sale2", "password": "secret123"})
    assert r.status_code == 403


def test_register_duplicate_username(client, monkeypatch):
    monkeypatch.setattr(settings, "APP_MODE", "public")
    client.post("/api/auth/register", json={"username": "sale3", "password": "secret123"})
    r = client.post("/api/auth/register", json={"username": "sale3", "password": "secret123"})
    assert r.status_code == 400


def test_login_ok(client):
    _make_user(password="secret123")
    r = client.post("/api/auth/login", json={"username": "eng1", "password": "secret123"})
    assert r.status_code == 200
    assert r.json()["user"]["role"] == "engineer"


def test_login_wrong_password(client):
    _make_user(password="secret123")
    r = client.post("/api/auth/login", json={"username": "eng1", "password": "wrong"})
    assert r.status_code == 401


def test_me_requires_token(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_me_ok(client):
    _make_user(password="secret123")
    token = client.post("/api/auth/login", json={"username": "eng1", "password": "secret123"}).json()["access_token"]
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["username"] == "eng1"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd backend && pytest tests/test_auth.py -v`
Expected: FAIL（模块不存在 / ImportError）。

- [ ] **Step 3: 实现 core/security.py**

```python
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: int, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
```

- [ ] **Step 4: 实现 core/deps.py**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db import get_db
from app.models.user import User

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "未登录")
    try:
        payload = decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "登录已失效")
    user = db.get(User, int(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "账号不可用")
    return user


def require_roles(*roles: str):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "无权访问")
        return user

    return checker
```

- [ ] **Step 5: 实现 schemas/user.py**

```python
from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    phone: str = ""


class UserOut(BaseModel):
    id: int
    username: str
    phone: str
    role: str
    group_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    role: str | None = None
    group_name: str | None = None
    is_active: bool | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
```

- [ ] **Step 6: 实现 routers/auth.py**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db import get_db
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=Token)
def register(body: UserCreate, db: Session = Depends(get_db)):
    if settings.APP_MODE == "full":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "内网账号由管理员创建")
    exists = db.scalar(select(User).where(User.username == body.username))
    if exists:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "用户名已存在")
    user = User(
        username=body.username,
        phone=body.phone,
        role="support",
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return Token(access_token=create_access_token(user.id, user.role), user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(body: UserCreate, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == body.username))
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "账号已被禁用")
    return Token(access_token=create_access_token(user.id, user.role), user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
```

- [ ] **Step 7: 挂载路由到 main.py**

在 `app/main.py` 中 `from app.config import settings` 之后追加：

```python
from app.routers import auth

app.include_router(auth.router)
```

- [ ] **Step 8: 运行测试**

Run: `cd backend && pytest tests/test_auth.py -v`
Expected: 8 passed。

- [ ] **Step 9: Commit**

```bash
git add backend/app backend/tests/test_auth.py
git commit -m "feat: JWT 认证与角色权限"
```

---
---


