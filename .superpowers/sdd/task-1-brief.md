### Task 1: 仓库结构与环境验证（本机 PostgreSQL 已就绪）

**Files:**
- Create: `.gitignore`
- Create: `backend/.env.example`
- Create: `README.md`

**Interfaces:**
- Consumes: 本机 PostgreSQL 16（服务 `postgresql-16` 已运行，`localhost:5432`；角色 `aiqa`/密码 `aiqa_dev_password`/库 `aiqa` 均已创建）。
- Produces: `.gitignore`、`backend/.env.example`（含 DATABASE_URL）、`README.md`；开发库连接串 `postgresql+psycopg://aiqa:aiqa_dev_password@localhost:5432/aiqa`。

- [ ] **Step 1: 创建 .gitignore**

```
node_modules/
dist/
__pycache__/
*.pyc
.venv/
.env
data/
.pytest_cache/
*.log
.DS_Store
```

- [ ] **Step 2: 创建 backend/.env.example**

```
APP_MODE=full
DATABASE_URL=postgresql+psycopg://aiqa:aiqa_dev_password@localhost:5432/aiqa
SECRET_KEY=please-change-me
ACCESS_TOKEN_EXPIRE_MINUTES=10080
DEEPSEEK_API_KEY=
PUBLIC_API_TOKEN=change-me
UPLOAD_DIR=./data/uploads
MAX_IMAGE_MB=10
MAX_VIDEO_MB=100
MAX_PDF_MB=50
```

- [ ] **Step 3: 创建 README.md**

```markdown
# 注塑机上位机智能问答系统（AIQA）

面向注塑机上位机领域的知识库共建 + 智能问答系统。

- 设计文档：`docs/superpowers/specs/2026-08-22-注塑机上位机智能问答系统-design.md`
- 实施计划：`docs/superpowers/plans/`

## 快速开始（开发环境：本机 PostgreSQL 16）

0. 前置：本机 PostgreSQL 16 已安装（`D:\PostgreSQL\16`，服务 `postgresql-16`），角色 `aiqa`/库 `aiqa` 已创建
1. `cd backend && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt`
2. 复制 `backend/.env.example` 为 `backend/.env` 并修改 SECRET_KEY
3. `cd backend && alembic upgrade head && uvicorn app.main:app --reload --port 8000`
4. `cd frontend && npm install && npm run dev`，浏览器打开 http://localhost:5173
```

- [ ] **Step 4: 验证本机数据库连接**

Run: `$env:PGPASSWORD = "aiqa_dev_password"; & "D:\PostgreSQL\16\bin\psql.exe" -U aiqa -h localhost -d aiqa -c "SELECT 1;"`
Expected: 输出 `1` 行（`?column?` 值为 1），说明连接串可用。

- [ ] **Step 5: Commit**

```bash
git add .gitignore backend/.env.example README.md
git commit -m "chore: 仓库结构与本机数据库连接配置"
```

---
---


