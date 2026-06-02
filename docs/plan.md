# 日程管理系统 — 项目计划

## 项目概述

基于数据库系统原理课程的日程管理系统，应用 ER 建模、3NF 范式化、索引设计、事务管理、查询优化等核心知识点。采用前后端分离架构，支持完整的日程管理功能。

## 技术栈

| 层 | 技术 | 理由 |
|---|------|------|
| 数据库 | SQLite + SQLAlchemy 2.0 (async) | 轻量、零配置，SQLAlchemy 提供完整 ORM + 迁移 |
| 后端 | FastAPI + Uvicorn | 异步支持、自动 OpenAPI 文档 |
| 前端 | Vue 3 (Composition API) + Vite + Pinia | 轻量 SPA 框架，组合式 API |
| 图表 | Chart.js | 统计分析可视化 |
| 迁移 | Alembic | 数据库 schema 版本管理 |

## 系统架构

```
用户浏览器 (Vue 3 SPA)
    ↓ HTTP/REST
FastAPI 后端
    ↓ SQLAlchemy ORM
SQLite 数据库 (WAL 模式)
```

## 数据库设计（ER 模型，3NF）

8 张表，全部满足 3NF：

```
users (user_id PK, username, email, password_hash, created_at, updated_at)
categories (category_id PK, user_id FK, name, color, is_default)
schedules (schedule_id PK, user_id FK, category_id FK, title, description,
           priority, status, due_date, completed_at, estimated_minutes,
           created_at, updated_at)
recurring_rules (rule_id PK, schedule_id FK UNIQUE, freq, interval,
                 weekdays, monthday, start_date, end_date, count)
reminders (reminder_id PK, schedule_id FK, remind_at, method, sent, sent_at)
tags (tag_id PK, user_id FK, name, color)
schedule_tags (schedule_id PK+FK, tag_id PK+FK)  -- M:N 关联表
schedule_dependencies (dependency_id PK, schedule_id FK, depends_on_id FK,
                       dep_type, UNIQUE(schedule_id, depends_on_id))
activity_log (log_id PK, schedule_id FK, user_id FK, action, field_changed,
              old_value, new_value, created_at)
```

### 数据库原理对应

- **1NF**：所有列原子化，无重复组
- **2NF**：唯一组合主键是 schedule_tags，无非键列，自动满足 2NF
- **3NF**：无传递依赖，如 reminders 直接引用 schedule_id 而非间接引用 user_id

### 关系说明

| 关系类型 | 表 | 说明 |
|---------|-----|------|
| 1:N | users → schedules | 一个用户有多个日程 |
| 1:N | users → categories | 一个用户有多个分类 |
| 1:N | categories → schedules | 一个分类下有多个日程 |
| 1:1 | schedules → recurring_rules | 一个日程最多一个周期规则 |
| 1:N | schedules → reminders | 一个日程可有多个提醒 |
| M:N | schedules ↔ tags | 通过 schedule_tags 关联表 |
| 1:N | schedules → schedule_dependencies | 日程依赖关系 |

## 索引策略

| 索引 | 类型 | 用途 |
|------|------|------|
| ix_schedules_user_due (user_id, due_date) | **组合索引** | 日历视图、逾期查询，最核心的索引 |
| ix_schedules_user_status (user_id, status) | 组合索引 | Dashboard "我的待办"查询 |
| ix_schedules_priority | B-tree | 优先级过滤排序 |
| ix_reminders_remind_at_sent (remind_at, sent) | 组合索引 | 后台提醒发送任务 |

## 项目目录结构

```
dbSysWUT/
  backend/
    app/
      main.py              # FastAPI 入口，CORS，lifespan
      config.py             # pydantic-settings 配置
      database.py           # SQLAlchemy engine + session
      dependencies.py       # Depends(get_db), get_current_user
      models/               # SQLAlchemy ORM 模型（8 个文件）
      schemas/              # Pydantic 请求/响应模型
      api/                  # RESTful 路由
        auth.py             # 注册/登录/刷新 token
        schedules.py        # 日程 CRUD + 状态变更
        categories.py       # 分类 CRUD
        tags.py             # 标签 CRUD
        reminders.py        # 提醒 CRUD
        calendar.py         # 日历视图（月/周/日）
        statistics.py       # 统计分析
        search.py           # 全文搜索+过滤
      services/             # 业务逻辑层
      core/
        security.py         # JWT + bcrypt
        exceptions.py       # 自定义异常
    requirements.txt
  frontend/
    src/
      App.vue
      router/index.js
      stores/               # Pinia 状态管理
      views/                # 页面组件
      components/           # 可复用组件
      utils/api.js          # API 请求封装
    index.html, vite.config.js, package.json
  docs/
    plan.md                 # 本文件
```

## API 端点设计

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/register | 注册 |
| POST | /api/auth/login | 登录，返回 JWT |
| POST | /api/auth/refresh | 刷新 token |
| GET | /api/auth/me | 当前用户信息 |

### 日程
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/schedules | 列表（?status=&priority=&category_id=&tag_ids=&page=&per_page=） |
| POST | /api/schedules | 创建 |
| GET | /api/schedules/{id} | 详情 |
| PATCH | /api/schedules/{id} | 更新 |
| DELETE | /api/schedules/{id} | 删除 |
| PATCH | /api/schedules/{id}/status | 快速改状态 |

### 分类 / 标签
| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | /api/categories | 分类列表/创建 |
| PATCH/DELETE | /api/categories/{id} | 分类更新/删除 |
| GET/POST | /api/tags | 标签列表/创建 |
| DELETE | /api/tags/{id} | 标签删除 |

### 日历 / 统计 / 搜索
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/calendar?year=&month= | 月视图 |
| GET | /api/calendar/week?date= | 周视图 |
| GET | /api/calendar/day?date= | 日视图 |
| GET | /api/statistics/overview | 状态概览 |
| GET | /api/statistics/completion?days=30 | 完成率趋势 |
| GET | /api/statistics/category-distribution | 分类分布 |
| GET | /api/statistics/overdue | 逾期分析 |
| GET | /api/search?q=&status=&priority= | 全文搜索 |

## 事务边界

| 操作 | 事务范围 |
|------|---------|
| 用户注册 | 创建 user + 默认分类 |
| 创建日程+标签 | insert schedule + insert schedule_tags |
| 状态变更 | update schedule + insert activity_log |
| 创建日程+周期 | insert schedule + insert recurring_rule |
| 删除日程 | cascade 删除 reminders, dependencies, tags |

通过 SQLAlchemy async session 的 commit/rollback 管理。

## 前端路由

```
/login              → LoginView
/register           → RegisterView
/                   → AppLayout（侧边栏 + 搜索 + 认证守卫）
  /                 → DashboardView（日程列表 + 统计卡片）
  /calendar         → CalendarView（月视图日历）
  /schedules/new    → ScheduleFormView
  /schedules/:id    → ScheduleDetailView
  /schedules/:id/edit → ScheduleFormView
  /categories       → CategoriesView
  /statistics       → StatisticsView（Chart.js 图表）
```

## 实施状态

| Phase | 内容 | 状态 |
|-------|------|------|
| Phase 1 | 清理 + 后端基础设施（模型/配置/数据库） | 已完成 |
| Phase 2 | 认证系统（JWT + bcrypt + 登录注册页面） | 已完成 |
| Phase 3 | 日程 CRUD + 分类标签（前后端） | 已完成 |
| Phase 4 | 日历视图（月/周/日） | 已完成 |
| Phase 5 | 提醒 + 周期 + 活动日志 | 已完成 |
| Phase 6 | 统计分析 + 搜索 | 已完成 |
| Phase 7 | 收尾 + README + 种子数据 | 待完成 |

## 验证方式

1. 启动后端：`cd backend && uvicorn app.main:app --reload`
2. 启动前端：`cd frontend && npm run dev`
3. 手动测试流程：注册 → 登录 → 创建分类 → 创建日程（含标签、提醒、周期）→ 日历视图查看 → 统计页面
4. 访问 `http://localhost:8000/docs` 查看 Swagger API 文档
5. 用 SQLite 客户端直接查看数据库表结构、索引、外键约束
