<template>
  <div class="shared-page">
    <div class="shared-card" v-loading="loading">
      <template v-if="error">
        <el-result icon="error" title="无法访问" :sub-title="error">
          <template #extra>
            <el-button type="primary" @click="$router.push('/login')">返回登录</el-button>
          </template>
        </el-result>
      </template>

      <template v-else-if="schedule">
        <div class="shared-header">
          <div class="badge-row">
            <StatusBadge :status="schedule.status" />
            <PriorityBadge :priority="schedule.priority" />
          </div>
          <h2 class="shared-title">{{ schedule.title }}</h2>
          <p class="shared-owner" v-if="schedule.user_id">分享自用户 #{{ schedule.user_id }}</p>
        </div>

        <el-descriptions :column="2" border class="shared-meta">
          <el-descriptions-item label="到期时间">
            {{ schedule.due_date ? new Date(schedule.due_date).toLocaleString('zh-CN') : '未设置' }}
          </el-descriptions-item>
          <el-descriptions-item label="预计耗时">
            {{ schedule.estimated_minutes ? schedule.estimated_minutes + ' 分钟' : '未设置' }}
          </el-descriptions-item>
          <el-descriptions-item label="实际耗时">
            <span v-if="schedule.actual_minutes">{{ schedule.actual_minutes }} 分钟</span>
            <span v-else class="muted-text">未记录</span>
          </el-descriptions-item>
          <el-descriptions-item label="分类">
            <el-tag :color="schedule.category?.color" effect="dark" size="small" v-if="schedule.category">
              {{ schedule.category.name }}
            </el-tag>
            <span v-else>无</span>
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="schedule.description" class="section">
          <h4>描述</h4>
          <p>{{ schedule.description }}</p>
        </div>

        <div v-if="schedule.tags?.length" class="section">
          <h4>标签</h4>
          <div class="tag-row">
            <TagBadge v-for="t in schedule.tags" :key="t.tag_id" :tag="t" />
          </div>
        </div>

        <div v-if="schedule.subtasks?.length" class="section">
          <h4>子任务 ({{ schedule.subtasks.filter(s => s.completed).length }}/{{ schedule.subtasks.length }})</h4>
          <div class="subtask-list">
            <div
              v-for="st in schedule.subtasks"
              :key="st.subtask_id"
              class="subtask-item"
              :class="{ completed: st.completed }"
            >
              <el-icon v-if="st.completed" color="#22c55e"><CircleCheck /></el-icon>
              <el-icon v-else color="var(--text-muted)"><CircleCheck /></el-icon>
              <span class="subtask-title">{{ st.title }}</span>
            </div>
          </div>
        </div>

        <div class="shared-footer">
          <el-button @click="$router.push('/login')">登录以管理日程</el-button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../utils/api.js'
import PriorityBadge from '../components/PriorityBadge.vue'
import StatusBadge from '../components/StatusBadge.vue'
import TagBadge from '../components/TagBadge.vue'
import { CircleCheck } from '@element-plus/icons-vue'

const route = useRoute()
const schedule = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    schedule.value = await api.getSharedSchedule(route.params.token)
  } catch (e) {
    error.value = e.message || '分享链接无效或日程不存在'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.shared-page {
  min-height: 100vh;
  background: var(--bg-page);
  display: flex;
  justify-content: center;
  padding: 40px 16px;
}
.shared-card {
  width: 100%;
  max-width: 700px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 40px;
}
.shared-header { margin-bottom: 24px; }
.badge-row { display: flex; gap: 8px; margin-bottom: 10px; }
.shared-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
}
.shared-owner {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 6px;
}
.shared-meta { margin-bottom: 24px; }
.section { margin-bottom: 24px; }
.section h4 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.section p { font-size: 14px; color: var(--text-secondary); line-height: 1.7; }
.tag-row { display: flex; gap: 6px; flex-wrap: wrap; }
.muted-text { color: var(--text-muted); font-size: 13px; }
.subtask-list { display: flex; flex-direction: column; gap: 6px; }
.subtask-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}
.subtask-item.completed .subtask-title {
  text-decoration: line-through;
  color: var(--text-muted);
}
.subtask-title { color: var(--text-secondary); }
.shared-footer {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
  text-align: center;
}
</style>
