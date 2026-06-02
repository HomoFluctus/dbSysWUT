<template>
  <div class="form-page">
    <h2>{{ isEdit ? 'Edit Task' : 'New Task' }}</h2>
    <form @submit.prevent="handleSubmit" class="schedule-form">
      <div class="form-group">
        <label>Title *</label>
        <input v-model="form.title" required placeholder="Task title" />
      </div>
      <div class="form-group">
        <label>Description</label>
        <textarea v-model="form.description" rows="3" placeholder="Task description"></textarea>
      </div>

      <div class="form-row">
        <div class="form-group flex-1">
          <label>Priority</label>
          <select v-model="form.priority">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>
        <div class="form-group flex-1">
          <label>Status</label>
          <select v-model="form.status">
            <option value="todo">Todo</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group flex-1">
          <label>Due Date</label>
          <input v-model="form.due_date" type="datetime-local" />
        </div>
        <div class="form-group flex-1">
          <label>Estimated (minutes)</label>
          <input v-model.number="form.estimated_minutes" type="number" min="0" />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group flex-1">
          <label>Category</label>
          <select v-model="form.category_id">
            <option :value="null">None</option>
            <option v-for="c in catStore.categories" :key="c.category_id" :value="c.category_id">{{ c.name }}</option>
          </select>
        </div>
        <div class="form-group flex-1">
          <label>Tags</label>
          <div class="tag-select">
            <label v-for="t in tagStore.tags" :key="t.tag_id" class="tag-checkbox">
              <input type="checkbox" :value="t.tag_id" v-model="form.tag_ids" />
              <span :style="{ color: t.color }">{{ t.name }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Recurring -->
      <div class="form-section">
        <label class="checkbox-label">
          <input type="checkbox" v-model="enableRecurring" /> Recurring Task
        </label>
        <div v-if="enableRecurring" class="recurring-row">
          <select v-model="recurring.freq">
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="yearly">Yearly</option>
          </select>
          <input v-model.number="recurring.interval" type="number" min="1" placeholder="Interval" style="width:80px" />
          <input v-model="recurring.start_date" type="date" required />
          <input v-model="recurring.end_date" type="date" placeholder="End (optional)" />
        </div>
      </div>

      <!-- Reminders -->
      <div class="form-section">
        <label>Reminders</label>
        <div v-for="(r, i) in reminders" :key="i" class="reminder-row">
          <input v-model="r.remind_at" type="datetime-local" />
          <button type="button" class="btn-sm btn-danger" @click="reminders.splice(i, 1)">Remove</button>
        </div>
        <button type="button" class="btn-sm" @click="reminders.push({ remind_at: '', method: 'push' })">+ Add Reminder</button>
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <div class="form-actions">
        <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Saving...' : 'Save' }}</button>
        <button type="button" class="btn-cancel" @click="$router.back()">Cancel</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useScheduleStore } from '../stores/schedules.js'
import { useCategoryStore } from '../stores/categories.js'
import { useTagStore } from '../stores/tags.js'
import { api } from '../utils/api.js'

const route = useRoute()
const router = useRouter()
const store = useScheduleStore()
const catStore = useCategoryStore()
const tagStore = useTagStore()

const isEdit = ref(!!route.params.id)
const saving = ref(false)
const error = ref('')

const form = ref({
  title: '', description: '', priority: 'medium', status: 'todo',
  due_date: '', estimated_minutes: null, category_id: null, tag_ids: [],
})

const enableRecurring = ref(false)
const recurring = ref({ freq: 'daily', interval: 1, start_date: '', end_date: '' })
const reminders = ref([])

onMounted(async () => {
  await catStore.fetchCategories()
  await tagStore.fetchTags()

  if (isEdit.value) {
    const s = await store.fetchSchedule(route.params.id)
    form.value = {
      title: s.title, description: s.description || '', priority: s.priority,
      status: s.status, due_date: s.due_date ? s.due_date.slice(0, 16) : '',
      estimated_minutes: s.estimated_minutes, category_id: s.category_id,
      tag_ids: s.tags?.map(t => t.tag_id) || [],
    }
    if (s.recurring) {
      enableRecurring.value = true
      recurring.value = {
        freq: s.recurring.freq, interval: s.recurring.interval,
        start_date: s.recurring.start_date, end_date: s.recurring.end_date || '',
      }
    }
    if (s.reminders?.length) {
      reminders.value = s.reminders.map(r => ({
        remind_at: r.remind_at.slice(0, 16), method: r.method,
        _id: r.reminder_id,
      }))
    }
  }
})

async function handleSubmit() {
  saving.value = true
  error.value = ''
  try {
    const data = { ...form.value }
    if (!data.due_date) data.due_date = null
    if (!data.description) data.description = null
    if (data.estimated_minutes === '' || data.estimated_minutes === null) data.estimated_minutes = null

    let schedule
    if (isEdit.value) {
      schedule = await store.updateSchedule(route.params.id, data)
      // Update recurring
      if (enableRecurring.value) {
        await api.upsertRecurring(schedule.schedule_id, { ...recurring.value, end_date: recurring.value.end_date || null })
      } else {
        await api.deleteRecurring(schedule.schedule_id).catch(() => {})
      }
    } else {
      schedule = await store.createSchedule(data)
      if (enableRecurring.value) {
        await api.upsertRecurring(schedule.schedule_id, { ...recurring.value, end_date: recurring.value.end_date || null })
      }
      for (const r of reminders.value) {
        if (r.remind_at) {
          await api.createReminder(schedule.schedule_id, { remind_at: r.remind_at + ':00', method: r.method })
        }
      }
    }

    router.push(`/schedules/${schedule.schedule_id}`)
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.form-page { max-width: 700px; }
h2 { font-size: 24px; color: #f1f5f9; margin-bottom: 24px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; color: #94a3b8; margin-bottom: 6px; }
input, textarea, select {
  display: block; width: 100%; padding: 10px 14px; border-radius: 8px;
  border: 1px solid #334155; background: #1e293b; color: #e2e8f0; font-size: 14px;
}
textarea { resize: vertical; }
.form-row { display: flex; gap: 16px; }
.flex-1 { flex: 1; }
.tag-select { display: flex; flex-wrap: wrap; gap: 8px; }
.tag-checkbox { display: flex; align-items: center; gap: 4px; font-size: 13px; cursor: pointer; }
.tag-checkbox input { width: auto; }

.form-section { margin: 20px 0; padding: 16px; background: #1e293b; border-radius: 10px; border: 1px solid #334155; }
.checkbox-label { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #e2e8f0; cursor: pointer; margin-bottom: 12px; }
.checkbox-label input { width: auto; }
.recurring-row { display: flex; gap: 8px; align-items: center; }
.recurring-row select, .recurring-row input { width: auto; }
.reminder-row { display: flex; gap: 8px; margin-bottom: 8px; }
.reminder-row input { flex: 1; }

.btn-sm { padding: 6px 12px; border-radius: 6px; border: 1px solid #334155; background: #1e293b; color: #e2e8f0; cursor: pointer; font-size: 12px; }
.btn-sm:hover { background: #334155; }
.btn-danger { color: #f87171; border-color: #7f1d1d; }
.btn-danger:hover { background: #7f1d1d; }

.form-actions { display: flex; gap: 12px; margin-top: 28px; }
.btn-primary { padding: 12px 28px; background: #6366f1; color: #fff; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; }
.btn-primary:hover { background: #4f46e5; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-cancel { padding: 12px 28px; background: #334155; color: #e2e8f0; border: none; border-radius: 8px; font-size: 15px; cursor: pointer; }
.btn-cancel:hover { background: #475569; }
.error { color: #f87171; font-size: 13px; margin-top: -8px; }
</style>
