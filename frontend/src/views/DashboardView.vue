<template>
  <div class="dashboard">
    <div class="page-header">
      <h2>我的日程</h2>
      <el-button type="primary" @click="$router.push('/schedules/new')">
        <el-icon><Plus /></el-icon>
        新建日程
      </el-button>
    </div>

    <!-- Stats Row -->
    <el-row :gutter="16" class="stats-row" v-if="stats">
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
    <div class="filter-bar">
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
    <el-empty v-else-if="store.schedules.length === 0" description="暂无日程">
      <el-button type="primary" @click="$router.push('/schedules/new')">创建第一个日程</el-button>
    </el-empty>

    <!-- Schedule Grid -->
    <div v-else class="schedule-grid">
      <ScheduleCard v-for="s in store.schedules" :key="s.schedule_id" :schedule="s" />
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
import ScheduleCard from '../components/ScheduleCard.vue'
import { Plus, List, Check, Clock, WarningFilled, CircleCloseFilled, Loading } from '@element-plus/icons-vue'

const route = useRoute()
const store = useScheduleStore()
const catStore = useCategoryStore()
const stats = ref(null)

const statCards = [
  { key: 'total', label: '全部', icon: List, cls: 'total' },
  { key: 'todo', label: '待办', icon: Clock, cls: 'todo' },
  { key: 'in_progress', label: '进行中', icon: Loading, cls: 'progress' },
  { key: 'done', label: '已完成', icon: Check, cls: 'done' },
  { key: 'overdue', label: '已逾期', icon: WarningFilled, cls: 'overdue' },
]

async function load() {
  await catStore.fetchCategories()
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
</style>
