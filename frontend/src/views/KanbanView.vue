<template>
  <div class="kanban-page" v-loading="loading">
    <div class="page-header">
      <h2>&#x1f3af; 看板视图</h2>
    </div>

    <div class="kanban-board">
      <div
        v-for="col in columns"
        :key="col.status"
        class="kanban-col"
        :class="col.cls"
        @dragover.prevent="onDragOver($event, col.status)"
        @dragenter.prevent
        @drop="onDrop($event, col.status)"
      >
        <div class="col-header">
          <div class="col-title">
            <span class="col-dot" :class="col.cls"></span>
            {{ col.label }}
            <el-tag size="small" round>{{ col.schedules.length }}</el-tag>
          </div>
        </div>
        <div class="col-body">
          <div
            v-for="s in col.schedules"
            :key="s.schedule_id"
            class="kanban-card"
            draggable="true"
            @dragstart="onDragStart($event, s.schedule_id)"
            @click="$router.push(`/schedules/${s.schedule_id}`)"
          >
            <div class="kc-top">
              <PriorityBadge :priority="s.priority" />
            </div>
            <div class="kc-title">{{ s.title }}</div>
            <div class="kc-meta" v-if="s.due_date">
              <el-icon :size="12"><Clock /></el-icon>
              <span :class="{ 'text-danger': isOverdue(s) }">{{ relativeDate(s.due_date) }}</span>
            </div>
            <div class="kc-footer" v-if="s.category || s.tags?.length">
              <el-tag v-if="s.category" :color="s.category.color" effect="dark" size="small">
                {{ s.category.name }}
              </el-tag>
              <TagBadge v-for="t in (s.tags || []).slice(0, 2)" :key="t.tag_id" :tag="t" />
            </div>
          </div>
          <div v-if="col.schedules.length === 0" class="col-empty">
            <span class="empty-icon">{{ col.emptyEmoji }}</span>
            暂无日程
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../utils/api.js'
import { Clock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PriorityBadge from '../components/PriorityBadge.vue'
import TagBadge from '../components/TagBadge.vue'

const loading = ref(true)
const schedules = ref([])
let dragId = null

const columns = [
  { status: 'todo', label: '待办', cls: 'todo', schedules: [], emptyEmoji: '\u{1f4cb}' },
  { status: 'in_progress', label: '进行中', cls: 'progress', schedules: [], emptyEmoji: '\u{1f3c3}' },
  { status: 'done', label: '已完成', cls: 'done', schedules: [], emptyEmoji: '\u{1f389}' },
  { status: 'cancelled', label: '已取消', cls: 'cancelled', schedules: [], emptyEmoji: '\u{1f4a4}' },
]

function buildBoard() {
  for (const col of columns) {
    col.schedules = schedules.value.filter(s => s.status === col.status)
  }
}

function isOverdue(s) {
  if (!s.due_date || s.status === 'done' || s.status === 'cancelled') return false
  return new Date(s.due_date) < new Date()
}

function relativeDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const diff = Math.ceil((d - new Date()) / (1000 * 60 * 60 * 24))
  if (diff < 0) return `逾期 ${Math.abs(diff)} 天`
  if (diff === 0) return '今天'
  if (diff === 1) return '明天'
  return `${diff} 天后`
}

function onDragStart(e, id) {
  dragId = id
  e.dataTransfer.effectAllowed = 'move'
}

function onDragOver(e, status) {
  e.dataTransfer.dropEffect = 'move'
}

async function onDrop(e, newStatus) {
  if (!dragId) return
  try {
    await api.changeStatus(dragId, newStatus)
    const s = schedules.value.find(s => s.schedule_id === dragId)
    if (s) s.status = newStatus
    buildBoard()
    ElMessage.success('状态已更新')
  } catch (e) {
    ElMessage.error(e.message)
  }
  dragId = null
}

onMounted(async () => {
  try {
    const data = await api.listSchedules({ per_page: 100 })
    schedules.value = data.items || []
    buildBoard()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.kanban-page { max-width: 100%; }
.page-header { margin-bottom: 20px; }
.page-header h2 { font-size: 24px; color: var(--text-primary); }

.kanban-board {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 20px;
  min-height: calc(100vh - 200px);
}

.kanban-col {
  flex: 1;
  min-width: 270px;
  max-width: 360px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}

.col-header {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-color);
}
.col-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 14px;
  color: var(--text-secondary);
}
.col-dot {
  width: 10px; height: 10px; border-radius: 50%;
}
.col-dot.todo { background: #64748b; }
.col-dot.progress { background: #3b82f6; }
.col-dot.done { background: #22c55e; }
.col-dot.cancelled { background: #71717a; }

.col-body {
  flex: 1;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  min-height: 200px;
}

.kanban-card {
  background: var(--bg-base);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 14px;
  cursor: grab;
  transition: all var(--transition-fast);
}
.kanban-card:hover {
  border-color: #6366f1;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.kanban-card:active { cursor: grabbing; }

.kc-top { margin-bottom: 8px; }
.kc-title {
  font-size: 14px; font-weight: 600; color: var(--text-primary);
  margin-bottom: 6px; line-height: 1.4;
}
.kc-meta {
  display: flex; align-items: center; gap: 4px;
  font-size: 12px; color: var(--text-muted); margin-bottom: 6px;
}
.text-danger { color: #f87171 !important; }
.kc-footer { display: flex; gap: 4px; flex-wrap: wrap; }
.col-empty {
  text-align: center; padding: 40px 0; color: var(--text-muted); font-size: 13px;
}
.empty-icon { display: block; font-size: 28px; margin-bottom: 4px; }
</style>
