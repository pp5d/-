# Task 4 报告：认证接口（注册/登录/me）

- **状态**: DONE
- **Commit**: `52577c0aca7a7a1e9d2419ca50322479a198512d`（`feat: JWT 认证与角色权限`，分支 `feature/m1-foundation`）
- **完成时间**: 2026-08-22

## 执行步骤

### Step 1: 写失败测试（TDD Red）
- 创建 `backend/tests/test_auth.py`，按简报逐字写入 7 个测试：`test_register_public_mode`、`test_register_forbidden_in_full_mode`、`test_register_duplicate_username`、`test_login_ok`、`test_login_wrong_password`、`test_me_requires_token`、`test_me_ok`。
- 另按父任务要求（8 个认证测试；"login 时禁用账号返回 403"）补充第 8 个测试 `test_login_disabled_account`（禁用账号登录 → 403）。

### Step 2: 运行测试确认失败
- `<venvPy> -m pytest tests/test_auth.py -v` → **8 failed**。
- 失败原因符合预期：`ModuleNotFoundError: No module named 'app.core'`（security/deps 不存在）与 `assert 404 == 200/401/...`（路由未挂载），其余测试在 import 阶段即失败。

### Step 3: 实现 `app/core/security.py`（按简报逐字）
- 创建 `backend/app/core/__init__.py`（空）。
- `hash_password` / `verify_password`：bcrypt 哈希与校验。
- `create_access_token`：HS256 签发 JWT，payload 含 `sub`（用户 id 字符串）、`role`、`exp`（`ACCESS_TOKEN_EXPIRE_MINUTES`）。
- `decode_token`：JWT 解码。

### Step 4: 实现 `app/core/deps.py`（按简报逐字）
- `get_current_user`：HTTPBearer 取 token → 401（未登录/失效/账号不存在或禁用）。
- `require_roles(*roles)`：角色检查，无权 → 403。

### Step 5: 实现 `app/schemas/user.py`（按简报逐字）
- 创建 `backend/app/schemas/__init__.py`（空）。
- `UserCreate{username, password, phone}`、`UserOut{...}`（from_attributes）、`UserUpdate`、`Token{access_token, token_type, user}`。

### Step 6: 实现 `app/routers/auth.py`（按简报逐字）
- 创建 `backend/app/routers/__init__.py`（空）。
- `POST /api/auth/register`：`APP_MODE == "full"` → 403；用户名重复 → 400；注册成功角色固定 `support`，返回 `Token`。
- `POST /api/auth/login`：凭据错误 → 401；账号禁用 → 403。
- `GET /api/auth/me`：`get_current_user` 依赖，返回当前用户。

### Step 7: 挂载路由
- `backend/app/main.py`：在 `from app.config import settings` 后追加 `from app.routers import auth` 与 `app.include_router(auth.router)`。

### Step 8: 运行测试（TDD Green）
- 首轮：**6 passed, 2 failed**。失败为 `test_login_wrong_password`、`test_login_disabled_account`，均 `assert 422 == 401/403`：简报测试中错误密码 `"wrong"`（5 字符）与我补充测试的密码 `"x"`（1 字符）不满足 `UserCreate.password` 的 `min_length=6`，被 Pydantic 校验拦截（422）。
- 最小修正（保留测试意图）：错误密码改为 `"wrong1"`（6 字符）；禁用账号测试改用 `hash_password("secret123")` 创建用户并以正确密码登录验证 403。
- 终轮：**8 passed**；全量套件 **11 passed**（8 auth + 1 health + 2 user_model，无回归）。

### Step 9: Commit
- `git add backend/app backend/tests/test_auth.py`
- `git commit -m "feat: JWT 认证与角色权限"` → `52577c0aca7a7a1e9d2419ca50322479a198512d`（9 files changed, 214 insertions）。

## 新增/修改文件

- 新增：`backend/app/core/__init__.py`、`backend/app/core/security.py`、`backend/app/core/deps.py`、`backend/app/schemas/__init__.py`、`backend/app/schemas/user.py`、`backend/app/routers/__init__.py`、`backend/app/routers/auth.py`、`backend/tests/test_auth.py`
- 修改：`backend/app/main.py`（挂载 auth 路由）

## 测试实际输出（Step 8 终轮）

```
============================= test session starts =============================
platform win32 -- Python 3.12.8, pytest-8.3.4, pluggy-1.6.0 -- D:\Vibing Code Project\...\backend\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\Vibing Code Project\...\backend
plugins: anyio-4.14.2
collecting ... collected 8 items

tests/test_auth.py::test_register_public_mode PASSED                     [ 12%]
tests/test_auth.py::test_register_forbidden_in_full_mode PASSED          [ 25%]
tests/test_auth.py::test_register_duplicate_username PASSED              [ 37%]
tests/test_auth.py::test_login_ok PASSED                                 [ 50%]
tests/test_auth.py::test_login_wrong_password PASSED                     [ 62%]
tests/test_auth.py::test_login_disabled_account PASSED                   [ 75%]
tests/test_auth.py::test_me_requires_token PASSED                        [ 87%]
tests/test_auth.py::test_me_ok PASSED                                    [100%]

============================== warnings summary ===============================
.venv\Lib\site-packages\pydantic\_internal\_config.py:295: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.10/migration/

======================== 8 passed, 1 warning in 2.04s =========================
```

全量回归：`pytest -v` → **11 passed, 1 warning in 2.06s**。

## Commit

- hash: `52577c0aca7a7a1e9d2419ca50322479a198512d`
- message: `feat: JWT 认证与角色权限`

## 问题 / 疑虑

1. **简报内部不一致（需记录）**：简报 Step 1 的 `test_login_wrong_password` 使用错误密码 `"wrong"`（5 字符），但 Step 5 的 `UserCreate.password` 有 `min_length=6`，该测试实际会得到 422 而非预期的 401——简报自身无法达到其声明的 "8 passed"。已按"最小改动、保留意图"将错误密码改为 `"wrong1"`。若简报本意是 login 使用独立的宽松校验 schema，请评审确认。
2. **测试数量与简报不符**：简报 Step 1 仅列出 7 个测试，但父任务与 Step 8 要求 8 个测试 / "8 passed"。按父任务明示的 "login 时禁用账号返回 403" 行为补充了第 8 个测试 `test_login_disabled_account`。
3. **Pydantic 弃用警告（非本任务引入）**：`config.py`（Task 2）的 class-based `Config` 触发 `PydanticDeprecatedSince20`，建议后续改为 `model_config = SettingsConfigDict(...)`。不影响功能。
4. **LF→CRLF 提示**：git 提交时对新增文件提示 LF 将被替换为 CRLF，属 Windows 行尾归一化，无实际影响。
5. **测试库耦合（沿用前序任务模式）**：测试通过 `conftest.py` 在导入 `app.db` 前设置 `DATABASE_URL=...aiqa_test` 使 `SessionLocal` 指向测试库，`reset_db` autouse fixture 每次重建表。工作正常，但属隐式耦合。
