# 日程管理系统 — 开发进展

## 当前状态

Phase 1 已完成，全部端到端测试通过。Phase 2 待开始。

---

## Phase 1: 清理 + 基础设施 ✅ 已完成

**完成时间:** 2026-06-02

### 已完成项

1. **清理旧项目** — 删除旧的 MiniDB 文件（backend/、data/、docs/）
2. **目录结构** — 创建新项目完整目录结构
3. **配置文件**:
   - `backend/app/config.py` — pydantic-settings 配置（使用绝对路径 `/home/suhongzhou/dbSysWUT/data/scheduler.db`）
   - `backend/app/database.py` — SQLAlchemy async engine、session factory、SQLite WAL + foreign keys pragma
4. **数据模型** — 全部 8 个 SQLAlchemy ORM 模型（9 张表）:
   - `user.py` — 用户表
   - `category.py` — 分类表
   - `schedule.py` — 日程表（含组合索引 `ix_schedules_user_due`、`ix_schedules_user_status`）
   - `recurring_rule.py` — 周期规则表
   - `reminder.py` — 提醒表（含组合索引 `ix_reminders_remind_at_sent`）
   - `tag.py` — 标签表
   - `schedule_tag.py` — 日程-标签关联表（M:N）
   - `schedule_dependency.py` — 日程依赖表
   - `activity_log.py` — 活动日志表
5. **Pydantic Schemas** — 请求/响应模型（user、schedule、category、tag、reminder、recurring）
6. **Service 层** — 9 个业务逻辑模块（auth、schedule、category、tag、reminder、recurring、calendar、statistics、search）
7. **API 路由** — 8 组 RESTful 端点（37 个路由，含 auth、schedules、categories、tags、reminders、calendar、statistics、search）
8. **认证核心** — `core/security.py`（JWT + bcrypt）、`core/exceptions.py`
9. **依赖注入** — `dependencies.py`（get_db、get_current_user）
10. **FastAPI 入口** — `main.py`（CORS、router 挂载、startup/shutdown 事件）
11. **依赖安装** — pip 安装成功（使用清华镜像源），所有 9 张表导入验证通过
12. **前端框架** — Vue 3 + Vite + Pinia + Vue Router 完整框架、25 个源码文件、npm 依赖已安装

### Bug 修复记录

1. **数据库路径问题** — 相对路径 `../data/scheduler.db` 在 aiosqlite 中无法打开，改为绝对路径
2. **列表序列化问题** — `list_schedules` 返回的 PaginatedResponse 中 items 是 SQLAlchemy 对象，需要转换为 Pydantic `ScheduleOut`；`ScheduleDetailOut` 会触发 `recurring`/`reminders` 的 lazy load 导致 MissingGreenlet 错误
3. **日历序列化问题** — `calendar` 端点使用 `ScheduleDetailOut` 但未加载 `reminders`，改为 `ScheduleOut`

### 端到端测试结果（全部通过 ✅）

```
1. 用户注册 ✅    POST /api/auth/register   → access_token + refresh_token
2. 用户登录 ✅    POST /api/auth/login      → access_token + refresh_token
3. 获取用户 ✅    GET  /api/auth/me           → {user_id, username, email}
4. 创建分类 ✅    POST /api/categories        → {category_id, name, color}
5. 创建日程 ✅    POST /api/schedules         → 含 title/priority/due_date/category/tags
6. 日程列表 ✅    GET  /api/schedules         → 分页列表，按 due_date + priority 排序
7. 日程详情 ✅    GET  /api/schedules/{id}    → 含 category/tags/recurring/reminders
8. 状态变更 ✅    PATCH /api/schedules/{id}/status → status + completed_at + activity_log
9. 日历月视图 ✅  GET  /api/calendar?year=&month= → 该月所有日程（使用组合索引）
10. 日历周视图 ✅ GET  /api/calendar/week?date=
11. 日历日视图 ✅ GET  /api/calendar/day?date=
12. 统计概览 ✅   GET  /api/statistics/overview → total/todo/in_progress/done/overdue
13. 搜索 ✅       GET  /api/search?q=关键字    → 标题+描述模糊匹配
14. 数据库验证 ✅ 9 张表 + 25 个索引全部创建成功
```

### 数据库实际验证

```
Tables in scheduler.db: 9 tables ✓
  activity_log:         rows populated ✓
  categories:           rows populated ✓ (含默认分类)
  recurring_rules:      table exists ✓
  reminders:            table exists ✓
  schedule_dependencies:table exists ✓
  schedule_tags:        table exists ✓
  schedules:            rows populated ✓
  tags:                 table exists ✓
  users:                rows populated ✓

Indexes: 25 indexes including:
  ix_schedules_user_due (user_id, due_date)  ✓
  ix_schedules_user_status (user_id, status) ✓
  ix_reminders_remind_at_sent (remind_at, sent) ✓
```

---

## 文件清单（73 个文件）

### 后端 (46 个文件)
```
backend/
  requirements.txt
  app/
    __init__.py, main.py, config.py, database.py, dependencies.py
    core/__init__.py, security.py, exceptions.py
    models/__init__.py, user.py, category.py, schedule.py,
           recurring_rule.py, reminder.py, tag.py, schedule_tag.py,
           schedule_dependency.py, activity_log.py
    schemas/__init__.py, user.py, schedule.py, category.py,
            tag.py, reminder.py, recurring.py
    api/__init__.py, router.py, auth.py, schedules.py,
        categories.py, tags.py, reminders.py, calendar.py,
        statistics.py, search.py
    services/__init__.py, auth_service.py, schedule_service.py,
             category_service.py, tag_service.py, reminder_service.py,
             recurring_service.py, calendar_service.py,
             statistics_service.py, search_service.py
```

### 前端 (25 个文件)
```
frontend/
  package.json, vite.config.js, index.html
  src/
    App.vue, main.js
    router/index.js
    stores/auth.js, schedules.js, categories.js, tags.js
    views/LoginView.vue, RegisterView.vue, DashboardView.vue,
         CalendarView.vue, ScheduleFormView.vue, ScheduleDetailView.vue,
         CategoriesView.vue, StatisticsView.vue
    components/AppLayout.vue, FilterPanel.vue, ScheduleCard.vue,
               PriorityBadge.vue, StatusBadge.vue, TagBadge.vue,
               StatisticsChart.vue
    utils/api.js, date.js, constants.js
```

### 文档 (2 个文件)
```
docs/plan.md, develop.md
```
