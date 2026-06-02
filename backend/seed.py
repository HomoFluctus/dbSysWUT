"""数据库种子数据脚本。清空现有数据并插入演示数据。

Usage:
    cd backend && python3 seed.py

注意：会清除全部现有数据。
"""

import asyncio
from datetime import date, datetime, timedelta, timezone

from app.database import async_session_factory, engine
from app.models.activity_log import ActivityLog
from app.models.category import Category
from app.models.recurring_rule import RecurringRule
from app.models.reminder import Reminder
from app.models.schedule import PriorityLevel, Schedule, ScheduleStatus
from app.models.schedule_tag import ScheduleTag
from app.models.tag import Tag
from app.models.user import User
from app.core.security import get_password_hash


async def seed():
    # 导入所有模型确保建表
    import app.models.user  # noqa
    import app.models.category  # noqa
    import app.models.schedule  # noqa
    import app.models.tag  # noqa
    import app.models.schedule_tag  # noqa
    import app.models.recurring_rule  # noqa
    import app.models.reminder  # noqa
    import app.models.schedule_dependency  # noqa
    import app.models.activity_log  # noqa

    async with engine.begin() as conn:
        from app.database import Base
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        # ===== 用户 =====
        alice = User(username="alice", email="alice@example.com", password_hash=get_password_hash("123456"))
        bob = User(username="bob", email="bob@example.com", password_hash=get_password_hash("123456"))
        db.add_all([alice, bob])
        await db.flush()

        # ===== 分类 =====
        cats = [
            Category(user_id=alice.user_id, name="学习", color="#3b82f6"),
            Category(user_id=alice.user_id, name="工作", color="#f97316"),
            Category(user_id=alice.user_id, name="生活", color="#22c55e"),
            Category(user_id=alice.user_id, name="运动", color="#ef4444"),
        ]
        db.add_all(cats)
        await db.flush()

        # ===== 标签 =====
        tags = [
            Tag(user_id=alice.user_id, name="数据库", color="#a855f7"),
            Tag(user_id=alice.user_id, name="SQL", color="#06b6d4"),
            Tag(user_id=alice.user_id, name="考试", color="#f43f5e"),
            Tag(user_id=alice.user_id, name="项目", color="#8b5cf6"),
            Tag(user_id=alice.user_id, name="阅读", color="#10b981"),
        ]
        db.add_all(tags)
        await db.flush()

        now = datetime.now(timezone.utc)

        # ===== 日程 =====
        s1 = Schedule(
            user_id=alice.user_id, category_id=cats[0].category_id,
            title="完成数据库第三章习题", description="索引设计、查询优化相关题目",
            priority=PriorityLevel.HIGH, status=ScheduleStatus.TODO,
            due_date=now + timedelta(days=3),
            estimated_minutes=120,
        )
        s2 = Schedule(
            user_id=alice.user_id, category_id=cats[0].category_id,
            title="复习SQL语法", description="DDL/DML/DCL 语句",
            priority=PriorityLevel.MEDIUM, status=ScheduleStatus.IN_PROGRESS,
            due_date=now + timedelta(days=1),
            estimated_minutes=60,
        )
        s3 = Schedule(
            user_id=alice.user_id, category_id=cats[0].category_id,
            title="数据库期中考试",
            priority=PriorityLevel.URGENT, status=ScheduleStatus.TODO,
            due_date=now + timedelta(days=14),
        )
        s4 = Schedule(
            user_id=alice.user_id, category_id=cats[1].category_id,
            title="项目周会", description="讨论项目进度，准备演示",
            priority=PriorityLevel.MEDIUM, status=ScheduleStatus.TODO,
            due_date=now + timedelta(hours=5),
            estimated_minutes=30,
        )
        s5 = Schedule(
            user_id=alice.user_id, category_id=cats[2].category_id,
            title="买纪念日礼物",
            priority=PriorityLevel.LOW, status=ScheduleStatus.TODO,
            due_date=now + timedelta(days=7),
        )
        s6 = Schedule(
            user_id=alice.user_id, category_id=cats[3].category_id,
            title="跑步锻炼", description="绕湖跑 5km",
            priority=PriorityLevel.LOW, status=ScheduleStatus.TODO,
            due_date=now + timedelta(days=2),
        )
        # 过期任务
        s7 = Schedule(
            user_id=alice.user_id, category_id=cats[0].category_id,
            title="提交 ER 图作业", description="画出图书馆管理系统的 ER 图",
            priority=PriorityLevel.HIGH, status=ScheduleStatus.TODO,
            due_date=now - timedelta(days=2),
        )
        s8 = Schedule(
            user_id=alice.user_id, category_id=cats[0].category_id,
            title="B+树实现练习", description="完成 bptree 的删除再平衡",
            priority=PriorityLevel.MEDIUM, status=ScheduleStatus.DONE,
            due_date=now - timedelta(days=5),
            completed_at=now - timedelta(days=4),
        )
        db.add_all([s1, s2, s3, s4, s5, s6, s7, s8])
        await db.flush()

        # ===== 标签关联 =====
        db.add_all([
            ScheduleTag(schedule_id=s1.schedule_id, tag_id=tags[0].tag_id),
            ScheduleTag(schedule_id=s1.schedule_id, tag_id=tags[1].tag_id),
            ScheduleTag(schedule_id=s2.schedule_id, tag_id=tags[1].tag_id),
            ScheduleTag(schedule_id=s3.schedule_id, tag_id=tags[2].tag_id),
            ScheduleTag(schedule_id=s7.schedule_id, tag_id=tags[0].tag_id),
        ])

        # ===== 周期规则 =====
        db.add_all([
            RecurringRule(
                schedule_id=s4.schedule_id, freq="weekly", interval=1,
                weekdays="[2]", start_date=date.today(),
            ),
            RecurringRule(
                schedule_id=s6.schedule_id, freq="weekly", interval=2,
                weekdays="[1,3,5]", start_date=date.today(),
                end_date=date.today() + timedelta(days=90),
            ),
        ])

        # ===== 提醒 =====
        db.add_all([
            Reminder(schedule_id=s1.schedule_id, remind_at=s1.due_date - timedelta(hours=2)),
            Reminder(schedule_id=s3.schedule_id, remind_at=s3.due_date - timedelta(days=1)),
            Reminder(schedule_id=s7.schedule_id, remind_at=s7.due_date - timedelta(hours=1)),
        ])

        # ===== 活动日志 =====
        db.add_all([
            ActivityLog(schedule_id=s1.schedule_id, user_id=alice.user_id, action="created"),
            ActivityLog(schedule_id=s2.schedule_id, user_id=alice.user_id, action="created"),
            ActivityLog(schedule_id=s2.schedule_id, user_id=alice.user_id, action="status_changed", field_changed="status", old_value="todo", new_value="in_progress"),
        ])

        await db.commit()
        await engine.dispose()

    print("种子数据插入完成！")
    print(f"  用户:   alice(123456), bob(123456)")
    print(f"  分类:   学习, 工作, 生活, 运动")
    print(f"  标签:   数据库, SQL, 考试, 项目, 阅读")
    print(f"  日程:   8 条 (含过期/已完成/周期/紧急)")
    print(f"  周期:   2 条 (每周会议, 隔周跑步)")
    print(f"  提醒:   3 条")
    print(f"  日志:   3 条")


if __name__ == "__main__":
    asyncio.run(seed())
