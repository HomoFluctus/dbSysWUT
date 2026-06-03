# 日程管理系统 — 开发进展

## 当前状态

全部 10 个 Phase 已完成。35 项 API 测试 + 前端构建全部通过。

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

### 数据库实际验证（当前状态）

```
Tables in scheduler.db: 12 tables
  activity_log:           rows populated ✓
  categories:             rows populated ✓ (含默认分类)
  recurring_rules:        table exists ✓
  reminders:              table exists ✓
  schedule_dependencies:  table exists ✓
  schedule_tags:          table exists ✓
  schedule_templates:     table exists ✓ (Phase 9.4)
  schedules:              rows populated ✓
  subtasks:               table exists ✓ (Phase 8)
  tags:                   table exists ✓
  users:                  rows populated ✓

New columns added:
  schedules.actual_minutes   INTEGER  (Phase 9.3 时间追踪)
  schedules.share_token      TEXT     (Phase 9.6 日程分享)
  users.ical_token           TEXT     (Phase 9.5 iCal 导出)
```

---

## 文件清单（95+ 个源文件）

### 后端 (60 个 .py 文件)
```
backend/
  requirements.txt
  app/
    __init__.py, main.py, config.py, database.py, dependencies.py
    core/
      __init__.py, security.py, exceptions.py
    models/
      __init__.py, user.py, category.py, schedule.py, schedule_tag.py,
      schedule_dependency.py, schedule_template.py, recurring_rule.py,
      reminder.py, tag.py, activity_log.py, subtask.py
    schemas/
      __init__.py, user.py, schedule.py, category.py, tag.py,
      reminder.py, recurring.py, dependency.py, subtask.py,
      activity_log.py, template.py
    api/
      __init__.py, router.py, auth.py, schedules.py, categories.py,
      tags.py, reminders.py, calendar.py, statistics.py, search.py,
      activity_log.py, ical.py, sharing.py, templates.py
    services/
      __init__.py, auth_service.py, schedule_service.py, category_service.py,
      tag_service.py, reminder_service.py, recurring_service.py,
      calendar_service.py, statistics_service.py, search_service.py,
      activity_log_service.py, dependency_service.py, ical_service.py,
      subtask_service.py, template_service.py
```

### 前端 (35 个 .vue/.js 文件)
```
frontend/
  package.json, vite.config.js, index.html
  src/
    App.vue, main.js
    router/
      index.js
    stores/
      auth.js, schedules.js, categories.js, tags.js, templates.js
    views/
      LoginView.vue, RegisterView.vue, DashboardView.vue, CalendarView.vue,
      ScheduleFormView.vue, ScheduleDetailView.vue, CategoriesView.vue,
      StatisticsView.vue, KanbanView.vue, FocusView.vue, ReviewView.vue,
      ActivityLogView.vue, SharedScheduleView.vue
    components/
      AppLayout.vue, FilterPanel.vue, ScheduleCard.vue, PriorityBadge.vue,
      StatusBadge.vue, TagBadge.vue, StatisticsChart.vue, ActivityHeatmap.vue,
      StreakCard.vue, PomodoroTimer.vue, TemplatePicker.vue
    utils/
      api.js, date.js, constants.js
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

## Phase 9: 功能丰富 — 10 项新功能 ✅ 已完成

**完成时间:** 2026-06-03

### 实现计划

| 阶段 | 功能 | 状态 |
|------|------|------|
| 1 | 快速捕获 + 专注视图 | ✅ 已完成 |
| 2 | 连续打卡 + 每日/每周回顾 | ✅ 已完成 |
| 3 | 活动日志视图 + 时间追踪 | ✅ 已完成 |
| 4 | 日程模板 | ✅ 已完成 |
| 5 | iCal 订阅导出 + 番茄钟 | ✅ 已完成 |
| 6 | 日程分享 | ✅ 已完成 |

### Phase 9.1 详情（快速捕获 + 专注视图）

**快速捕获**
- AppLayout 顶部栏新增输入框，前缀 Plus 图标
- 输入标题 + Enter 即可创建日程（Ctrl+Enter 聚焦）
- 默认 status=todo，其他字段留空
- 创建成功显示 Toast 提示，清空输入框
- 后端复用 `POST /schedules`，无需改动

**专注视图**
- 新路由 `/focus`，`FocusView.vue`
- 三个分区：已逾期（红色）/ 今天（蓝色）/ 即将到来（橙色）
- 自动排除已完成和已取消的日程
- 后端 `list_schedules` 新增 `focus=True` 参数，筛选今日+逾期
- 键盘快捷键：F 键跳转专注模式

### Phase 9.2 详情（连续打卡 + 回顾）

**连续打卡**
- 后端 `statistics_service.get_streaks()` 查询 `completed_at` 去重日期，计算 current_streak 和 longest_streak
- 前端 `StreakCard.vue` 组件，Dashboard 统计区展示当前连续 🔥 和最长连续 🏆 天数
- API: `GET /statistics/streaks`

**每日/每周回顾**
- 后端 `statistics_service.get_review(period)` 返回 completed/overdue/upcoming 三组数据
- 前端 `ReviewView.vue`，路由 `/review`，日/周切换
- 三个卡片区域：已完成 ✅、已逾期 ⚠️、即将到来 📅
- API: `GET /statistics/review?period=day|week`

### Phase 9.3 详情（活动日志 + 时间追踪）

**活动日志**
- 后端 `activity_log_service.list_activity_logs()` 分页查询，JOIN schedules 返回标题
- 前端 `ActivityLogView.vue`，路由 `/activity-log`，el-timeline 展示
- 支持按 action 类型筛选（created/updated/deleted/completed 等）
- API: `GET /activity-log?page=&per_page=&action=`

**时间追踪**
- Schedule 模型新增 `actual_minutes` 列
- 后端 `PATCH /schedules/{id}/log-time` 端点，支持 add（累加）和 set（覆盖）模式
- 前端 ScheduleDetailView 新增时间输入 + 追加耗时 / 设为按钮
- 实际 vs 预估对比进度条（绿/黄/红三色）
- 统计端点 `GET /statistics/time-accuracy` 返回准确率
- 数据库: `ALTER TABLE schedules ADD COLUMN actual_minutes INTEGER`

### Phase 9.4 详情（日程模板）

**后端**
- `ScheduleTemplate` 模型（template_id, user_id, title, description, priority, estimated_minutes, category_id, tag_ids JSON 文本）
- 完整 CRUD API: `GET/POST/DELETE /templates`
- Apply 端点: `POST /templates/{id}/apply` 从模板创建日程

**前端**
- `stores/templates.js` Pinia store
- `TemplatePicker.vue` 对话框组件，浏览模板列表，点击"使用"应用模板
- ScheduleFormView 新增"从模板加载"按钮
- ScheduleDetailView 新增"存为模板"按钮

### Phase 9.5 详情（iCal + 番茄钟）

**iCal 导出**
- User 模型新增 `ical_token` 列
- `ical_service.py` 生成 ICS 格式文本（支持周期日程展开）
- 公开端点 `GET /ical/feed?token=` 无需认证
- 认证端点 `GET /ical/token` 获取/生成用户 token
- 前端 Dashboard 导出菜单新增"iCal 订阅链接"，一键复制

**番茄钟**
- `PomodoroTimer.vue` 组件
- SVG 圆形进度环，预设 15/25/45 分钟
- 工作/休息模式切换
- Web Audio API 提示音 + Notification API 浏览器通知
- 嵌入 ScheduleDetailView

### Phase 9.6 详情（日程分享）

**后端**
- Schedule 模型新增 `share_token` 列
- `POST /schedules/{id}/share` 生成分享链接
- `DELETE /schedules/{id}/share` 撤销分享
- `GET /schedules/share/{token}` 公开端点，无需认证，返回 ScheduleDetailOut

**前端**
- `SharedScheduleView.vue` 只读展示页，路由 `/share/:token`（无需登录）
- ScheduleDetailView 新增分享按钮 + 弹窗（生成链接/复制/撤销）

### Phase 9.7 详情（分类管理完善）

**完成时间:** 2026-06-03

- 分类列表完整 CRUD：创建（名称+颜色）、行内重命名（点击名称编辑，Enter/blur 保存）、颜色修改、删除
- 点击分类名称或日程计数 → 跳转 Dashboard 并自动按该分类筛选
- 删除确认对话框，显示该分类下的日程数量，防止误删
- 后端保护：默认分类不可删除（返回 400）
- Dashboard 支持从 URL query 参数 `?category_id=X` 读取筛选条件
- 防重复提交（saving 锁）、创建/删除 loading 状态

### 路由总览

| 路由 | 视图 | 认证 | 说明 |
|------|------|------|------|
| `/` | DashboardView | 需要 | 日程总览、热力图、连续打卡、统计 |
| `/login` | LoginView | 否 | 登录页 |
| `/register` | RegisterView | 否 | 注册页 |
| `/focus` | FocusView | 需要 | 专注视图（今日+逾期） |
| `/calendar` | CalendarView | 需要 | 月/周/日日历视图 |
| `/kanban` | KanbanView | 需要 | 看板视图 |
| `/review` | ReviewView | 需要 | 每日/每周回顾 |
| `/statistics` | StatisticsView | 需要 | 统计图表 |
| `/categories` | CategoriesView | 需要 | 分类管理 |
| `/activity-log` | ActivityLogView | 需要 | 活动日志时间线 |
| `/schedules/new` | ScheduleFormView | 需要 | 新建日程 |
| `/schedules/:id` | ScheduleDetailView | 需要 | 日程详情 |
| `/schedules/:id/edit` | ScheduleFormView | 需要 | 编辑日程 |
| `/share/:token` | SharedScheduleView | 否 | 公开分享只读视图 |

### 全部新建文件

**后端 (11)**:
- `models/schedule_template.py`, `schemas/template.py`, `services/template_service.py`, `api/templates.py`
- `services/ical_service.py`, `api/ical.py`
- `services/activity_log_service.py`, `schemas/activity_log.py`, `api/activity_log.py`
- `api/sharing.py`

**前端 (8)**:
- `views/FocusView.vue`, `views/ReviewView.vue`, `views/ActivityLogView.vue`, `views/SharedScheduleView.vue`
- `components/StreakCard.vue`, `components/PomodoroTimer.vue`, `components/TemplatePicker.vue`
- `stores/templates.js`

**后端修改 (7)**:
- `models/schedule.py` — 加 `actual_minutes`, `share_token`
- `models/user.py` — 加 `ical_token`
- `services/schedule_service.py` — focus 筛选, log_time, share_token
- `services/statistics_service.py` — get_streaks, get_review, get_time_accuracy
- `api/schedules.py` — focus, log-time, share, batch, subtask, duplicate, export 端点
- `api/statistics.py` — streaks, review, time-accuracy 端点
- `api/router.py` — 注册 templates, ical, activity_log, sharing 路由

**前端修改 (7)**:
- `router/index.js` — 新增 /focus, /review, /activity-log, /share/:token 路由
- `components/AppLayout.vue` — 导航项: 专注, 回顾, 活动日志
- `utils/api.js` — 新增 streaks, review, logTime, templates, ical, share, activityLog API 方法
- `views/DashboardView.vue` — StreakCard 组件, iCal 订阅链接, 统计卡点击筛选, 读取 ?category_id 参数
- `views/ScheduleDetailView.vue` — 时间追踪, 番茄钟, 分享, 存为模板
- `views/ScheduleFormView.vue` — 集成 TemplatePicker 从模板加载
- `views/CategoriesView.vue` — 完整重写: 行内编辑, 颜色管理, 点击筛选, 删除确认对话框

**数据库变更**:
- `ALTER TABLE schedules ADD COLUMN actual_minutes INTEGER`
- `ALTER TABLE schedules ADD COLUMN share_token TEXT`
- `ALTER TABLE users ADD COLUMN ical_token TEXT`

### 端到端测试结果（30 项全部通过 ✅）

```
 1. Category create          ✅ POST /api/categories (name + color)
 2. Category create default  ✅ POST /api/categories (default color #6366f1)
 3. Category update name     ✅ PATCH /api/categories/{id} (partial update)
 4. Category update color    ✅ PATCH /api/categories/{id} (color only)
 5. Category update both     ✅ PATCH /api/categories/{id} (name + color)
 6. Category delete          ✅ DELETE /api/categories/{id} → 204
 7. Default cat protection   ✅ DELETE /api/categories/{default} → 400 (blocked)
 8. Category filter          ✅ GET /api/schedules?category_id=X (filtered)
 9. Tag create               ✅ POST /api/tags
10. Schedule create          ✅ POST /api/schedules (full fields)
11. Quick capture            ✅ POST /api/schedules (title only)
12. Focus view               ✅ GET /api/schedules?focus=true (1 item)
13. Streaks                  ✅ GET /api/statistics/streaks (current_streak, longest_streak)
14. Review (day)             ✅ GET /api/statistics/review?period=day
15. Review (week)            ✅ GET /api/statistics/review?period=week
16. Activity log             ✅ GET /api/activity-log (paginated)
17. Time tracking (add)      ✅ PATCH /schedules/{id}/log-time mode=add (30→30)
18. Time tracking (set)      ✅ PATCH /schedules/{id}/log-time mode=set (30→45)
19. Time accuracy            ✅ GET /api/statistics/time-accuracy
20. Template save            ✅ POST /api/templates
21. Template list            ✅ GET /api/templates
22. Template apply           ✅ POST /api/templates/{id}/apply
23. iCal token               ✅ GET /api/ical/token
24. iCal feed (public)       ✅ GET /api/ical/feed?token= (no auth, ICS format)
25. Share generate           ✅ POST /api/schedules/{id}/share
26. Share public view        ✅ GET /api/schedules/share/{token} (no auth)
27. Share revoke             ✅ DELETE /api/schedules/{id}/share (then 404)
28. Duplicate                ✅ POST /api/schedules/{id}/duplicate
29. Subtask create           ✅ POST /api/schedules/{id}/subtasks
30. Subtask toggle           ✅ PATCH /api/schedules/{id}/subtasks/{id}
31. Batch status             ✅ POST /api/schedules/batch/status
32. Recurring create         ✅ PUT /api/schedules/{id}/recurring
33. Recurring dates          ✅ GET /api/schedules/{id}/recurring/dates
34. Export CSV               ✅ GET /api/schedules/export/csv (200)
35. Export JSON              ✅ GET /api/schedules/export/json (200)
```
