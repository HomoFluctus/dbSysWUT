<template>
  <div class="detail-page" v-loading="loading">
    <template v-if="schedule">
      <div class="detail-hero">
        <div>
          <div class="badge-row">
            <StatusBadge :status="schedule.status" />
            <PriorityBadge :priority="schedule.priority" />
          </div>
          <h2 class="detail-title">{{ schedule.title }}</h2>
        </div>
        <div class="hero-actions">
          <el-button-group>
            <el-button
              v-for="opt in statusOptions"
              :key="opt.value"
              :type="schedule.status === opt.value ? 'primary' : 'default'"
              size="small"
              @click="changeStatus(opt.value)"
            >{{ opt.label }}</el-button>
          </el-button-group>
          <router-link :to="`/schedules/${schedule.schedule_id}/edit`">
            <el-button type="primary" plain size="small">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
          </router-link>
          <el-popconfirm title="确定删除这个日程？" confirm-button-text="删除" @confirm="handleDelete">
            <template #reference>
              <el-button type="danger" plain size="small">
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </template>
          </el-popconfirm>
        </div>
      </div>

      <el-descriptions :column="2" border class="detail-meta">
        <el-descriptions-item label="到期时间">
          {{ schedule.due_date ? new Date(schedule.due_date).toLocaleString('zh-CN') : '未设置' }}
        </el-descriptions-item>
        <el-descriptions-item label="预计耗时">
          {{ schedule.estimated_minutes ? schedule.estimated_minutes + ' 分钟' : '未设置' }}
        </el-descriptions-item>
        <el-descriptions-item label="分类">
          <el-tag :color="schedule.category?.color" effect="dark" size="small" v-if="schedule.category">
            {{ schedule.category.name }}
          </el-tag>
          <span v-else>无</span>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ new Date(schedule.created_at).toLocaleString('zh-CN') }}
        </el-descriptions-item>
      </el-descriptions>

      <div v-if="schedule.description" class="section">
        <h4>描述</h4>
        <p>{{ schedule.description }}</p>
      </div>

      <div v-if="schedule.tags?.length" class="section">
        <h4>标签</h4>
        <div class="tag-row">
          <TagBadge v-for="t in schedule.tags" :key="t.tag_id" :tag="t" />
        </div>
      </div>

      <div v-if="schedule.recurring" class="section">
        <h4>周期规则</h4>
        <el-tag type="info" effect="plain">
          {{ schedule.recurring.freq === 'daily' ? '每天' : schedule.recurring.freq === 'weekly' ? '每周' : schedule.recurring.freq === 'monthly' ? '每月' : '每年' }}
          ，间隔 {{ schedule.recurring.interval }} 次
        </el-tag>
      </div>

      <div v-if="schedule.reminders?.length" class="section">
        <h4>提醒</h4>
        <el-timeline>
          <el-timeline-item
            v-for="r in schedule.reminders"
            :key="r.reminder_id"
            :timestamp="new Date(r.remind_at).toLocaleString('zh-CN')"
            :type="r.sent ? 'success' : 'primary'"
          >
            {{ r.sent ? '已发送' : '待发送' }}
          </el-timeline-item>
        </el-timeline>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useScheduleStore } from '../stores/schedules.js'
import { ElMessage } from 'element-plus'
import PriorityBadge from '../components/PriorityBadge.vue'
import StatusBadge from '../components/StatusBadge.vue'
import TagBadge from '../components/TagBadge.vue'
import { Edit, Delete } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const store = useScheduleStore()
const schedule = ref(null)
const loading = ref(true)

const statusOptions = [
  { label: '待办', value: 'todo' },
  { label: '进行中', value: 'in_progress' },
  { label: '已完成', value: 'done' },
  { label: '已取消', value: 'cancelled' },
]

onMounted(async () => {
  try {
    schedule.value = await store.fetchSchedule(route.params.id)
  } finally {
    loading.value = false
  }
})

async function changeStatus(status) {
  try {
    schedule.value = await store.changeStatus(route.params.id, status)
    ElMessage.success('状态已更新')
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function handleDelete() {
  try {
    await store.deleteSchedule(route.params.id)
    ElMessage.success('日程已删除')
    router.push('/')
  } catch (e) {
    ElMessage.error(e.message)
  }
}
</script>

<style scoped>
.detail-page { max-width: 750px; }
.detail-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}
.badge-row { display: flex; gap: 8px; margin-bottom: 10px; }
.detail-title { font-size: 26px; font-weight: 700; color: var(--text-primary); }
.hero-actions { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.detail-meta { margin-bottom: 24px; }
.section { margin-bottom: 24px; }
.section h4 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-bottom: 10px;
  letter-spacing: 0.5px;
}
.section p { font-size: 14px; color: var(--text-secondary); line-height: 1.7; }
.tag-row { display: flex; gap: 6px; flex-wrap: wrap; }
</style>
