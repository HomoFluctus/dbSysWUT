<template>
  <div class="review-page" v-loading="loading">
    <div class="review-header">
      <h2>&#x1f4dd; 回顾</h2>
      <el-radio-group v-model="period" @change="load" size="default">
        <el-radio-button value="day">今日</el-radio-button>
        <el-radio-button value="week">本周</el-radio-button>
      </el-radio-group>
    </div>

    <el-row :gutter="16" class="review-grid">
      <el-col :span="8">
        <div class="review-section done">
          <div class="section-head">
            <span class="section-icon">&#x2705;</span>
            <span class="section-title">已完成</span>
            <el-tag size="small" round>{{ data.completed_count }}</el-tag>
          </div>
          <div class="section-list" v-if="data.completed.length">
            <div v-for="s in data.completed" :key="s.schedule_id" class="section-item"
                 @click="$router.push(`/schedules/${s.schedule_id}`)">
              <span class="item-title">{{ s.title }}</span>
              <span class="item-meta">{{ s.completed_at ? new Date(s.completed_at).toLocaleString('zh-CN') : '' }}</span>
            </div>
          </div>
          <el-empty v-else description="暂无" :image-size="40" />
        </div>
      </el-col>
      <el-col :span="8">
        <div class="review-section overdue">
          <div class="section-head">
            <span class="section-icon">&#x26a0;&#xfe0f;</span>
            <span class="section-title">已逾期</span>
            <el-tag size="small" type="danger" round>{{ data.overdue_count }}</el-tag>
          </div>
          <div class="section-list" v-if="data.overdue.length">
            <div v-for="s in data.overdue" :key="s.schedule_id" class="section-item"
                 @click="$router.push(`/schedules/${s.schedule_id}`)">
              <span class="item-title">{{ s.title }}</span>
              <PriorityBadge :priority="s.priority" />
            </div>
          </div>
          <el-empty v-else description="暂无逾期" :image-size="40" />
        </div>
      </el-col>
      <el-col :span="8">
        <div class="review-section upcoming">
          <div class="section-head">
            <span class="section-icon">&#x1f4c5;</span>
            <span class="section-title">即将到来</span>
            <el-tag size="small" type="primary" round>{{ data.upcoming_count }}</el-tag>
          </div>
          <div class="section-list" v-if="data.upcoming.length">
            <div v-for="s in data.upcoming" :key="s.schedule_id" class="section-item"
                 @click="$router.push(`/schedules/${s.schedule_id}`)">
              <span class="item-title">{{ s.title }}</span>
              <span class="item-meta">{{ s.due_date ? new Date(s.due_date).toLocaleString('zh-CN') : '-' }}</span>
            </div>
          </div>
          <el-empty v-else description="暂无" :image-size="40" />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { api } from '../utils/api.js'
import PriorityBadge from '../components/PriorityBadge.vue'

const loading = ref(true)
const period = ref('day')
const data = reactive({ completed: [], completed_count: 0, overdue: [], overdue_count: 0, upcoming: [], upcoming_count: 0 })

async function load() {
  loading.value = true
  try {
    const res = await api.getReview(period.value)
    Object.assign(data, res)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.review-page { max-width: 1100px; }
.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.review-header h2 { font-size: 24px; color: var(--text-primary); }

.review-grid { min-height: 400px; }
.review-section {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 18px;
  height: 100%;
}
.section-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}
.section-icon { font-size: 16px; }
.section-title { font-size: 15px; font-weight: 600; color: var(--text-primary); }

.section-list { display: flex; flex-direction: column; gap: 6px; }
.section-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: var(--bg-base);
  border-radius: 8px;
  cursor: pointer;
  transition: background var(--transition-fast);
}
.section-item:hover { background: var(--el-fill-color); }
.item-title { font-size: 13px; color: var(--text-primary); font-weight: 500; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.item-meta { font-size: 11px; color: var(--text-muted); flex-shrink: 0; margin-left: 8px; }
</style>
