<template>
  <div class="calendar-page">
    <div class="cal-header">
      <button @click="prevMonth">&lt;</button>
      <h2>{{ year }} / {{ month }}</h2>
      <button @click="nextMonth">&gt;</button>
      <button @click="goToday" class="btn-today">Today</button>
    </div>

    <div class="cal-grid">
      <div class="cal-day-header" v-for="d in dayNames" :key="d">{{ d }}</div>
      <div
        v-for="cell in cells"
        :key="cell.key"
        class="cal-cell"
        :class="{ 'other-month': !cell.isCurrentMonth, today: cell.isToday }"
        @click="cell.schedules.length && showDayDetail(cell)"
      >
        <span class="cell-date">{{ cell.day }}</span>
        <div class="cell-schedules">
          <div
            v-for="s in cell.schedules.slice(0, 3)"
            :key="s.schedule_id"
            class="cell-event"
            :style="{ borderLeftColor: getPriorityColor(s.priority) }"
            @click.stop="$router.push(`/schedules/${s.schedule_id}`)"
          >
            {{ s.title }}
          </div>
          <div v-if="cell.schedules.length > 3" class="cell-more">
            +{{ cell.schedules.length - 3 }} more
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../utils/api.js'
import { getPriorityColor } from '../utils/date.js'

const router = useRouter()
const now = new Date()
const year = ref(now.getFullYear())
const month = ref(now.getMonth() + 1)
const schedules = ref([])

const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

const cells = computed(() => {
  const firstDay = new Date(year.value, month.value - 1, 1)
  const startDow = firstDay.getDay()
  const daysInMonth = new Date(year.value, month.value, 0).getDate()
  const daysInPrevMonth = new Date(year.value, month.value - 1, 0).getDate()

  const todayStr = new Date().toISOString().split('T')[0]
  const result = []
  let weekTotal = 0

  // Previous month fill
  for (let i = startDow - 1; i >= 0; i--) {
    const d = daysInPrevMonth - i
    const dateStr = `${year.value}-${String(month.value - 1 || 12).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    result.push(buildCell(d, dateStr, false, todayStr))
    weekTotal++
  }

  // Current month
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${year.value}-${String(month.value).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    result.push(buildCell(d, dateStr, true, todayStr))
    weekTotal++
  }

  // Next month fill (complete to 42 = 6 rows)
  let nextD = 1
  while (result.length < 42) {
    const dateStr = `${year.value}-${String(month.value + 1 > 12 ? 1 : month.value + 1).padStart(2, '0')}-${String(nextD).padStart(2, '0')}`
    result.push(buildCell(nextD, dateStr, false, todayStr))
    nextD++
  }

  return result
})

function buildCell(day, dateStr, isCur, todayStr) {
  return {
    key: dateStr,
    day,
    dateStr,
    isCurrentMonth: isCur,
    isToday: dateStr === todayStr,
    schedules: schedules.value.filter(s => s.due_date?.startsWith(dateStr)),
  }
}

async function loadMonth() {
  schedules.value = await api.getMonthCalendar(year.value, month.value)
}

function prevMonth() {
  if (month.value === 1) { month.value = 12; year.value-- }
  else month.value--
  loadMonth()
}
function nextMonth() {
  if (month.value === 12) { month.value = 1; year.value++ }
  else month.value++
  loadMonth()
}
function goToday() {
  year.value = now.getFullYear()
  month.value = now.getMonth() + 1
  loadMonth()
}

function showDayDetail(cell) {
  // Navigate to a day view or show quick detail
}

onMounted(loadMonth)
</script>

<style scoped>
.calendar-page { max-width: 1000px; }
.cal-header { display: flex; align-items: center; gap: 16px; margin-bottom: 20px; }
.cal-header h2 { font-size: 20px; color: #f1f5f9; min-width: 140px; text-align: center; }
.cal-header button {
  padding: 8px 16px; border-radius: 8px; border: 1px solid #334155;
  background: #1e293b; color: #e2e8f0; cursor: pointer;
}
.cal-header button:hover { background: #334155; }
.btn-today { margin-left: auto; }

.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; }
.cal-day-header {
  padding: 10px; text-align: center; font-size: 12px; font-weight: 600;
  color: #64748b; text-transform: uppercase;
}
.cal-cell {
  min-height: 110px; background: #1e293b; border: 1px solid #334155;
  border-radius: 6px; padding: 8px; cursor: pointer; transition: border-color 0.15s;
}
.cal-cell:hover { border-color: #6366f1; }
.cal-cell.other-month { opacity: 0.35; }
.cal-cell.today { border-color: #6366f1; }
.cell-date { font-size: 12px; color: #94a3b8; display: block; margin-bottom: 4px; }
.cell-event {
  font-size: 11px; padding: 2px 6px; margin-bottom: 2px; border-radius: 4px;
  background: #0f172a; border-left: 3px solid #6366f1; color: #e2e8f0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: pointer;
}
.cell-more { font-size: 11px; color: #6366f1; padding: 2px 6px; }
</style>
