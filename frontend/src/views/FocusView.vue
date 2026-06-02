<template>
  <div class="focus-view">
    <div class="page-header">
      <h2>&#x1f3af; 专注模式</h2>
      <span class="focus-sub">只显示今天和逾期的待处理日程</span>
    </div>

    <el-skeleton v-if="loading" :rows="4" animated />

    <el-empty v-else-if="schedules.length === 0" description="太棒了，没有待处理的日程！">
      <div class="empty-emoji">&#x1f389;&#x2728;&#x1f389;</div>
      <p style="color: var(--text-muted); font-size: 13px;">所有日程都已处理完毕</p>
    </el-empty>

    <div v-else class="focus-sections">
      <div v-if="overdue.length > 0" class="focus-section overdue-section">
        <div class="section-header">
          <span class="section-dot overdue-dot"></span>
          <span>已逾期</span>
          <el-tag size="small" type="danger" round>{{ overdue.length }}</el-tag>
        </div>
        <div class="focus-grid">
          <ScheduleCard
            v-for="s in overdue"
            :key="s.schedule_id"
            :schedule="s"
            @refresh="load"
          />
        </div>
      </div>

      <div v-if="today.length > 0" class="focus-section today-section">
        <div class="section-header">
          <span class="section-dot today-dot"></span>
          <span>今天</span>
          <el-tag size="small" type="primary" round>{{ today.length }}</el-tag>
        </div>
        <div class="focus-grid">
          <ScheduleCard
            v-for="s in today"
            :key="s.schedule_id"
            :schedule="s"
            @refresh="load"
          />
        </div>
      </div>

      <div v-if="upcoming.length > 0" class="focus-section upcoming-section">
        <div class="section-header">
          <span class="section-dot upcoming-dot"></span>
          <span>即将到来（含逾期）</span>
          <el-tag size="small" type="warning" round>{{ upcoming.length }}</el-tag>
        </div>
        <div class="focus-grid">
          <ScheduleCard
            v-for="s in upcoming"
            :key="s.schedule_id"
            :schedule="s"
            @refresh="load"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../utils/api.js'
import ScheduleCard from '../components/ScheduleCard.vue'

const loading = ref(true)
const schedules = ref([])

const overdue = ref([])
const today = ref([])
const upcoming = ref([])

async function load() {
  loading.value = true
  try {
    const data = await api.listSchedules({ focus: true, per_page: 100 })
    schedules.value = data.items || []
    const now = new Date()
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const todayEnd = new Date(todayStart.getTime() + 86400000)

    overdue.value = schedules.value.filter(s => s.due_date && new Date(s.due_date) < todayStart)
    today.value = schedules.value.filter(s => {
      if (!s.due_date) return false
      const d = new Date(s.due_date)
      return d >= todayStart && d < todayEnd
    })
    upcoming.value = schedules.value.filter(s => s.due_date && new Date(s.due_date) >= todayEnd)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.focus-view { max-width: 900px; }
.page-header { margin-bottom: 20px; }
.page-header h2 { font-size: 24px; font-weight: 700; color: var(--text-primary); }
.focus-sub { font-size: 13px; color: var(--text-muted); margin-top: 4px; display: block; }

.focus-sections { display: flex; flex-direction: column; gap: 24px; }
.focus-section {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 18px;
}
.section-header {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 600; color: var(--text-primary);
  margin-bottom: 14px;
}
.section-dot { width: 10px; height: 10px; border-radius: 50%; }
.overdue-dot { background: #ef4444; }
.today-dot { background: #3b82f6; }
.upcoming-dot { background: #f59e0b; }

.focus-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
}
.empty-emoji { font-size: 32px; margin-bottom: 8px; }
</style>
