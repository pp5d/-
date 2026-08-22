### Task 3: 用户模型与 Alembic 迁移

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/user.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`、`backend/alembic/script.py.mako`、`backend/alembic/versions/`（`alembic init alembic` 生成后修改）
- Create: `backend/tests/test_user_model.py`

**Interfaces:**
- Consumes: Task 2 的 `Base`、`get_db`、测试夹具。
- Produces: `app.models.user.User`（表 `users`），字段：`id:int PK`、`username:str(64) unique`、`phone:str(20)`、`hashed_password:str(128)`、`role:str(16) default "support"`、`group_name:str(64) default ""`、`is_active:bool default True`、`created_at:datetime server_default now()`。角色常量 `app.models.user.ROLES = ("engineer", "support", "admin")`。

- [ ] **Step 1: 创建模型文件 app/models/user.py**

```python
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

ROLES = ("engineer", "support", "admin")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), default="")
    hashed_password: Mapped[str] = mapped_column(String(128))
    role: Mapped[str] = mapped_column(String(16), default="support")
    group_name: Mapped[str] = mapped_column(String(64), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

在 `app/models/__init__.py` 中：

```python
from app.models.user import ROLES, User

__all__ = ["User", "ROLES"]
```

- [ ] **Step 2: 初始化 Alembic**

Run: `cd backend && alembic init alembic`

- [ ] **Step 3: 修改 alembic/env.py 接入应用配置**

在 `alembic/env.py` 中，把 `from app.config import settings` 与 `import app.models  # noqa` 加到文件顶部（在 `from alembic import context` 之前），并把 `config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)` 放在 `run_migrations_offline` 与 `run_migrations_online` 之前的模块顶层：

```python
from app.config import settings
import app.models  # noqa: F401 确保模型注册到 Base.metadata
from app.db import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata
```

同时删除 `env.py` 中原本的 `target_metadata = None` 行。

- [ ] **Step 4: 生成并应用迁移**

Run: `cd backend && alembic revision --autogenerate -m "create users table"`
Run: `alembic upgrade head`
Run: `$env:PGPASSWORD = "aiqa_dev_password"; & "D:\PostgreSQL\16\bin\psql.exe" -U aiqa -h localhost -d aiqa -c "\d users"`
Expected: 显示 `users` 表结构，包含 `username`、`hashed_password`、`role`、`is_active` 等列。

- [ ] **Step 5: 创建 tests/test_user_model.py**

```python
from app.models.user import User
from app.db import SessionLocal


def test_create_user():
    db = SessionLocal()
    u = User(username="eng1", role="engineer", hashed_password="x")
    db.add(u)
    db.commit()
    db.refresh(u)
    assert u.id is not None
    assert u.is_active is True
    assert u.role == "engineer"
    db.close()


def test_username_unique():
    db = SessionLocal()
    db.add(User(username="dup", role="support", hashed_password="x"))
    db.commit()
    db.add(User(username="dup", role="support", hashed_password="x"))
    try:
        db.commit()
        assert False, "应抛出唯一约束异常"
    except Exception:
        db.rollback()
    db.close()
```

- [ ] **Step 6: 运行测试**

Run: `cd backend && pytest tests/test_user_model.py -v`
Expected: 2 passed。

- [ ] **Step 7: Commit**

```bash
git add backend/app/models backend/alembic backend/alembic.ini backend/tests/test_user_model.py
git commit -m "feat: 用户模型与 alembic 迁移"
```

---
---


