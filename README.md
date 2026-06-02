# 日程管理系统

基于数据库系统原理课程的综合实践项目，应用 ER 建模、3NF 范式化、索引设计、事务管理、查询优化等核心知识点。

## 技术栈

| 层 | 技术 |
|---|------|
| 数据库 | SQLite (WAL 模式) + SQLAlchemy 2.0 (async ORM) |
| 后端 | FastAPI + Uvicorn (ASGI) |
| 前端 | Vue 3 + Vite + Pinia + Vue Router |
| 图表 | Chart.js |
| 迁移 | Alembic |

## 快速开始

```bash
# 安装依赖
./start.sh install

# 插入种子数据
./start.sh seed

# 启动全部服务
./start.sh
```

或者分别启动：

```bash
# 终端 1: 后端 (http://localhost:8001)
cd backend && uvicorn app.main:app --reload --port 8001

# 终端 2: 前端 (http://localhost:3000)
cd frontend && npm run dev
```

API 文档: http://localhost:8001/docs

种子用户: `alice` / `123456` (含完整演示数据)

## 数据库设计

### ER 模型

```
users ──1:N── categories ──1:N── schedules ──1:N── reminders
  │                                  │
  │                                  ├── 1:1 ── recurring_rules
  │                                  ├── 1:N ── schedule_dependencies
  │                                  ├── M:N ── tags (via schedule_tags)
  │                                  └── 1:N ── activity_log
  │
  └── 1:N ── tags
```

### 数据库原理映射

| 原理 | 实现位置 | 说明 |
|------|---------|------|
| **ER 建模** | `backend/app/models/` | 8 个实体/关系，1:1、1:N、M:N 关系完整建模 |
| **1NF** | 全部表 | 所有列原子化、无重复组、无多值列 |
| **2NF** | 全部表 | 唯一组合主键 `schedule_tags` 无非键列，自动满足 2NF |
| **3NF** | 全部表 | 无传递依赖；`reminders` 直接引用 `schedule_id`，不间接引用 `user_id` |
| **参照完整性** | `models/schedule.py:21-28` | 全部 FK 带 ON DELETE CASCADE/SET NULL，数据库级约束 |
| **索引设计** | `models/schedule.py:18-21` | 组合索引 `ix_schedules_user_due` 覆盖日历/逾期查询 |
| **事务管理** | `database.py:32-39` | `get_db()` 依赖注入，自动 commit/rollback |
| **审计日志** | `models/activity_log.py` | 记录所有创建/修改/状态变更操作 |
| **Schema 迁移** | `alembic/` | 版本化数据库变更，可追踪可回滚 |

### 关键索引

| 索引名 | 列 | 用途 |
|--------|---|------|
| `ix_schedules_user_due` | (user_id, due_date) | 日历视图、逾期查询 |
| `ix_schedules_user_status` | (user_id, status) | 待办列表查询 |
| `ix_reminders_remind_at_sent` | (remind_at, sent) | 后台提醒调度 |

## API 概览 (37 个端点)

```
认证:
  POST /api/auth/register, /login, /refresh
  GET  /api/auth/me

日程 CRUD:
  GET|POST       /api/schedules          (分页 + 过滤)
  GET|PATCH|DELETE /api/schedules/{id}
  PATCH          /api/schedules/{id}/status

日历:
  GET /api/calendar?year=&month=
  GET /api/calendar/week?date=
  GET /api/calendar/day?date=

统计:
  GET /api/statistics/overview
  GET /api/statistics/completion?days=30
  GET /api/statistics/category-distribution
  GET /api/statistics/priority-distribution
  GET /api/statistics/overdue

搜索:
  GET /api/search?q=&status=&priority=&category_id=

分类/标签/提醒:
  GET|POST /api/categories    PATCH|DELETE /api/categories/{id}
  GET|POST /api/tags          DELETE /api/tags/{id}
  POST     /api/schedules/{id}/reminders
  PATCH|DELETE /api/reminders/{id}
```

## 项目结构

```
dbSysWUT/
  backend/              # FastAPI 后端
    app/
      api/              # REST 路由 (8 组)
      services/         # 业务逻辑 (9 个模块)
      models/           # SQLAlchemy ORM (9 张表)
      schemas/          # Pydantic 请求/响应
      core/             # JWT, bcrypt, 异常
      database.py       # Engine, Session, 事务
      dependencies.py   # 认证 + DB 依赖注入
    alembic/            # 数据库迁移
    seed.py             # 种子数据脚本
  frontend/             # Vue 3 SPA
    src/
      views/            # 8 个页面
      components/       # 7 个可复用组件
      stores/           # 4 个 Pinia stores
      router/           # 路由 + 认证守卫
      utils/            # API 封装 + 日期工具
  start.sh              # 一键启动脚本
  docs/
    plan.md             # 完整项目计划
    develop.md          # 开发进展记录
```
