# Task 3 报告：用户模型与 Alembic 迁移

- **状态**: DONE
- **Commit**: `732755b9f558beb5d884cd5d60b9dca94dc8c2be`（`feat: 用户模型与 alembic 迁移`，分支 `feature/m1-foundation`）
- **完成时间**: 2026-08-22

## 执行步骤

### Step 1: 创建模型文件（严格按简报代码）
- 创建 `backend/app/models/user.py`：`User` 模型，表名 `users`，字段 `id:int PK`、`username:String(64) unique+index`、`phone:String(20) default ""`、`hashed_password:String(128)`、`role:String(16) default "support"`、`group_name:String(64) default ""`、`is_active:Boolean default True`、`created_at:DateTime(timezone=True) server_default now()`；常量 `ROLES = ("engineer", "support", "admin")`。
- 创建 `backend/app/models/__init__.py`：导出 `User`、`ROLES`。

### Step 2: 初始化 Alembic
- 在 `backend` 目录运行 `<venvPy> -m alembic init alembic`，生成 `backend/alembic.ini`、`backend/alembic/env.py`、`backend/alembic/script.py.mako`、`backend/alembic/README`、`backend/alembic/versions/`。

### Step 3: 修改 `alembic/env.py`
- 在 `from alembic import context` 之前加入：
  ```python
  from app.config import settings
  import app.models  # noqa: F401 确保模型注册到 Base.metadata
  from app.db import Base
  ```
- 模块顶层加入 `config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)`。
- 删除原 `target_metadata = None`，改为 `target_metadata = Base.metadata`。

### Step 4: 生成并应用迁移
- 生成：`alembic revision --autogenerate -m "create users table"` → 成功，一次通过（import 生效，检测到 `users` 表 + `ix_users_username` 索引）。
- 应用：`alembic upgrade head` → `Running upgrade -> 1292ef54ea51, create users table`。
- psql 验证 `\d users`：8 列全部符合预期，`users_pkey` 主键、`ix_users_username` UNIQUE btree 索引存在，`created_at` 默认 `now()`。

### Step 5: 创建测试（严格按简报代码）
- 创建 `backend/tests/test_user_model.py`：`test_create_user`、`test_username_unique`。

### Step 6: 运行测试
- `<venvPy> -m pytest tests/test_user_model.py -v` → **2 passed**（实际输出见下）。
- 附加验证：全量 `pytest -q` → **3 passed**（含 Task 1 的 test_health，无回归）。

### Step 7: Commit
- `git add backend/app/models backend/alembic backend/alembic.ini backend/tests/test_user_model.py`
- `git commit -m "feat: 用户模型与 alembic 迁移"` → `732755b9f558beb5d884cd5d60b9dca94dc8c2be`（8 files changed, 315 insertions）。

## 迁移生成的文件路径

- `backend/alembic/versions/1292ef54ea51_create_users_table.py`
  - upgrade：`create_table('users', ...)` + `create_index('ix_users_username', 'users', ['username'], unique=True)`
  - downgrade：`drop_index` + `drop_table`

## 测试实际输出

```
============================= test session starts =============================
platform win32 -- Python 3.12.8, pytest-8.3.4, pluggy-1.6.0 -- D:\Vibing Code Project\...\backend\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\Vibing Code Project\...\backend
plugins: anyio-4.14.2
collecting ... collected 2 items

tests/test_user_model.py::test_create_user PASSED                        [ 50%]
tests/test_user_model.py::test_username_unique PASSED                    [100%]

============================== warnings summary ===============================
.venv\Lib\site-packages\pydantic\_internal\_config.py:295: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/

======================== 2 passed, 1 warning in 0.16s =========================
```

## Commit

- hash: `732755b9f558beb5d884cd5d60b9dca94dc8c2be`
- message: `feat: 用户模型与 alembic 迁移`

## 问题 / 疑虑

1. **Pydantic 弃用警告（非本任务引入）**：`config.py`（Task 2）使用 class-based `Config`，触发 `PydanticDeprecatedSince20` 警告，建议后续改为 `model_config = SettingsConfigDict(...)`。不影响功能。
2. **测试对测试库的依赖是隐式的**：`test_user_model.py` 使用 `app.db.SessionLocal`，其绑定的库由 `conftest.py` 在导入 `app.db` 之前设置 `DATABASE_URL=...aiqa_test` 环境变量决定。当前工作正常（pytest 先加载 conftest），但属于隐式耦合，后续若 conftest 顺序变化需注意。
3. **LF→CRLF 提示**：git 提交时对新增文件报 LF 将被替换为 CRLF 的警告，属 Windows 行尾归一化，无实际影响。
4. 简报 Step 4 的 psql 路径 `D:\PostgreSQL\16\bin\psql.exe` 验证可用，`users` 表结构与模型完全一致。
