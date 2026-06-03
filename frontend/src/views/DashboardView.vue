<template>
  <div class="dashboard">
    <div class="page-header">
      <h2>&#x1f4cb; 我的日程</h2>
      <div class="header-actions">
        <el-button v-if="!batchMode" @click="batchMode = true" plain size="default">
          <el-icon><Select /></el-icon>
          批量操作
        </el-button>
        <template v-else>
          <el-button type="primary" size="default" @click="applyBatch">批量完成</el-button>
          <el-button type="danger" size="default" @click="handleBatchDelete">批量删除</el-button>
          <el-button size="default" @click="exitBatch">取消</el-button>
        </template>
        <el-dropdown trigger="click" v-if="!batchMode">
          <el-button plain size="default">
            <el-icon><Download /></el-icon>
            导出
            <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="exportCSV">CSV 格式</el-dropdown-item>
              <el-dropdown-item @click="exportJSON">JSON 格式</el-dropdown-item>
              <el-dropdown-item divided @click="copyIcalLink">iCal 订阅链接</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="primary" @click="$router.push('/schedules/new')">
          <el-icon><Plus /></el-icon>
          新建日程
        </el-button>
      </div>
    </div>

    <!-- Batch bar -->
    <div v-if="batchMode && selectedIds.length > 0" class="batch-bar">
      <span class="batch-count">已选 <strong>{{ selectedIds.length }}</strong> 项</span>
      <el-select v-model="batchStatus" placeholder="目标状态" size="default" style="width: 160px">
        <el-option label="待办" value="todo" />
        <el-option label="进行中" value="in_progress" />
        <el-option label="已完成" value="done" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
      <el-button type="primary" @click="applyBatch">应用</el-button>
    </div>

    <!-- Heatmap -->
    <ActivityHeatmap v-if="!batchMode" />

    <!-- Streaks -->
    <StreakCard v-if="!batchMode" />

    <!-- Stats Row -->
    <el-row :gutter="16" class="stats-row" v-if="stats && !batchMode">
      <el-col :span="4" v-for="s in statCards" :key="s.key">
        <div class="stat-card" :class="s.cls" @click="onStatClick(s.status)">
          <div class="stat-icon">
            <el-icon :size="18"><component :is="s.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-num">{{ stats[s.key] }}</span>
            <span class="stat-label">{{ s.label }}</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Filters -->
    <div class="filter-bar" v-if="!batchMode">
      <el-select v-model="store.filters.status" placeholder="全部状态" clearable @change="onFilterChange" size="default">
        <el-option label="待办" value="todo" />
        <el-option label="进行中" value="in_progress" />
        <el-option label="已完成" value="done" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
      <el-select v-model="store.filters.priority" placeholder="全部优先级" clearable @change="onFilterChange" size="default">
        <el-option label="低" value="low" />
        <el-option label="中" value="medium" />
        <el-option label="高" value="high" />
        <el-option label="紧急" value="urgent" />
      </el-select>
      <el-select v-model="store.filters.category_id" placeholder="全部分类" clearable @change="onFilterChange" size="default">
        <el-option v-for="c in catStore.categories" :key="c.category_id" :label="c.name" :value="c.category_id" />
      </el-select>
    </div>

    <!-- Loading -->
    <el-skeleton v-if="store.loading" :rows="4" animated />

    <!-- Empty -->
    <el-empty v-else-if="store.schedules.length === 0" description="空空如也，今天要做什么呢？">
      <div class="empty-emoji">&#x2728;&#x1f4ad;&#x2728;</div>
      <el-button type="primary" @click="$router.push('/schedules/new')">&#x1f680; 创建第一个日程</el-button>
    </el-empty>

    <!-- Schedule Grid -->
    <div v-else class="schedule-grid">
      <ScheduleCard
        v-for="s in store.schedules"
        :key="s.schedule_id"
        :schedule="s"
        :batch-mode="batchMode"
        :model-value="selectedIds.includes(s.schedule_id)"
        @update:model-value="(val) => toggleSelect(s.schedule_id, val)"
        @refresh="load"
      />
    </div>

    <!-- Pagination -->
    <div v-if="store.total > store.pagination.per_page" class="pagination-wrap">
      <el-pagination
        :current-page="store.pagination.page"
        :page-size="store.pagination.per_page"
        :total="store.total"
        layout="prev, pager, next"
        @current-change="changePage"
        background
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useScheduleStore } from '../stores/schedules.js'
import { useCategoryStore } from '../stores/categories.js'
import { api } from '../utils/api.js'
import { ElMessage, ElMessageBox } from 'element-plus'
import ScheduleCard from '../components/ScheduleCard.vue'
import ActivityHeatmap from '../components/ActivityHeatmap.vue'
import StreakCard from '../components/StreakCard.vue'
import { Plus, List, Check, Clock, WarningFilled, Loading, Select, Download, ArrowDown } from '@element-plus/icons-vue'

const route = useRoute()
const store = useScheduleStore()
const catStore = useCategoryStore()
const stats = ref(null)

const batchMode = ref(false)
const selectedIds = ref([])
const batchStatus = ref('')

const statCards = [
  { key: 'total', label: '全部', icon: List, cls: 'total' },
  { key: 'todo', label: '待办', icon: Clock, cls: 'todo' },
  { key: 'in_progress', label: '进行中', icon: Loading, cls: 'progress' },
  { key: 'done', label: '已完成', icon: Check, cls: 'done' },
  { key: 'overdue', label: '已逾期', icon: WarningFilled, cls: 'overdue' },
]

async function load() {
  await catStore.fetchCategories()
  // Read filters from query params (set by category management click, etc.)
  if (route.query.category_id) store.filters.category_id = Number(route.query.category_id)
  let params = { ...store.filters, page: store.pagination.page, per_page: store.pagination.per_page }
  if (route.query.q) {
    const data = await api.search({ q: route.query.q, ...params })
    store.schedules = data.items
    store.total = data.total
  } else {
    await store.fetchSchedules(params)
  }
  stats.value = await api.getOverview()
}

function onFilterChange() {
  store.pagination.page = 1
  load()
}

function onStatClick(status) {
  if (status) {
    store.filters.status = status
    store.filters.priority = ''
    store.filters.category_id = ''
  } else {
    store.filters.status = ''
    store.filters.priority = ''
    store.filters.category_id = ''
  }
  store.pagination.page = 1
  load()
}

function changePage(p) {
  store.pagination.page = p
  load()
}

function toggleSelect(id, val) {
  if (val) {
    selectedIds.value.push(id)
  } else {
    selectedIds.value = selectedIds.value.filter(i => i !== id)
  }
}

function exitBatch() {
  batchMode.value = false
  selectedIds.value = []
  batchStatus.value = ''
}

async function applyBatch() {
  if (selectedIds.value.length === 0) return
  const status = batchStatus.value || 'done'
  try {
    await api.batchUpdateStatus({ schedule_ids: selectedIds.value, status })
    ElMessage.success(`已将 ${selectedIds.value.length} 项标记为${status === 'todo' ? '待办' : status === 'in_progress' ? '进行中' : status === 'done' ? '已完成' : '已取消'}`)
    exitBatch()
    load()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function handleBatchDelete() {
  if (selectedIds.value.length === 0) return
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 个日程？`, '批量删除', { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' })
    await api.batchDelete({ schedule_ids: selectedIds.value })
    ElMessage.success(`已删除 ${selectedIds.value.length} 项`)
    exitBatch()
    load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message)
  }
}

async function exportCSV() {
  try { await api.exportCsv(); ElMessage.success('CSV 导出成功') }
  catch (e) { ElMessage.error(e.message) }
}

async function exportJSON() {
  try { await api.exportJson(); ElMessage.success('JSON 导出成功') }
  catch (e) { ElMessage.error(e.message) }
}

async function copyIcalLink() {
  try {
    const { ical_token } = await api.getIcalToken()
    const url = `${window.location.origin}/api/ical/feed?token=${ical_token}`
    await navigator.clipboard.writeText(url)
    ElMessage.success('iCal 订阅链接已复制到剪贴板')
  } catch (e) {
    ElMessage.error(e.message)
  }
}

watch(() => route.query.q, () => { store.pagination.page = 1; load() })
onMounted(load)
</script>

<style scoped>
.dashboard { max-width: 1100px; }
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.page-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}
.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.batch-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 12px 16px;
  background: var(--bg-surface);
  border: 1px solid #6366f1;
  border-radius: 10px;
}
.batch-count {
  font-size: 14px;
  color: var(--text-secondary);
}

.stats-row { margin-bottom: 24px; }
.stat-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.stat-card.total:hover { border-color: #6366f1; }
.stat-card.todo:hover { border-color: #64748b; }
.stat-card.progress:hover { border-color: #3b82f6; }
.stat-card.done:hover { border-color: #22c55e; }
.stat-card.overdue:hover { border-color: #ef4444; }
.stat-icon {
  width: 38px; height: 38px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
}
.total .stat-icon { background: rgba(99,102,241,0.2); color: #818cf8; }
.todo .stat-icon { background: rgba(100,116,139,0.2); color: #94a3b8; }
.progress .stat-icon { background: rgba(59,130,246,0.2); color: #60a5fa; }
.done .stat-icon { background: rgba(34,197,94,0.2); color: #4ade80; }
.overdue .stat-icon { background: rgba(239,68,68,0.2); color: #f87171; }
.stat-num { display: block; font-size: 22px; font-weight: 700; color: var(--text-primary); line-height: 1.2; }
.stat-label { font-size: 12px; color: var(--text-muted); }

.filter-bar { display: flex; gap: 12px; margin-bottom: 20px; }
.filter-bar .el-select { width: 160px; }

.schedule-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 28px;
}
.empty-emoji { font-size: 32px; margin-bottom: 8px; }
</style>
