# Task 5 报告：用户管理接口（管理员）

- **状态**: DONE
- **Commit**: `e0cf1af81e241ea983d60021ba590b68a648abe7`（`feat: 管理员用户管理接口`，分支 `feature/m1-foundation`）
- **完成时间**: 2026-08-22

## 执行步骤

### Step 1: 写失败测试（TDD Red）
- 创建 `backend/tests/test_users.py`，按简报逐字写入 4 个测试及 3 个辅助函数：
  - `_login_as` / `_seed_user` / `_admin_token`（经 `app.db.SessionLocal` 直插用户、admin 登录取 token）。
  - `test_admin_list_users`：admin 可列出全部用户（含 admin 与 engineer）。
  - `test_non_admin_forbidden`：engineer 访问 `/api/users` → 403。
  - `test_admin_create_user`：`POST /api/users?role=engineer` 创建用户 → 200 且 role 正确。
  - `test_admin_disable_user`：PATCH `is_active=False` → 200，且被禁用用户登录 → 403。

### Step 2: 运行测试确认失败
- `<venvPy> -m pytest tests/test_users.py -v` → **4 failed**。
- 失败原因符合预期（接口未实现）：3 个测试 `assert 404 == 200/403`（`/api/users` 路由不存在），1 个 `KeyError: 0`（列表接口 404 返回 `{"detail":"Not Found"}` 无 `[0]`）。测试收集正常、无导入错误。

### Step 3: 实现 `app/routers/users.py`（按简报逐字）
- 创建 `backend/app/routers/users.py`，路由 `prefix="/api/users"`、`tags=["users"]`，整路由挂 `Depends(require_roles("admin"))`：
  - `GET ""` → `list_users`：按 `id` 升序返回全部用户（`list[UserOut]`）。
  - `POST ""` → `create_user`：`APP_MODE != "full"` → 403（公网实例禁止创建）；`role` 不在 `ROLES` → 400；用户名已存在 → 400；bcrypt 哈希后入库，`role` 取 query 参数（默认 `"support"`）。
  - `PATCH "/{user_id}"` → `update_user`：不存在 → 404；`role`（校验 `ROLES`）/`group_name`/`is_active` 按需更新。

### Step 4: 挂载路由
- `backend/app/main.py`：import 改为 `from app.routers import auth, users`，追加 `app.include_router(users.router)`。

### Step 5: 运行测试（TDD Green）
- `<venvPy> -m pytest tests/test_users.py -v` → **4 passed**。
- 全量回归 `pytest tests/ -v` → **15 passed**（auth 8 + users 4 + health 1 + user_model 2，无回归），与简报预期一致。

### Step 6: Commit
- `git add backend/app/routers/users.py backend/app/main.py backend/tests/test_users.py`
- `git commit -m "feat: 管理员用户管理接口"` → `e0cf1af81e241ea983d60021ba590b68a648abe7`（3 files changed, 115 insertions(+), 1 deletion(-)）。

## 新增/修改文件

- 新增：`backend/app/routers/users.py`、`backend/tests/test_users.py`
- 修改：`backend/app/main.py`（挂载 users 路由）

## 测试实际输出（Step 5 终轮）

```
============================= test session starts =============================
platform win32 -- Python 3.12.8, pytest-8.3.4, pluggy-1.6.0 -- D:\Vibing Code Project\...\backend\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\Vibing Code Project\...\backend
plugins: anyio-4.14.2
collecting ... collected 15 items

tests/test_auth.py::test_register_public_mode PASSED                     [  6%]
tests/test_auth.py::test_register_forbidden_in_full_mode PASSED          [ 13%]
tests/test_auth.py::test_register_duplicate_username PASSED              [ 20%]
tests/test_auth.py::test_login_ok PASSED                                 [ 26%]
tests/test_auth.py::test_login_wrong_password PASSED                     [ 33%]
tests/test_auth.py::test_login_disabled_account PASSED                   [ 40%]
tests/test_auth.py::test_me_requires_token PASSED                        [ 46%]
tests/test_auth.py::test_me_ok PASSED                                    [ 53%]
tests/test_health.py::test_health PASSED                                 [ 60%]
tests/test_user_model.py::test_create_user PASSED                        [ 66%]
tests/test_user_model.py::test_username_unique PASSED                    [ 73%]
tests/test_users.py::test_admin_list_users PASSED                        [ 80%]
tests/test_users.py::test_non_admin_forbidden PASSED                     [ 86%]
tests/test_users.py::test_admin_create_user PASSED                       [ 93%]
tests/test_users.py::test_admin_disable_user PASSED                      [100%]

============================== warnings summary ===============================
.venv\Lib\site-packages\pydantic\_internal\_config.py:295: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://docs.pydantic.dev/2.10/migration/

======================== 15 passed, 1 warning in 4.40s ========================
```

users 专项：`pytest tests/test_users.py -v` → **4 passed, 1 warning**。

## Commit

- hash: `e0cf1af81e241ea983d60021ba590b68a648abe7`
- message: `feat: 管理员用户管理接口`

## 问题 / 疑虑

1. **简报 Step 2 预期与实测表述差异（无碍）**：简报预期失败为"模块不存在"（import 错误），实测为 4 个测试全失败、原因均为 `/api/users` 路由未实现（404/KeyError），本质一致：接口未实现。测试文件本身导入成功（依赖均已就绪）。
2. **`test_admin_disable_user` 对 id 的依赖**：取列表 `[0]`（按 id 升序，即先 seed 的 `eng1`）。若将来并行 seed 更多用户仍成立（`reset_db` 每测试重建表），但依赖"admin 是列表第二项之后"的隐式顺序，与简报一致、未改动。
3. **Pydantic 弃用警告（非本任务引入）**：`config.py`（Task 2）class-based `Config` 触发 `PydanticDeprecatedSince20`，建议后续改用 `SettingsConfigDict`，不影响功能。
4. **LF→CRLF 提示**：git 提交时对新增文件提示 LF 将被替换为 CRLF，属 Windows 行尾归一化，无实际影响。
5. **create_user 的 403 分支未被测试覆盖**：`APP_MODE != "full"` 返回 403 的逻辑（简报要求 3 中明示）无对应测试（简报 Step 1 未提供），仅按实现逐字照抄；如需覆盖可在后续任务补测试。
