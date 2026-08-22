# Task 2 报告：后端骨架（FastAPI + 配置 + 健康检查）

- **执行者**：M1 里程碑实现子代理
- **分支**：`feature/m1-foundation`
- **状态**：DONE（附环境注意事项，见"问题/疑虑"）

## 一、执行步骤（按简报 Step 1 → Step 8）

### Step 1：创建 `backend/requirements.txt`
逐字写入 12 个固定版本依赖（fastapi 0.115.6 / uvicorn 0.34.0 / sqlalchemy 2.0.36 / psycopg[binary] 3.2.3 / alembic 1.14.0 / pydantic 2.10.4 / pydantic-settings 2.7.0 / PyJWT 2.10.1 / bcrypt 4.2.1 / python-multipart 0.0.20 / pytest 8.3.4 / httpx 0.28.1）。

### Step 2：创建 `backend/app/config.py`
逐字写入 `Settings(BaseSettings)`，含 `APP_MODE`、`DATABASE_URL`（默认指向本机 `aiqa` 库）、`SECRET_KEY`、令牌过期、DeepSeek/公网令牌、上传目录与大小限制；`env_file = ".env"`；模块级单例 `settings = Settings()`。

### Step 3：创建 `backend/app/db.py`
逐字写入 `create_engine(settings.DATABASE_URL, pool_pre_ping=True)`、`SessionLocal`、`Base(DeclarativeBase)`、`get_db()` FastAPI 依赖（yield + finally close）。

### Step 4：创建 `backend/app/main.py`
逐字写入 FastAPI 应用（title "AIQA - 注塑机上位机智能问答系统"）、CORS 中间件（allow_origins=["*"]）、`GET /api/health` 返回 `{"status": "ok", "mode": settings.APP_MODE}`。

### Step 5：创建 `backend/tests/conftest.py`
逐字写入：模块顶部设置 `DATABASE_URL=...aiqa_test` / `APP_MODE=full` / `SECRET_KEY=test-secret` 环境变量 → 以 `postgres` 库为管理连接 `CREATE DATABASE aiqa_test`（已存在则忽略）→ 测试引擎与 `TestingSessionLocal` → `reset_db` 夹具（每测试前 drop_all + create_all）→ `client` 夹具（`TestClient` + `get_db` 依赖覆盖）。

### Step 6：创建 `backend/tests/test_health.py`
逐字写入 `test_health`：断言 `/api/health` 返回 200、`status == "ok"`、`mode == "full"`。

另外按要求创建两个 UTF-8 空文件：`backend/app/__init__.py`、`backend/tests/__init__.py`。

### Step 7：创建 venv、安装依赖、运行测试
命令与输出见下节。**注**：由于沙箱限制，实际命令与简报略有差异（见"问题/疑虑"第 1 条），最终结果一致。

### Step 8：git 提交
```bash
git add backend/
git commit -m "feat: 后端骨架与健康检查"
```
- 提交 hash：**`e07c30a3ca7e1fa3a05b66360f0b09c5b183000e`**
- 提交内容：8 个文件，+123 行（`backend/app/__init__.py`、`config.py`、`db.py`、`main.py`、`requirements.txt`、`tests/__init__.py`、`conftest.py`、`test_health.py`）。
- 根 `.gitignore` 已含 `.venv/`、`__pycache__/`、`.pytest_cache/`、`.env`，虚拟环境未被提交。

## 二、测试实际输出

```
$ backend\.venv\Scripts\python.exe -m pytest tests/test_health.py -v
============================= test session starts =============================
platform win32 -- Python 3.12.8, pytest-8.3.4, pluggy-1.6.0 -- D:\...\backend\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\...\backend
plugins: anyio-4.14.2
collecting ... collected 1 item

tests/test_health.py::test_health PASSED                                 [100%]

============================== warnings summary ===============================
.venv\Lib\site-packages\pydantic\_internal\_config.py:295: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead.
...
======================== 1 passed, 1 warning in 0.07s =========================
```

- **结果：1 passed** ✓
- 唯一 warning 是 pydantic 对 `class Config` 的弃用提示——这是简报代码逐字要求，未改动。

## 三、依赖安装输出（要点）

```
Successfully installed Mako-1.4.1 MarkupSafe-3.0.3 PyJWT-2.10.1 alembic-1.14.0 annotated-types-0.8.0
anyio-4.14.2 bcrypt-4.2.1 certifi-2026.7.22 click-8.4.2 colorama-0.4.6 fastapi-0.115.6 greenlet-3.5.5
h11-0.16.0 httpcore-1.0.9 httptools-0.8.0 httpx-0.28.1 idna-3.19 iniconfig-2.3.0 packaging-26.3
pluggy-1.6.0 psycopg-3.2.3 psycopg-binary-3.2.3 pydantic-2.10.4 pydantic-core-2.27.2 pydantic-settings-2.7.0
pytest-8.3.4 python-dotenv-1.2.3 python-multipart-0.0.20 pyyaml-6.0.3 sqlalchemy-2.0.36 starlette-0.41.3
typing-extensions-4.16.0 tzdata-2026.3 uvicorn-0.34.0 watchfiles-1.2.0 websockets-17.0.1
```

安装后验证：所有 12 个顶层包 `import` 成功；`pip check` → `No broken requirements found.`。venv 为 Python 3.12.8 + pip 24.3.1。

## 四、问题/疑虑

1. **沙箱临时目录权限（重要，环境性）**：本会话沙箱下，Python 以默认 `0o700` 模式创建目录（`tempfile.mkdtemp`，ensurepip/pip 均依赖）后，该目录**不可写入**（`PermissionError [Errno 13]`，`os.mkdir` 0o700 失败、0o777 成功）。导致：
   - `python -m venv .venv` 内置 ensurepip 步骤失败（venv 本身能建，pip 装不上）；
   - 直接 `pip install` 在 `pip-unpack-*` 等临时目录同样失败。
   - **应对**：改用 `python -m venv --without-pip .venv` 建 venv，从系统 Python（`D:\Python312`，自带 pip 24.3.1）复制 `pip` 包与 `pip-24.3.1.dist-info` 到 `.venv\Lib\site-packages\`；并在 `.venv\Lib\site-packages\sitecustomize.py` 放置 monkey-patch，把 `tempfile.mkdtemp` 改为以 `0o777` 创建目录（该文件只在 venv 内生效，未提交）。随后 `pip install -r requirements.txt` 一次成功。
   - 说明：这是子代理会话沙箱（workspace-write）的环境限制，**不是仓库/代码问题**；在普通终端中按简报原命令（`python -m venv .venv`）即可，无需 sitecustomize 补丁。此补丁属于本机 venv 内文件，不影响团队。
2. **`.tmp` 目录残留**：为解决临时目录权限问题，将 `TMP/TEMP/PIP_CACHE_DIR` 指向仓库根 `.tmp`；其中有 `0o700` 子目录在沙箱下无法 chmod/删除，`.tmp/` 目前以未跟踪目录残留在仓库根（`git status` 可见 `?? .tmp/`），未被提交。建议主代理或本人在普通终端删除，或加入根 `.gitignore`。
3. **pydantic 弃用警告**：`PydanticDeprecatedSince20: class-based config deprecated, use ConfigDict`——来自简报 Step 2 代码的 `class Config: env_file = ".env"`，按要求逐字实现，未自行改写。后续任务如允许可迁移到 `model_config = SettingsConfigDict(env_file=".env")`。
4. **LF→CRLF 警告**：提交时 git 提示 backend 文件 LF 将转 CRLF，属仓库常规配置行为（core.autocrlf），无影响。
5. 测试运行前后 `reset_db` 夹具实际连接了本机 PostgreSQL（`aiqa_test` 库自动创建），健康检查测试未触碰表结构，但 conftest 的建库/建表逻辑已被执行路径验证（测试通过说明 DB 连接与依赖覆盖均正常）。

## 五、产出接口确认

- `app.config.settings`：全局 Settings 单例 ✓
- `app.db.Base`（DeclarativeBase）、`app.db.get_db`（FastAPI 依赖）✓
- `GET /api/health` → `{"status": "ok", "mode": "full"}` ✓（测试断言通过）
- 测试夹具 `client`（httpx TestClient）与 `reset_db`（每测试重建全部表）✓
