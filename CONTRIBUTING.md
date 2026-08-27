# 参与开发指南（CONTRIBUTING）

欢迎加入**注塑机上位机智能问答系统（AIQA）**的开发！本文档帮你快速上手：环境配置、项目结构、开发流程、常见任务。

## 快速了解项目

- **是什么**：面向注塑机上位机领域的知识库共建 + 智能问答 + 工单闭环系统
- **技术栈**：FastAPI（Python 3.12）+ Vue3 + PostgreSQL 16 + bge-small 向量检索 + DeepSeek
- **必读文档**（按顺序）：
  1. `README.md` —— 项目总览 + 快速开始
  2. `docs/superpowers/specs/2026-08-22-注塑机上位机智能问答系统-design.md` —— 设计文档（权威）
  3. `docs/superpowers/progress/` —— 各里程碑总结（M1-M7，了解进度与决策）
  4. `docs/superpowers/plans/` —— 实施计划（任务清单，是开发任务的来源）

## 环境配置（Windows）

### 1. 前置依赖
- Python 3.12（安装到 `D:\Python312`）
- PostgreSQL 16（安装到 `D:\PostgreSQL\16`，服务名 `postgresql-16`）
- Node.js ≥ 18

### 2. 数据库初始化（一次性）
```powershell
# 创建角色和库（替换密码）
"D:\PostgreSQL\16\bin\psql.exe" -U postgres -c "CREATE ROLE aiqa LOGIN PASSWORD 'aiqa_dev_password' CREATEDB;"
"D:\PostgreSQL\16\bin\psql.exe" -U postgres -c "CREATE DATABASE aiqa OWNER aiqa;"
```

### 3. 后端
```powershell
cd backend
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
# 编辑 .env，把 SECRET_KEY 改成强随机字符串（必改，否则后端拒绝启动）
# 有 DeepSeek API Key 就填 DEEPSEEK_API_KEY
.venv\Scripts\python.exe -m alembic upgrade head
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

### 4. 前端
```powershell
cd frontend
npm install
npm run dev
# 浏览器打开 http://localhost:5173
```

### 5. 跑测试
```powershell
cd backend
.venv\Scripts\python.exe -m pytest tests/ -q   # 全量测试（56 项）
```

### 6. 种子数据（可选，演示用）
```powershell
cd backend
.venv\Scripts\python.exe seed.py   # 灌入 13 条注塑机示例知识
```

## 项目结构

```
backend/
  app/
    config.py       # 配置（pydantic-settings）
    db.py           # 数据库会话
    models/         # ORM 模型（user/knowledge/chunk/ticket）
    schemas/        # Pydantic 请求/响应模型
    routers/        # API 路由（auth/users/knowledge/files/qa/tickets/sync/stats）
    services/       # 业务逻辑（embedding/indexing/retrieval/llm/rate_limit）
    core/           # 安全（JWT/bcrypt/依赖）
  tests/            # pytest 测试
  seed.py           # 种子数据脚本
  alembic/          # 数据库迁移
frontend/
  src/
    api/            # axios 封装
    stores/         # Pinia（auth/app）
    layouts/        # 主布局
    views/          # 页面（chat/knowledge/ticket/admin）
deploy/             # 部署文档 + 备份脚本 + 验收清单
docs/               # 设计文档、实施计划、里程碑总结
```

## 开发流程

### 分支策略
- **master**：稳定版，随时可运行（合并后必须测试通过）
- 每个功能/修复建分支：`feature/xxx` 或 `fix/xxx`
- 开发完成 → 跑测试 → 提 PR → 审查 → 合并

### 提交信息规范
- `feat: 新功能描述`
- `fix: bug 修复描述`
- `docs: 文档改动`
- `refactor: 重构`
- `test: 测试改动`
- `chore: 杂项（依赖、配置）`

### 代码规范
- 后端：FastAPI + SQLAlchemy 2.0（用 `select()` 而非 `db.query()`）；用户可见错误用中文
- 前端：Vue3 组合式 API；所有 API 调用走 `src/api/http.js`（自动带 token）
- 新增功能必须配套测试

### 如何认领任务
实施计划（`docs/superpowers/plans/`）里的每个任务都是独立可交付的（含完整代码 + 测试 + 验收标准）。认领任务后：
1. 建分支：`git checkout -b feature/任务名`
2. 按计划里的任务步骤实现
3. 跑测试确认通过
4. 提 PR 给维护者 review

## 常见问题

- **后端启动报 SECRET_KEY 错误**：`.env` 里 SECRET_KEY 还是默认值，改成强随机字符串
- **数据库连不上**：检查 PostgreSQL 服务是否运行（`Start-Service postgresql-16`）
- **向量模型下载慢**：模型缓存在 `backend/data/hf_cache`（通过 hf-mirror 下载），首次加载慢属正常
- **前端提问没命中**：确认知识已"发布"（审核通过）且已向量化
