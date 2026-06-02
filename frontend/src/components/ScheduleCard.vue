<template>
  <div
    class="schedule-card"
    :class="{ overdue: isOverdue, 'batch-mode': batchMode }"
    @click="onCardClick"
  >
    <!-- Batch checkbox -->
    <div v-if="batchMode" class="batch-check" @click.stop>
      <el-checkbox :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" />
    </div>

    <!-- Quick actions overlay -->
    <div class="quick-actions" @click.stop>
      <el-tooltip content="复制日程" placement="top">
        <el-button size="small" circle @click="handleDuplicate">
          <el-icon :size="14"><CopyDocument /></el-icon>
        </el-button>
      </el-tooltip>
    </div>

    <div class="card-header">
      <StatusBadge :status="schedule.status" />
      <PriorityBadge :priority="schedule.priority" />
    </div>

    <h3 class="card-title">{{ schedule.title }}</h3>
    <p v-if="schedule.description" class="card-desc">{{ schedule.description }}</p>

    <div class="card-meta">
      <span class="meta-item" v-if="schedule.due_date">
        <el-icon :size="14"><Clock /></el-icon>
        <span :class="{ 'text-danger': isOverdue }">
          {{ relativeDate(schedule.due_date) }}
        </span>
      </span>
      <span class="meta-item" v-if="schedule.category?.name">
        <span class="color-dot" :style="{ background: schedule.category.color }"></span>
        {{ schedule.category.name }}
      </span>
    </div>

    <div v-if="schedule.tags?.length" class="card-tags">
      <TagBadge v-for="t in schedule.tags" :key="t.tag_id" :tag="t" />
    </div>

    <div v-if="schedule.subtasks?.length" class="card-subtasks">
      <div class="subtask-progress">
        <span class="subtask-bar-bg">
          <span class="subtask-bar-fill" :style="{ width: subtaskPct + '%' }"></span>
        </span>
        <span class="subtask-text">{{ subtaskDone }}/{{ schedule.subtasks.length }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Clock, CopyDocument } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { api } from '../utils/api.js'
import PriorityBadge from './PriorityBadge.vue'
import StatusBadge from './StatusBadge.vue'
import TagBadge from './TagBadge.vue'

const props = defineProps({
  schedule: Object,
  batchMode: { type: Boolean, default: false },
  modelValue: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue', 'refresh'])
const router = useRouter()

const isOverdue = computed(() => {
  if (!props.schedule.due_date || props.schedule.status === 'done' || props.schedule.status === 'cancelled') return false
  return new Date(props.schedule.due_date) < new Date()
})

const subtaskDone = computed(() => {
  return (props.schedule.subtasks || []).filter(s => s.completed).length
})
const subtaskPct = computed(() => {
  if (!props.schedule.subtasks?.length) return 0
  return Math.round((subtaskDone.value / props.schedule.subtasks.length) * 100)
})

function relativeDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diffDays = Math.ceil((d - now) / (1000 * 60 * 60 * 24))
  if (diffDays < 0) return `逾期 ${Math.abs(diffDays)} 天`
  if (diffDays === 0) return '今天到期'
  if (diffDays === 1) return '明天到期'
  return `${diffDays} 天后到期`
}

function onCardClick() {
  if (props.batchMode) {
    emit('update:modelValue', !props.modelValue)
  } else {
    router.push(`/schedules/${props.schedule.schedule_id}`)
  }
}

async function handleDuplicate() {
  try {
    await api.duplicateSchedule(props.schedule.schedule_id)
    ElMessage.success('日程已复制')
    emit('refresh')
  } catch (e) {
    ElMessage.error(e.message)
  }
}
</script>

<style scoped>
.schedule-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
}
.schedule-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  border-color: #6366f1;
}
.schedule-card.overdue {
  border-left: 3px solid #ef4444;
}

/* Batch mode */
.batch-check {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 2;
}
.schedule-card.batch-mode {
  padding-left: 44px;
}

/* Quick actions */
.quick-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity var(--transition-fast);
  z-index: 2;
}
.schedule-card:hover .quick-actions {
  opacity: 1;
}
.schedule-card.batch-mode .quick-actions {
  display: none;
}

.card-header {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}
.card-desc {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.card-meta {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 10px;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-muted);
}
.text-danger { color: #f87171 !important; }
.color-dot {
  width: 8px; height: 8px; border-radius: 50%; display: inline-block;
}
.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.card-subtasks { margin-top: 10px; }
.subtask-progress { display: flex; align-items: center; gap: 8px; }
.subtask-bar-bg {
  flex: 1;
  height: 4px;
  background: #334155;
  border-radius: 2px;
  overflow: hidden;
}
.subtask-bar-fill {
  display: block;
  height: 100%;
  background: #22c55e;
  border-radius: 2px;
  transition: width var(--transition-normal);
}
.subtask-text { font-size: 11px; color: var(--text-muted); white-space: nowrap; }
</style>
