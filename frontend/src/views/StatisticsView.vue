<template>
  <div class="stats-page" v-loading="loading">
    <h2>&#x1f4ca; 统计分析</h2>

    <!-- Overview row -->
    <el-row :gutter="16" class="overview-row" v-if="overview">
      <el-col :span="6">
        <el-statistic title="总日程" :value="overview.total" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="已完成" :value="overview.done" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="逾期" :value="overview.overdue">
          <template #suffix><span style="color:#f87171;font-size:14px">项</span></template>
        </el-statistic>
      </el-col>
      <el-col :span="6">
        <el-statistic title="完成率" :value="completionRate" suffix="%" :precision="1" />
      </el-col>
    </el-row>

    <ActivityHeatmap />

    <el-row :gutter="16" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>状态概览</span></template>
          <StatisticsChart v-if="overviewData" type="doughnut" :data="overviewData" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <span>完成趋势</span>
            <el-select v-model="completionDays" size="small" style="width:100px;float:right" @change="loadCompletion">
              <el-option label="7 天" :value="7" />
              <el-option label="30 天" :value="30" />
              <el-option label="90 天" :value="90" />
            </el-select>
          </template>
          <StatisticsChart v-if="completionData" type="bar" :data="completionData" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>分类分布</span></template>
          <StatisticsChart v-if="catDistData" type="doughnut" :data="catDistData" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header><span>优先级分布</span></template>
          <StatisticsChart v-if="priorityData" type="bar" :data="priorityData" />
        </el-card>
      </el-col>
    </el-row>

    <!-- Overdue table -->
    <el-card shadow="never" class="overdue-card" v-if="overdue.length">
      <template #header><span>逾期日程</span></template>
      <el-table :data="overdue" style="width:100%" @row-click="(row) => $router.push(`/schedules/${row.schedule_id}`)">
        <el-table-column prop="title" label="日程" />
        <el-table-column label="到期日" width="120">
          <template #default="{ row }">
            {{ row.due_date ? new Date(row.due_date).toLocaleDateString('zh-CN') : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="优先级" width="80">
          <template #default="{ row }"><PriorityBadge :priority="row.priority" /></template>
        </el-table-column>
        <el-table-column prop="overdue_days" label="逾期天数" width="100">
          <template #default="{ row }">
            <span class="overdue-days">{{ row.overdue_days }} 天</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { api } from '../utils/api.js'
import StatisticsChart from '../components/StatisticsChart.vue'
import ActivityHeatmap from '../components/ActivityHeatmap.vue'
import PriorityBadge from '../components/PriorityBadge.vue'

const loading = ref(true)
const overview = ref(null)
const overviewData = ref(null)
const completionData = ref(null)
const completionDays = ref(30)
const catDistData = ref(null)
const priorityData = ref(null)
const overdue = ref([])

const completionRate = computed(() => {
  if (!overview.value || overview.value.total === 0) return 0
  return (overview.value.done / overview.value.total) * 100
})

async function loadCompletion() {
  const comp = await api.getCompletion(completionDays.value)
  completionData.value = {
    labels: comp.map(c => c.day),
    datasets: [
      { label: '总数', data: comp.map(c => c.total), backgroundColor: '#3b82f6' },
      { label: '已完成', data: comp.map(c => c.completed), backgroundColor: '#22c55e' },
    ],
  }
}

onMounted(async () => {
  try {
    overview.value = await api.getOverview()
    overviewData.value = {
      labels: ['待办', '进行中', '已完成', '已取消'],
      datasets: [{
        data: [overview.value.todo, overview.value.in_progress, overview.value.done, overview.value.cancelled],
        backgroundColor: ['#64748b', '#3b82f6', '#22c55e', '#71717a'],
      }],
    }

    await loadCompletion()

    const catDist = await api.getCategoryDist()
    catDistData.value = {
      labels: catDist.map(c => c.name),
      datasets: [{ data: catDist.map(c => c.count), backgroundColor: catDist.map(c => c.color) }],
    }

    const priDist = await api.getPriorityDist()
    const priColors = { low: '#22c55e', medium: '#eab308', high: '#f97316', urgent: '#ef4444' }
    priorityData.value = {
      labels: Object.keys(priDist),
      datasets: [{
        label: '数量',
        data: Object.values(priDist),
        backgroundColor: Object.keys(priDist).map(k => priColors[k] || '#94a3b8'),
      }],
    }

    overdue.value = await api.getOverdue()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.stats-page { max-width: 1100px; }
.stats-page h2 { font-size: 24px; color: var(--text-primary); margin-bottom: 24px; }
.overview-row { margin-bottom: 20px; }
.chart-row { margin-bottom: 20px; }
.overdue-card { margin-top: 20px; }
.overdue-days { color: #f87171; font-weight: 600; }
</style>
