<template>
  <div class="activity-page" v-loading="loading">
    <div class="page-head">
      <h2>&#x1f4c3; 活动日志</h2>
      <el-select v-model="actionFilter" placeholder="全部操作" clearable @change="load(1)" size="default" style="width: 150px">
        <el-option label="创建" value="created" />
        <el-option label="更新" value="updated" />
        <el-option label="状态变更" value="status_changed" />
      </el-select>
    </div>

    <el-empty v-if="!loading && items.length === 0" description="暂无活动记录" :image-size="80" />

    <el-timeline v-else>
      <el-timeline-item
        v-for="log in items"
        :key="log.log_id"
        :timestamp="new Date(log.created_at).toLocaleString('zh-CN')"
        :type="actionType(log.action)"
        placement="top"
      >
        <div class="log-card" @click="goSchedule(log.schedule_id)">
          <div class="log-action">{{ actionLabel(log) }}</div>
          <div class="log-title" v-if="log.schedule_title">&#x1f4cb; {{ log.schedule_title }}</div>
          <div class="log-detail" v-if="log.field_changed">
            {{ log.field_changed }}: {{ log.old_value || '(空)' }} → {{ log.new_value }}
          </div>
        </div>
      </el-timeline-item>
    </el-timeline>

    <div v-if="total > perPage" class="pagination-wrap">
      <el-pagination
        :current-page="page"
        :page-size="perPage"
        :total="total"
        layout="prev, pager, next"
        @current-change="load"
        background
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../utils/api.js'

const router = useRouter()
const loading = ref(true)
const items = ref([])
const page = ref(1)
const total = ref(0)
const perPage = 30
const actionFilter = ref('')

const actionLabels = {
  created: '创建了日程',
  updated: '更新了日程',
  status_changed: '变更了状态',
}

function actionType(action) {
  return action === 'created' ? 'success' : action === 'status_changed' ? 'primary' : 'info'
}

function actionLabel(log) {
  return actionLabels[log.action] || log.action
}

function goSchedule(id) {
  if (id) router.push(`/schedules/${id}`)
}

async function load(p) {
  page.value = p || page.value
  loading.value = true
  try {
    const params = { page: page.value, per_page: perPage }
    if (actionFilter.value) params.action = actionFilter.value
    const data = await api.listActivityLogs(params)
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

onMounted(() => load(1))
</script>

<style scoped>
.activity-page { max-width: 700px; }
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.page-head h2 { font-size: 24px; color: var(--text-primary); }

.log-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 14px 16px;
  cursor: pointer;
  transition: border-color var(--transition-fast);
}
.log-card:hover { border-color: #6366f1; }
.log-action { font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.log-title { font-size: 13px; color: var(--text-secondary); }
.log-detail { font-size: 12px; color: var(--text-muted); margin-top: 4px; }

.pagination-wrap { display: flex; justify-content: center; margin-top: 24px; }
</style>
