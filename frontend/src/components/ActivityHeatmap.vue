<template>
  <div class="heatmap-wrap">
    <div class="heatmap-header">
      <h4><span class="header-emoji">&#x1f4c5;</span> 活动热力图</h4>
      <span class="heatmap-sub">过去一年每天创建的日程数</span>
    </div>
    <div v-if="loading" class="heatmap-loading">
      <div class="loading-spinner"></div>
    </div>
    <div v-else-if="error" class="heatmap-error">
      <span class="error-emoji">&#x1f62f;</span>
      <p>加载失败</p>
      <el-button size="small" @click="fetchData" plain>重试</el-button>
    </div>
    <div v-else class="heatmap-body">
      <div class="heatmap-grid">
        <div
          v-for="cell in cells"
          :key="cell.date"
          class="heatmap-cell"
          :class="'level-' + cell.level"
          :title="cell.date + ': ' + cell.count + ' 条日程'"
        >
          <div class="cell-tip" v-if="cell.count > 0">{{ cell.date.slice(5) }}: {{ cell.count }}条</div>
        </div>
      </div>
      <div class="heatmap-footer">
        <span class="total-badge">{{ totalCount }} 条日程</span>
        <div class="heatmap-legend">
          <span>少</span>
          <span class="legend-dot level-0"></span>
          <span class="legend-dot level-1"></span>
          <span class="legend-dot level-2"></span>
          <span class="legend-dot level-3"></span>
          <span class="legend-dot level-4"></span>
          <span>多</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../utils/api.js'

const loading = ref(true)
const error = ref(false)
const cells = ref([])
const totalCount = ref(0)

onMounted(fetchData)

async function fetchData() {
  loading.value = true
  error.value = false
  try {
    const data = await api.getActivityHeatmap()
    const result = buildCells(data)
    cells.value = result.cells
    totalCount.value = result.total
  } catch (e) {
    error.value = true
    console.error('Heatmap fetch failed:', e)
  } finally {
    loading.value = false
  }
}

function buildCells(data) {
  const result = []
  let total = 0
  const now = new Date()
  const start = new Date(now.getFullYear(), now.getMonth() - 11, 1)
  const d = new Date(start)
  while (d <= now) {
    const key = d.toISOString().slice(0, 10)
    const count = data[key] || 0
    total += count
    result.push({
      date: key,
      count,
      level: count === 0 ? 0 : count <= 1 ? 1 : count <= 2 ? 2 : count <= 4 ? 3 : 4,
    })
    d.setDate(d.getDate() + 1)
  }
  return { cells: result, total }
}
</script>

<style scoped>
.heatmap-wrap {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}
.heatmap-header { margin-bottom: 14px; }
.heatmap-header h4 {
  font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px;
  display: flex; align-items: center; gap: 6px;
}
.header-emoji { font-size: 18px; }
.heatmap-sub { font-size: 12px; color: var(--text-muted); }

.heatmap-body { position: relative; }
.heatmap-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
}
.heatmap-cell {
  width: 13px;
  height: 13px;
  border-radius: 2px;
  background: #e2e8f0;
  position: relative;
  cursor: default;
  transition: transform 0.1s ease;
}
html.dark .heatmap-cell { background: #0f172a; }
.heatmap-cell:hover { transform: scale(1.5); z-index: 2; }
.heatmap-cell:hover .cell-tip { display: block; }

.heatmap-cell.level-1 { background: #9be9a8; }
.heatmap-cell.level-2 { background: #40c463; }
.heatmap-cell.level-3 { background: #30a14e; }
.heatmap-cell.level-4 { background: #216e39; }
html.dark .heatmap-cell.level-1 { background: #0e4429; }
html.dark .heatmap-cell.level-2 { background: #006d32; }
html.dark .heatmap-cell.level-3 { background: #26a641; }
html.dark .heatmap-cell.level-4 { background: #39d353; }

.cell-tip {
  display: none;
  position: absolute;
  bottom: 120%;
  left: 50%;
  transform: translateX(-50%);
  background: #1e293b;
  color: #f1f5f9;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  z-index: 10;
  pointer-events: none;
}

.heatmap-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}
.total-badge {
  font-size: 12px;
  color: var(--text-muted);
  padding: 2px 10px;
  background: var(--bg-base);
  border-radius: 10px;
}
.heatmap-legend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-muted);
}
.legend-dot {
  width: 11px; height: 11px; border-radius: 2px;
}
.legend-dot.level-0 { background: #e2e8f0; }
html.dark .legend-dot.level-0 { background: #0f172a; }
.legend-dot.level-1 { background: #9be9a8; }
html.dark .legend-dot.level-1 { background: #0e4429; }
.legend-dot.level-2 { background: #40c463; }
html.dark .legend-dot.level-2 { background: #006d32; }
.legend-dot.level-3 { background: #30a14e; }
html.dark .legend-dot.level-3 { background: #26a641; }
.legend-dot.level-4 { background: #216e39; }
html.dark .legend-dot.level-4 { background: #39d353; }

.heatmap-loading {
  text-align: center; padding: 30px;
}
.loading-spinner {
  width: 24px; height: 24px;
  border: 2px solid var(--border-color);
  border-top-color: var(--el-color-primary);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin: 0 auto;
}
@keyframes spin { to { transform: rotate(360deg); } }

.heatmap-error {
  text-align: center;
  padding: 20px;
  color: var(--text-muted);
}
.error-emoji { font-size: 28px; display: block; margin-bottom: 6px; }
.heatmap-error p { font-size: 13px; margin-bottom: 8px; }
</style>
