<template>
  <div class="stats-page">
    <h2>Statistics</h2>

    <div class="chart-grid">
      <div class="chart-card">
        <h3>Status Overview</h3>
        <StatisticsChart v-if="overviewData" type="doughnut" :data="overviewData" />
      </div>
      <div class="chart-card">
        <h3>Completion Rate (30 days)</h3>
        <StatisticsChart v-if="completionData" type="bar" :data="completionData" />
      </div>
      <div class="chart-card">
        <h3>By Category</h3>
        <StatisticsChart v-if="catDistData" type="doughnut" :data="catDistData" />
      </div>
      <div class="chart-card">
        <h3>By Priority</h3>
        <StatisticsChart v-if="priorityData" type="bar" :data="priorityData" />
      </div>
    </div>

    <!-- Overdue tasks -->
    <div v-if="overdue.length" class="section">
      <h3>Overdue Tasks</h3>
      <table class="overdue-table">
        <thead>
          <tr><th>Task</th><th>Due Date</th><th>Priority</th><th>Overdue Days</th></tr>
        </thead>
        <tbody>
          <tr v-for="o in overdue" :key="o.schedule_id">
            <td>
              <router-link :to="`/schedules/${o.schedule_id}`">{{ o.title }}</router-link>
            </td>
            <td>{{ o.due_date ? new Date(o.due_date).toLocaleDateString('zh-CN') : '-' }}</td>
            <td><PriorityBadge :priority="o.priority" /></td>
            <td class="overdue-days">{{ o.overdue_days }} days</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../utils/api.js'
import StatisticsChart from '../components/StatisticsChart.vue'
import PriorityBadge from '../components/PriorityBadge.vue'

const overviewData = ref(null)
const completionData = ref(null)
const catDistData = ref(null)
const priorityData = ref(null)
const overdue = ref([])

const statusColors = { todo: '#64748b', in_progress: '#3b82f6', done: '#22c55e', cancelled: '#71717a' }

onMounted(async () => {
  const overview = await api.getOverview()
  overviewData.value = {
    labels: ['Todo', 'In Progress', 'Done', 'Cancelled'],
    datasets: [{
      data: [overview.todo, overview.in_progress, overview.done, overview.cancelled],
      backgroundColor: ['#64748b', '#3b82f6', '#22c55e', '#71717a'],
    }],
  }

  const comp = await api.getCompletion(30)
  completionData.value = {
    labels: comp.map(c => c.day),
    datasets: [
      { label: 'Total', data: comp.map(c => c.total), backgroundColor: '#3b82f6' },
      { label: 'Completed', data: comp.map(c => c.completed), backgroundColor: '#22c55e' },
    ],
  }

  const catDist = await api.getCategoryDist()
  catDistData.value = {
    labels: catDist.map(c => c.name),
    datasets: [{
      data: catDist.map(c => c.count),
      backgroundColor: catDist.map(c => c.color),
    }],
  }

  const priDist = await api.getPriorityDist()
  const priColors = { low: '#22c55e', medium: '#eab308', high: '#f97316', urgent: '#ef4444' }
  priorityData.value = {
    labels: Object.keys(priDist),
    datasets: [{
      label: 'Count',
      data: Object.values(priDist),
      backgroundColor: Object.keys(priDist).map(k => priColors[k] || '#94a3b8'),
    }],
  }

  overdue.value = await api.getOverdue()
})
</script>

<style scoped>
.stats-page { max-width: 1100px; }
h2 { font-size: 24px; color: #f1f5f9; margin-bottom: 24px; }
.chart-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 32px; }
.chart-card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; }
.chart-card h3 { font-size: 14px; color: #94a3b8; margin-bottom: 16px; }

.section { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; }
.section h3 { font-size: 14px; color: #94a3b8; margin-bottom: 14px; }
.overdue-table { width: 100%; border-collapse: collapse; }
.overdue-table th { text-align: left; padding: 8px 12px; font-size: 12px; color: #64748b; text-transform: uppercase; border-bottom: 1px solid #334155; }
.overdue-table td { padding: 10px 12px; font-size: 13px; color: #cbd5e1; border-bottom: 1px solid #1e293b; }
.overdue-days { color: #f87171; font-weight: 600; }
</style>
