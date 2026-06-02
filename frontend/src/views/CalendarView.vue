<template>
  <div class="calendar-page">
    <div class="cal-header">
      <el-button :icon="ArrowLeft" circle @click="prevMonth" />
      <h2>{{ year }} 年 {{ month }} 月</h2>
      <el-button :icon="ArrowRight" circle @click="nextMonth" />
      <el-button @click="goToday" class="today-btn">今天</el-button>
    </div>

    <div class="cal-grid">
      <div class="cal-day-header" v-for="d in dayNames" :key="d">{{ d }}</div>
      <div
        v-for="cell in cells"
        :key="cell.key"
        class="cal-cell"
        :class="{ 'other-month': !cell.isCurrentMonth, today: cell.isToday }"
        @click="showDayDetail(cell)"
      >
        <span class="cell-date">{{ cell.day }}</span>
        <div class="cell-events">
          <div
            v-for="s in cell.schedules.slice(0, 3)"
            :key="s.schedule_id"
            class="cell-event"
            :style="{ borderLeftColor: priorityColor(s.priority) }"
            @click.stop="$router.push(`/schedules/${s.schedule_id}`)"
          >
            {{ s.title }}
          </div>
          <div v-if="cell.schedules.length > 3" class="cell-more">
            +{{ cell.schedules.length - 3 }}
          </div>
        </div>
      </div>
    </div>

    <!-- Day Detail Drawer -->
    <el-drawer v-model="drawerVisible" :title="drawerTitle" size="360px">
      <div v-if="drawerSchedules.length === 0" class="empty-day">
        <el-empty description="当天暂无日程" :image-size="80" />
      </div>
      <div v-else class="day-list">
        <div v-for="s in drawerSchedules" :key="s.schedule_id" class="day-item" @click="$router.push(`/schedules/${s.schedule_id}`); drawerVisible=false">
          <div class="day-item-top">
            <StatusBadge :status="s.status" />
            <PriorityBadge :priority="s.priority" />
          </div>
          <div class="day-item-title">{{ s.title }}</div>
          <div class="day-item-desc" v-if="s.description">{{ s.description }}</div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../utils/api.js'
import PriorityBadge from '../components/PriorityBadge.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const now = new Date()
const year = ref(now.getFullYear())
const month = ref(now.getMonth() + 1)
const schedules = ref([])
const drawerVisible = ref(false)
const drawerTitle = ref('')
const drawerSchedules = ref([])

const dayNames = ['日', '一', '二', '三', '四', '五', '六']

const priorityColor = (p) => ({ low: '#22c55e', medium: '#eab308', high: '#f97316', urgent: '#ef4444' }[p] || '#64748b')

const cells = computed(() => {
  const firstDay = new Date(year.value, month.value - 1, 1)
  const startDow = firstDay.getDay()
  const daysInMonth = new Date(year.value, month.value, 0).getDate()
  const daysInPrevMonth = new Date(year.value, month.value - 1, 0).getDate()
  const todayStr = new Date().toISOString().split('T')[0]
  const result = []

  for (let i = startDow - 1; i >= 0; i--) {
    const d = daysInPrevMonth - i
    const ds = `${year.value}-${String(month.value > 1 ? month.value - 1 : 12).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    result.push(buildCell(d, ds, false, todayStr))
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const ds = `${year.value}-${String(month.value).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    result.push(buildCell(d, ds, true, todayStr))
  }
  let nextD = 1
  while (result.length < 42) {
    const nm = month.value + 1 > 12 ? 1 : month.value + 1
    const ds = `${year.value}-${String(nm).padStart(2, '0')}-${String(nextD).padStart(2, '0')}`
    result.push(buildCell(nextD, ds, false, todayStr))
    nextD++
  }
  return result
})

function buildCell(day, dateStr, isCur, todayStr) {
  return {
    key: dateStr, day, dateStr,
    isCurrentMonth: isCur,
    isToday: dateStr === todayStr,
    schedules: schedules.value.filter(s => s.due_date?.startsWith(dateStr)),
  }
}

async function loadMonth() {
  schedules.value = await api.getMonthCalendar(year.value, month.value)
}

function prevMonth() {
  if (month.value === 1) { month.value = 12; year.value-- } else month.value--
  loadMonth()
}
function nextMonth() {
  if (month.value === 12) { month.value = 1; year.value++ } else month.value++
  loadMonth()
}
function goToday() {
  year.value = now.getFullYear(); month.value = now.getMonth() + 1
  loadMonth()
}
function showDayDetail(cell) {
  drawerTitle.value = cell.dateStr
  drawerSchedules.value = cell.schedules
  drawerVisible.value = true
}

onMounted(loadMonth)
</script>

<style scoped>
.calendar-page { max-width: 1000px; }
.cal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.cal-header h2 { font-size: 20px; color: var(--text-primary); min-width: 150px; text-align: center; }
.today-btn { margin-left: auto; }

.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 1px; background: var(--border-color); border-radius: 12px; overflow: hidden; }
.cal-day-header { padding: 10px; text-align: center; font-size: 12px; font-weight: 600; color: var(--text-muted); background: var(--bg-surface); }
.cal-cell {
  min-height: 110px;
  background: var(--bg-surface);
  padding: 8px;
  cursor: pointer;
  transition: background var(--transition-fast);
}
.cal-cell:hover { background: var(--el-fill-color); }
.cal-cell.other-month { opacity: 0.4; }
.cal-cell.today { box-shadow: inset 0 2px 0 #818cf8; background: var(--el-color-primary-light-9); }
html.dark .cal-cell.today { background: rgba(99,102,241,0.05); }
.cell-date { font-size: 12px; color: var(--text-muted); display: block; margin-bottom: 4px; }
.cell-event {
  font-size: 11px;
  padding: 2px 6px;
  margin-bottom: 2px;
  border-radius: 3px;
  background: var(--el-fill-color-light);
  border-left: 3px solid;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}
.cell-more { font-size: 11px; color: var(--el-color-primary); padding: 2px 6px; cursor: pointer; }

.day-list { display: flex; flex-direction: column; gap: 8px; }
.day-item {
  background: var(--bg-base); border: 1px solid var(--border-color);
  border-radius: 10px; padding: 14px; cursor: pointer;
  transition: border-color var(--transition-fast);
}
.day-item:hover { border-color: #6366f1; }
.day-item-top { display: flex; gap: 6px; margin-bottom: 8px; }
.day-item-title { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.day-item-desc { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
.empty-day { padding: 60px 0; }
</style>
