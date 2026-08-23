# 注塑机上位机智能问答系统（AIQA）

面向注塑机上位机领域的知识库共建 + 智能问答 + 工单闭环系统。

## 功能清单

- **知识库**：五类内容（问答对/文章/故障案例/代码表格）+ 问法别名 + 附件 + 审核流 + 下架/删除
- **智能问答**：RAG（本地 bge-small-zh-v1.5 向量检索 + DeepSeek 生成），未命中转工单或自由回答（带风险标注）
- **工单闭环**：未命中自动建单 → 工程师答复 → 一键沉淀为知识
- **双区部署**：内网全功能 + 公网只读问答，发布同步
- **管理后台**：用户管理、统计报表（高频问题/知识利用率/工单响应）、同步按钮
- **运维**：Docker 一键部署、备份脚本

## 快速开始（开发环境：本机 PostgreSQL 16）

0. 前置：本机 PostgreSQL 16 已安装（`D:\PostgreSQL\16`，服务 `postgresql-16`），角色 `aiqa`/库 `aiqa` 已创建
1. `cd backend && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt`
2. 复制 `backend/.env.example` 为 `backend/.env` 并修改 SECRET_KEY
3. `cd backend && alembic upgrade head && uvicorn app.main:app --reload --port 8000`
4. `cd frontend && npm install && npm run dev`，浏览器打开 http://localhost:5173

## 部署

见 `deploy/内网部署.md`（内网独立部署）与 `deploy/公网部署.md`（公网后加）。分阶段：先内网内部测试，稳定后再开公网。

## 验收

见 `deploy/验收走查.md`。

## 文档

- 设计文档：`docs/superpowers/specs/2026-08-22-注塑机上位机智能问答系统-design.md`
- 里程碑总结：`docs/superpowers/progress/`（M1-M6 各一份）
- 实施计划：`docs/superpowers/plans/`（M1-M7 各一份）
