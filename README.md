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
