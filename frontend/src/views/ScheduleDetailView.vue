<template>
  <div class="detail-page" v-if="schedule">
    <div class="detail-header">
      <div>
        <div class="badge-row">
          <StatusBadge :status="schedule.status" />
          <PriorityBadge :priority="schedule.priority" />
        </div>
        <h2>{{ schedule.title }}</h2>
      </div>
      <div class="detail-actions">
        <select @change="changeStatus($event.target.value)" :value="schedule.status">
          <option value="todo">Todo</option>
          <option value="in_progress">In Progress</option>
          <option value="done">Done</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <router-link :to="`/schedules/${schedule.schedule_id}/edit`" class="btn-edit">Edit</router-link>
        <button @click="handleDelete" class="btn-delete">Delete</button>
      </div>
    </div>

    <div v-if="schedule.description" class="section">
      <h4>Description</h4>
      <p>{{ schedule.description }}</p>
    </div>

    <div class="meta-grid">
      <div class="meta-item">
        <span class="meta-label">Due Date</span>
        <span class="meta-value">{{ formatDateTime(schedule.due_date) || 'Not set' }}</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Estimated</span>
        <span class="meta-value">{{ schedule.estimated_minutes ? schedule.estimated_minutes + ' min' : 'Not set' }}</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Category</span>
        <span class="meta-value" :style="{ color: schedule.category?.color }">
          {{ schedule.category?.name || 'None' }}
        </span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Created</span>
        <span class="meta-value">{{ formatDateTime(schedule.created_at) }}</span>
      </div>
    </div>

    <div v-if="schedule.tags?.length" class="section">
      <h4>Tags</h4>
      <div class="tags-row">
        <TagBadge v-for="t in schedule.tags" :key="t.tag_id" :tag="t" />
      </div>
    </div>

    <div v-if="schedule.recurring" class="section">
      <h4>Recurring</h4>
      <p>{{ schedule.recurring.freq }}, every {{ schedule.recurring.interval }} from {{ schedule.recurring.start_date }}<span v-if="schedule.recurring.end_date"> to {{ schedule.recurring.end_date }}</span></p>
    </div>

    <div v-if="schedule.reminders?.length" class="section">
      <h4>Reminders</h4>
      <div v-for="r in schedule.reminders" :key="r.reminder_id" class="reminder-item">
        <span>{{ formatDateTime(r.remind_at) }}</span>
        <span>{{ r.sent ? 'Sent' : 'Pending' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useScheduleStore } from '../stores/schedules.js'
import { formatDateTime } from '../utils/date.js'
import PriorityBadge from '../components/PriorityBadge.vue'
import StatusBadge from '../components/StatusBadge.vue'
import TagBadge from '../components/TagBadge.vue'

const route = useRoute()
const router = useRouter()
const store = useScheduleStore()
const schedule = ref(null)

onMounted(async () => {
  schedule.value = await store.fetchSchedule(route.params.id)
})

async function changeStatus(status) {
  schedule.value = await store.changeStatus(route.params.id, status)
}

async function handleDelete() {
  if (confirm('Delete this task?')) {
    await store.deleteSchedule(route.params.id)
    router.push('/')
  }
}
</script>

<style scoped>
.detail-page { max-width: 750px; }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 28px; }
.badge-row { display: flex; gap: 8px; margin-bottom: 10px; }
h2 { font-size: 24px; color: #f1f5f9; }
.detail-actions { display: flex; gap: 8px; align-items: center; }
.detail-actions select {
  padding: 8px 12px; border-radius: 8px; border: 1px solid #334155;
  background: #1e293b; color: #e2e8f0; font-size: 13px;
}
.btn-edit {
  padding: 8px 18px; background: #6366f1; color: #fff; border-radius: 8px; font-size: 13px;
}
.btn-delete {
  padding: 8px 18px; background: #7f1d1d; color: #fca5a5; border: none; border-radius: 8px; cursor: pointer; font-size: 13px;
}
.btn-delete:hover { background: #991b1b; }

.section { margin-bottom: 20px; }
.section h4 { font-size: 13px; font-weight: 600; color: #64748b; margin-bottom: 8px; text-transform: uppercase; }
.section p { font-size: 14px; color: #cbd5e1; line-height: 1.6; }

.meta-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 20px; }
.meta-item { background: #1e293b; padding: 14px; border-radius: 10px; border: 1px solid #334155; }
.meta-label { display: block; font-size: 12px; color: #64748b; margin-bottom: 4px; }
.meta-value { font-size: 14px; color: #e2e8f0; }

.tags-row { display: flex; gap: 6px; flex-wrap: wrap; }
.reminder-item {
  display: flex; justify-content: space-between; padding: 8px 0;
  border-bottom: 1px solid #1e293b; font-size: 13px; color: #cbd5e1;
}
</style>
