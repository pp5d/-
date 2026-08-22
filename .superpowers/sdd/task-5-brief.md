### Task 5: 用户管理接口（管理员）

**Files:**
- Create: `backend/app/routers/users.py`
- Modify: `backend/app/main.py`（挂载 users 路由）
- Create: `backend/tests/test_users.py`

**Interfaces:**
- Consumes: Task 4 的 `require_roles`、`hash_password`、`UserCreate/UserOut/UserUpdate`；Task 3 的 `User`。
- Produces: `GET /api/users`（管理员，全部用户列表）、`POST /api/users?role=engineer`（管理员创建，仅 full 模式）、`PATCH /api/users/{user_id}`（管理员，改 role/group_name/is_active）。

- [ ] **Step 1: 写失败测试 tests/test_users.py**

```python
def _login_as(client, username, password):
    return client.post("/api/auth/login", json={"username": username, "password": password}).json()["access_token"]


def _seed_user(client, username, role, password="secret123"):
    from app.db import SessionLocal
    from app.models.user import User
    from app.core.security import hash_password

    db = SessionLocal()
    db.add(User(username=username, role=role, hashed_password=hash_password(password)))
    db.commit()
    db.close()


def _admin_token(client):
    _seed_user(client, "boss", "admin")
    return _login_as(client, "boss", "secret123")


def test_admin_list_users(client):
    _seed_user(client, "eng1", "engineer")
    token = _admin_token(client)
    r = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    usernames = [u["username"] for u in r.json()]
    assert "eng1" in usernames and "boss" in usernames


def test_non_admin_forbidden(client):
    _seed_user(client, "eng1", "engineer")
    token = _login_as(client, "eng1", "secret123")
    r = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_admin_create_user(client):
    token = _admin_token(client)
    r = client.post("/api/users?role=engineer", json={"username": "eng2", "password": "secret123"}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["role"] == "engineer"


def test_admin_disable_user(client):
    _seed_user(client, "eng1", "engineer")
    token = _admin_token(client)
    uid = client.get("/api/users", headers={"Authorization": f"Bearer {token}"}).json()[0]["id"]
    r = client.patch(f"/api/users/{uid}", json={"is_active": False}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["is_active"] is False
    # 被禁用的用户无法登录
    r2 = client.post("/api/auth/login", json={"username": "eng1", "password": "secret123"})
    assert r2.status_code == 403
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd backend && pytest tests/test_users.py -v`
Expected: FAIL（模块不存在）。

- [ ] **Step 3: 实现 routers/users.py**

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.deps import require_roles
from app.core.security import hash_password
from app.db import get_db
from app.models.user import ROLES, User
from app.schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    dependencies=[Depends(require_roles("admin"))],
)


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.id)).all()


@router.post("", response_model=UserOut)
def create_user(body: UserCreate, role: str = Query(default="support"), db: Session = Depends(get_db)):
    if settings.APP_MODE != "full":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "公网实例禁止创建用户")
    if role not in ROLES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"角色必须是 {ROLES}")
    exists = db.scalar(select(User).where(User.username == body.username))
    if exists:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "用户名已存在")
    user = User(
        username=body.username,
        phone=body.phone,
        role=role,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "用户不存在")
    if body.role is not None:
        if body.role not in ROLES:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"角色必须是 {ROLES}")
        user.role = body.role
    if body.group_name is not None:
        user.group_name = body.group_name
    if body.is_active is not None:
        user.is_active = body.is_active
    db.commit()
    db.refresh(user)
    return user
```

- [ ] **Step 4: 挂载路由到 main.py**

在 `app/main.py` 中追加：

```python
from app.routers import auth, users

app.include_router(auth.router)
app.include_router(users.router)
```

- [ ] **Step 5: 运行测试**

Run: `cd backend && pytest tests/ -v`
Expected: 全部通过（auth 8 项 + users 4 项 + health 1 项 + user_model 2 项）。

- [ ] **Step 6: Commit**

```bash
git add backend/app/routers/users.py backend/app/main.py backend/tests/test_users.py
git commit -m "feat: 管理员用户管理接口"
```

---
---


