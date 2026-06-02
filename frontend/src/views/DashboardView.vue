<template>
  <div class="dashboard">
    <div class="header">
      <h2>Dashboard</h2>
      <router-link to="/schedules/new" class="btn-primary">+ New Task</router-link>
    </div>

    <!-- Overview stats -->
    <div v-if="stats" class="stats-grid">
      <div class="stat-card"><span class="stat-num">{{ stats.total }}</span><span class="stat-label">Total</span></div>
      <div class="stat-card todo"><span class="stat-num">{{ stats.todo }}</span><span class="stat-label">Todo</span></div>
      <div class="stat-card progress"><span class="stat-num">{{ stats.in_progress }}</span><span class="stat-label">In Progress</span></div>
      <div class="stat-card done"><span class="stat-num">{{ stats.done }}</span><span class="stat-label">Done</span></div>
      <div class="stat-card overdue"><span class="stat-num">{{ stats.overdue }}</span><span class="stat-label">Overdue</span></div>
    </div>

    <!-- Filters -->
    <FilterPanel :filters="store.filters" :categories="catStore.categories" @update:filters="onFilter" />

    <!-- Schedule list -->
    <div v-if="store.loading" class="loading">Loading...</div>
    <div v-else-if="store.schedules.length === 0" class="empty">No schedules found</div>
    <div v-else class="schedule-grid">
      <ScheduleCard v-for="s in store.schedules" :key="s.schedule_id" :schedule="s" />
    </div>

    <!-- Pagination -->
    <div v-if="store.total > store.pagination.per_page" class="pagination">
      <button :disabled="store.pagination.page <= 1" @click="changePage(store.pagination.page - 1)">Prev</button>
      <span>Page {{ store.pagination.page }} / {{ Math.ceil(store.total / store.pagination.per_page) }}</span>
      <button :disabled="store.pagination.page >= Math.ceil(store.total / store.pagination.per_page)" @click="changePage(store.pagination.page + 1)">Next</button>
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
import FilterPanel from '../components/FilterPanel.vue'

const route = useRoute()
const store = useScheduleStore()
const catStore = useCategoryStore()
const stats = ref(null)

async function load() {
  await catStore.fetchCategories()

  let params = { ...store.filters, page: store.pagination.page, per_page: store.pagination.per_page }
  // If search query in URL, use search endpoint
  if (route.query.q) {
    const data = await api.search({ q: route.query.q, ...params })
    store.schedules = data.items
    store.total = data.total
  } else {
    await store.fetchSchedules(params)
  }

  stats.value = await api.getOverview()
}

function onFilter(f) {
  Object.assign(store.filters, f)
  store.pagination.page = 1
  load()
}

function changePage(p) {
  store.pagination.page = p
  load()
}

watch(() => route.query.q, () => {
  store.pagination.page = 1
  load()
})

onMounted(load)
</script>

<style scoped>
.dashboard { max-width: 1100px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
h2 { font-size: 24px; font-weight: 700; color: #f1f5f9; }
.btn-primary {
  display: inline-block; padding: 10px 20px; background: #6366f1; color: #fff;
  border-radius: 8px; font-size: 14px; font-weight: 600;
}
.btn-primary:hover { background: #4f46e5; }

.stats-grid { display: flex; gap: 16px; margin-bottom: 24px; }
.stat-card {
  flex: 1; background: #1e293b; border: 1px solid #334155; border-radius: 12px;
  padding: 16px; text-align: center;
}
.stat-card.todo { border-color: #475569; }
.stat-card.progress { border-color: #1e3a5f; }
.stat-card.done { border-color: #14532d; }
.stat-card.overdue { border-color: #7f1d1d; }
.stat-num { display: block; font-size: 28px; font-weight: 700; color: #f1f5f9; }
.stat-label { font-size: 13px; color: #94a3b8; margin-top: 4px; }

.schedule-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }

.loading, .empty { text-align: center; padding: 60px 0; color: #64748b; font-size: 14px; }

.pagination { display: flex; align-items: center; justify-content: center; gap: 16px; margin-top: 24px; }
.pagination button {
  padding: 8px 16px; border-radius: 8px; border: 1px solid #334155;
  background: #1e293b; color: #e2e8f0; cursor: pointer; font-size: 13px;
}
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
.pagination span { font-size: 13px; color: #94a3b8; }
</style>
