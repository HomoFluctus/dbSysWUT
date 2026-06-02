# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

日程管理系统，基于数据库系统原理课程（ER 建模、3NF、索引、事务、查询优化）。
前后端分离：FastAPI 后端 + Vue 3 SPA 前端 + SQLite 数据库。

## 启动命令

```bash
# 后端 (http://localhost:8000)
cd backend && ~/.local/bin/uvicorn app.main:app --reload --port 8000
# API 文档: http://localhost:8000/docs

# 前端 (http://localhost:3000，自动代理 /api 到后端)
cd frontend && npm run dev
```

Python 包安装：`~/.local/bin/pip install -r backend/requirements.txt --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple`

## 架构

三层架构，每层有明确的职责边界：

```
frontend/src/
  views/          ← 页面，组合组件，调用 stores
  components/     ← 可复用 UI 组件
  stores/         ← Pinia 状态管理，调用 api.js
  utils/api.js    ← 所有后端请求的封装
  router/index.js ← 路由 + 认证守卫 (检查 localStorage token)

backend/app/
  api/            ← FastAPI 路由，只做参数解析和 HTTP 响应，调 services
  services/       ← 业务逻辑，SQLAlchemy 查询，不碰 HTTP
  models/         ← SQLAlchemy ORM (Base 定义在 database.py)
  schemas/        ← Pydantic 请求/响应模型
  core/           ← JWT + bcrypt, 自定义异常
  dependencies.py ← FastAPI Depends: get_db (事务管理), get_current_user (JWT 验证)
  database.py     ← async engine, session factory, Base, SQLite pragma
```

**事务管理**: `get_db()` 依赖在请求成功时自动 commit，异常时自动 rollback。不要在 services 中手动 commit。

## 数据库设计

9 张表 (SQLAlchemy `async` 模式，SQLite WAL + foreign_keys=ON):

| 表 | 核心关系 | 说明 |
|---|---------|------|
| users | | 用户，注册/登录/JWT |
| schedules | user_id FK, category_id FK | 日程，核心表 |
| categories | user_id FK | 分类，注册时自动创建默认分类 |
| tags / schedule_tags | M:N | 标签，schedule_tags 是纯关联表 |
| recurring_rules | schedule_id FK UNIQUE | 1:1 周期规则 |
| reminders | schedule_id FK | 1:N 提醒 |
| schedule_dependencies | schedule_id FK, depends_on_id FK | 日程依赖 |
| activity_log | user_id FK, schedule_id FK | 操作审计日志 |

**核心索引**: `ix_schedules_user_due` (user_id, due_date) 组合索引，支撑日历视图和逾期查询。

## 关键模式与已知陷阱

### 序列化

- `ScheduleOut` 对应列表/日历等不需要详情场景（只有 `category_id` 数字，不含关系对象）
- `ScheduleDetailOut` 包含 `category`, `tags`, `recurring`, `reminders` 全套——**仅用于详情接口**
- **陷阱**: 如果 query 没有 `selectinload` 对应关系，用 `ScheduleDetailOut` 序列化会触发 `MissingGreenlet` 错误
- list_schedules 返回的 `PaginatedResponse.items` 是 SQLAlchemy 对象，需要手动 `ScheduleOut.model_validate()` 转换

### 认证

- JWT 双 token：access (30min) + refresh (7d)
- 前端 `router.beforeEach` 检查 localStorage 中有无 token 来决定跳转
- 所有受保护端点注入 `Depends(get_current_user)`
- 注册时在同一事务中创建 user + 默认分类 (name="默认")

### 路径

- `backend/app/config.py` 中数据库 URL 使用绝对路径 `/home/suhongzhou/dbSysWUT/data/scheduler.db`
- 切换环境时需要修改此路径
- 前端通过 Vite proxy 将 `/api` 转发到 `http://127.0.0.1:8000`

## 开发阶段

全部 Phase 已完成 ✅（Phase 1-7），详见 `docs/develop.md`。
