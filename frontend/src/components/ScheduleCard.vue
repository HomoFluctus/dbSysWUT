<template>
  <div
    class="schedule-card"
    :class="{ overdue: isOverdue }"
    @click="$router.push(`/schedules/${schedule.schedule_id}`)"
  >
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
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Clock } from '@element-plus/icons-vue'
import PriorityBadge from './PriorityBadge.vue'
import StatusBadge from './StatusBadge.vue'
import TagBadge from './TagBadge.vue'

const props = defineProps({ schedule: Object })

const isOverdue = computed(() => {
  if (!props.schedule.due_date || props.schedule.status === 'done' || props.schedule.status === 'cancelled') return false
  return new Date(props.schedule.due_date) < new Date()
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
</script>

<style scoped>
.schedule-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all var(--transition-normal);
}
.schedule-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  border-color: #6366f1;
}
.schedule-card.overdue {
  border-left: 3px solid #ef4444;
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
</style>
