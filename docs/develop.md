m# 日程管理系统 — 开发进展

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

---

## Phase 8: 交互增强 ✅ 已完成

**完成时间:** 2026-06-02

### 新增功能
1. **子任务清单** — 日程下拆分检查项，支持勾选/取消/删除
2. **活动热力图** — GitHub 风格年度活动热力图，按 created_at + due_date 双维度统计
3. **全局键盘快捷键** — N 新建、K 看板、/ 搜索、? 帮助面板
4. **明暗主题切换** — 完整 CSS 变量体系 light/dark 双主题，localStorage 持久化
5. **卡通吉祥物** — 侧边栏青蛙形象+轮播鼓励语
6. **Emoji 装饰** — 全页面添加 emoji 图标

### 新增/修改文件
- `backend/app/models/subtask.py` — Subtask 模型
- `backend/app/schemas/subtask.py` — Subtask Pydantic schemas
- `backend/app/services/subtask_service.py` — 子任务业务逻辑
- `backend/app/api/schedules.py` — 新增 4 个子任务端点 + 导出修复
- `backend/app/services/statistics_service.py` — 新增 `get_activity_heatmap()`
- `backend/app/api/statistics.py` — 新增 `/activity-heatmap` 端点
- `frontend/src/components/ActivityHeatmap.vue` — 热力图组件
- `frontend/src/App.vue` — 完整明暗主题 CSS 变量
- `frontend/src/components/AppLayout.vue` — 主题切换+快捷键+吉祥物

### Bug 修复
1. CSV/JSON 导出 401 → 改用 fetch+Blob+Authorization header
2. 看板视图无数据 → per_page 从 200 改为 100（后端限制 le=100）
3. 主题切换不明显 → :root 亮色系，html.dark 暗色系
4. 热力图无色 → 合并 created_at + due_date 统计，修复 level-0 背景色

---

## Phase 9: 功能丰富 — 10 项新功能 🚧 进行中

**计划时间:** 2026-06-02

### 实现计划

| 阶段 | 功能 | 状态 |
|------|------|------|
| 1 | 快速捕获 + 专注视图 | ✅ 已完成 |
| 2 | 连续打卡 + 每日/每周回顾 | ⬜ 待实现 |
| 3 | 活动日志视图 + 时间追踪 | ⬜ 待实现 |
| 4 | 日程模板 | ⬜ 待实现 |
| 5 | iCal 订阅导出 + 番茄钟 | ⬜ 待实现 |
| 6 | 日程分享 | ⬜ 待实现 |

### Phase 9.1 详情（快速捕获 + 专注视图）

**快速捕获**
- AppLayout 顶部栏新增输入框，前缀 Plus 图标
- 输入标题 + Enter 即可创建日程（Ctrl+Enter 聚焦）
- 默认 status=todo，其他字段留空
- 创建成功显示 Toast 提示，清空输入框
- 后端复用 `POST /schedules`，无需改动

**专注视图**
- 新路由 `/focus`，自动筛选今日及逾期日程
- 三个分区：已逾期（红色）/ 今天（蓝色）/ 即将到来（橙色）
- 自动排除已完成和已取消的日程
- 后端 `list_schedules` 新增 `focus=True` 参数
- 键盘快捷键：F 键跳转专注模式

### Phase 9 全部新建文件

**后端 (11)**:
- `models/schedule_template.py`, `schemas/template.py`, `services/template_service.py`, `api/templates.py`
- `services/ical_service.py`, `api/ical.py`
- `services/activity_log_service.py`, `schemas/activity_log.py`, `api/activity_log.py`
- `api/sharing.py`

**前端 (7)**:
- `views/FocusView.vue`, `views/ReviewView.vue`, `views/ActivityLogView.vue`, `views/SharedScheduleView.vue`
- `components/StreakCard.vue`, `components/PomodoroTimer.vue`, `components/TemplatePicker.vue`
- `stores/templates.js`

**后端修改**:
- `models/schedule.py` — 加 `actual_minutes`, `share_token`
- `models/user.py` — 加 `ical_token`
- `services/schedule_service.py` — focus 筛选, log_time, share_token
- `services/statistics_service.py` — get_streaks, get_review, get_time_accuracy
- `api/schedules.py` — focus, log-time, share 端点
- `api/statistics.py` — streaks, review, time-accuracy 端点
- `api/router.py`, `main.py`, `config.py`

**前端修改**:
- `router/index.js`, `components/AppLayout.vue`, `utils/api.js`, `views/DashboardView.vue`, `views/ScheduleDetailView.vue`
