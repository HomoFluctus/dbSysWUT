<template>
  <div class="card" :class="{ overdue: isOverdue }" @click="$router.push(`/schedules/${schedule.schedule_id}`)">
    <div class="card-top">
      <StatusBadge :status="schedule.status" />
      <PriorityBadge :priority="schedule.priority" />
    </div>
    <h3>{{ schedule.title }}</h3>
    <p v-if="schedule.description" class="desc">{{ schedule.description }}</p>
    <div class="card-meta">
      <span v-if="schedule.due_date" class="due" :class="{ overdue: isOverdue }">
        {{ formatDate(schedule.due_date) }}
      </span>
      <span v-if="schedule.category" class="cat" :style="{ color: schedule.category.color }">
        {{ schedule.category.name }}
      </span>
    </div>
    <div v-if="schedule.tags?.length" class="tags">
      <TagBadge v-for="t in schedule.tags" :key="t.tag_id" :tag="t" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatDate, isOverdue as checkOverdue } from '../utils/date.js'
import PriorityBadge from './PriorityBadge.vue'
import StatusBadge from './StatusBadge.vue'
import TagBadge from './TagBadge.vue'

const props = defineProps({ schedule: Object })
const isOverdue = computed(() => checkOverdue(props.schedule.due_date, props.schedule.status))
</script>

<style scoped>
.card {
  background: #1e293b; border: 1px solid #334155; border-radius: 12px;
  padding: 18px; cursor: pointer; transition: all 0.15s;
}
.card:hover { border-color: #6366f1; }
.card.overdue { border-color: #7f1d1d; }
.card-top { display: flex; gap: 8px; margin-bottom: 10px; }
h3 { font-size: 15px; font-weight: 600; color: #f1f5f9; margin-bottom: 6px; }
.desc { font-size: 13px; color: #94a3b8; margin-bottom: 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card-meta { display: flex; gap: 16px; align-items: center; margin-bottom: 8px; }
.due { font-size: 12px; color: #94a3b8; }
.due.overdue { color: #f87171; }
.cat { font-size: 12px; font-weight: 500; }
.tags { display: flex; flex-wrap: wrap; gap: 4px; }
</style>
