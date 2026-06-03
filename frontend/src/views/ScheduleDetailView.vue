<template>
  <div class="detail-page" v-loading="loading">
    <template v-if="schedule">
      <div class="detail-hero">
        <div>
          <div class="badge-row">
            <StatusBadge :status="schedule.status" />
            <PriorityBadge :priority="schedule.priority" />
          </div>
          <h2 class="detail-title">{{ schedule.title }}</h2>
        </div>
        <div class="hero-actions">
          <el-button-group>
            <el-button
              v-for="opt in statusOptions"
              :key="opt.value"
              :type="schedule.status === opt.value ? 'primary' : 'default'"
              size="small"
              @click="changeStatus(opt.value)"
            >{{ opt.label }}</el-button>
          </el-button-group>
          <router-link :to="`/schedules/${schedule.schedule_id}/edit`">
            <el-button type="primary" plain size="small">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
          </router-link>
          <el-button plain size="small" @click="handleDuplicate">
            <el-icon><CopyDocument /></el-icon>复制
          </el-button>
          <el-dropdown trigger="click">
            <el-button plain size="small">
              <el-icon><Download /></el-icon>导出
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="exportCSV">CSV 格式</el-dropdown-item>
                <el-dropdown-item @click="exportJSON">JSON 格式</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button plain size="small" @click="saveAsTemplate">
            <el-icon><Collection /></el-icon>存为模板
          </el-button>
          <el-button plain size="small" @click="openShareDialog">
            <el-icon><Share /></el-icon>分享
          </el-button>
          <el-popconfirm title="确定删除这个日程？" confirm-button-text="删除" @confirm="handleDelete">
            <template #reference>
              <el-button type="danger" plain size="small">
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </template>
          </el-popconfirm>
        </div>
      </div>

      <el-descriptions :column="2" border class="detail-meta">
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
        <el-descriptions-item label="创建时间">
          {{ new Date(schedule.created_at).toLocaleString('zh-CN') }}
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

      <div v-if="schedule.recurring" class="section">
        <h4>周期规则</h4>
        <el-tag type="info" effect="plain">
          {{ schedule.recurring.freq === 'daily' ? '每天' : schedule.recurring.freq === 'weekly' ? '每周' : schedule.recurring.freq === 'monthly' ? '每月' : '每年' }}
          ，间隔 {{ schedule.recurring.interval }} 次
        </el-tag>
        <div v-if="recurringDates.length > 0" style="margin-top: 12px;">
          <span style="font-size: 12px; color: var(--text-muted);">未来 {{ recurringDates.length }} 次：</span>
          <div class="recurring-date-list">
            <el-tag v-for="d in recurringDates" :key="d" size="small" effect="plain" round>{{ d }}</el-tag>
          </div>
        </div>
      </div>

      <div v-if="schedule.reminders?.length" class="section">
        <h4>提醒</h4>
        <el-timeline>
          <el-timeline-item
            v-for="r in schedule.reminders"
            :key="r.reminder_id"
            :timestamp="new Date(r.remind_at).toLocaleString('zh-CN')"
            :type="r.sent ? 'success' : 'primary'"
          >
            {{ r.sent ? '已发送' : '待发送' }}
          </el-timeline-item>
        </el-timeline>
      </div>

      <!-- Subtasks -->
      <div class="section">
        <div class="section-header">
          <h4>子任务</h4>
          <div class="subtask-add-row">
            <el-input
              v-model="newSubtaskTitle"
              placeholder="添加子任务..."
              size="small"
              @keyup.enter="addSubtask"
              style="width: 200px"
            />
            <el-button size="small" @click="addSubtask" :disabled="!newSubtaskTitle.trim()">
              <el-icon><Plus /></el-icon>
            </el-button>
          </div>
        </div>
        <el-empty v-if="subtasks.length === 0" description="暂无子任务" :image-size="60" />
        <div v-else class="subtask-list">
          <div
            v-for="st in subtasks"
            :key="st.subtask_id"
            class="subtask-item"
            :class="{ completed: st.completed }"
          >
            <el-checkbox
              :model-value="st.completed"
              @change="toggleSubtask(st)"
              :disabled="subtaskLoading"
            />
            <span class="subtask-title">{{ st.title }}</span>
            <el-button type="danger" link size="small" @click="removeSubtask(st.subtask_id)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
        <div v-if="subtasks.length > 0" class="subtask-summary">
          已完成 {{ subtasks.filter(s => s.completed).length }} / {{ subtasks.length }}
        </div>
      </div>

      <!-- Time tracking -->
      <div class="section">
        <h4>时间追踪</h4>
        <div class="time-track-row">
          <el-input-number v-model="logMinutes" :min="1" :max="480" size="small" style="width: 120px" placeholder="分钟" />
          <el-button size="small" type="primary" @click="logTime('add')" :disabled="!logMinutes">追加耗时</el-button>
          <el-button size="small" @click="logTime('set')" :disabled="!logMinutes">设为</el-button>
        </div>
        <div v-if="schedule.estimated_minutes && schedule.actual_minutes" class="time-bar-wrap">
          <div class="time-bar">
            <div class="time-bar-fill" :style="{ width: timeBarWidth + '%' }" :class="timeBarClass"></div>
          </div>
          <span class="time-bar-label">实际 {{ schedule.actual_minutes }} / 预估 {{ schedule.estimated_minutes }} 分钟</span>
        </div>
      </div>

      <!-- Pomodoro Timer -->
      <PomodoroTimer />

      <!-- Dependencies -->
      <div class="section">
        <div class="section-header">
          <h4>依赖关系</h4>
          <el-button size="small" @click="showDepDialog = true">
            <el-icon><Plus /></el-icon>添加依赖
          </el-button>
        </div>
        <el-empty v-if="deps.length === 0" description="暂无依赖" :image-size="60" />
        <div v-else class="dep-list">
          <div v-for="d in deps" :key="d.dependency_id" class="dep-item">
            <el-icon><Link /></el-icon>
            <span class="dep-type">{{ d.dep_type === 'blocks' ? '阻塞' : d.dep_type }}</span>
            <span class="dep-id">日程 #{{ d.depends_on_id }}</span>
            <el-button type="danger" link size="small" @click="removeDep(d.dependency_id)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </template>

    <!-- Add dependency dialog -->
    <el-dialog v-model="showDepDialog" title="添加依赖" width="420px">
      <el-form @submit.prevent="addDep">
        <el-form-item label="依赖的日程 ID">
          <el-input-number v-model="depForm.depends_on_id" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="依赖类型">
          <el-select v-model="depForm.dep_type" style="width: 100%">
            <el-option label="阻塞" value="blocks" />
            <el-option label="关联" value="related" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDepDialog = false">取消</el-button>
        <el-button type="primary" @click="addDep" :loading="depLoading">添加</el-button>
      </template>
    </el-dialog>

    <!-- Share dialog -->
    <el-dialog v-model="showShareDialog" title="分享日程" width="440px">
      <template v-if="shareToken">
        <p style="margin-bottom: 10px; font-size: 14px; color: var(--text-secondary);">任何人通过以下链接即可查看此日程：</p>
        <div class="share-link-row">
          <el-input :model-value="shareUrl" readonly size="default" />
          <el-button type="primary" size="default" @click="copyShareLink">{{ copyText }}</el-button>
        </div>
        <div style="margin-top: 16px;">
          <el-button type="danger" plain size="small" @click="revokeShare">撤销分享</el-button>
        </div>
      </template>
      <template v-else>
        <p style="font-size: 14px; color: var(--text-secondary);">生成一个公开链接，任何人打开后即可查看此日程。</p>
      </template>
      <template #footer>
        <el-button @click="showShareDialog = false">关闭</el-button>
        <el-button v-if="!shareToken" type="primary" @click="generateShare" :loading="shareLoading">生成链接</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useScheduleStore } from '../stores/schedules.js'
import { api } from '../utils/api.js'
import { ElMessage } from 'element-plus'
import PriorityBadge from '../components/PriorityBadge.vue'
import StatusBadge from '../components/StatusBadge.vue'
import TagBadge from '../components/TagBadge.vue'
import PomodoroTimer from '../components/PomodoroTimer.vue'
import { Edit, Delete, CopyDocument, Download, Plus, Link, Collection, Share } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const store = useScheduleStore()
const schedule = ref(null)
const loading = ref(true)

const deps = ref([])
const subtasks = ref([])
const recurringDates = ref([])
const newSubtaskTitle = ref('')
const subtaskLoading = ref(false)
const showDepDialog = ref(false)
const depLoading = ref(false)
const depForm = ref({ depends_on_id: null, dep_type: 'blocks' })

const logMinutes = ref(null)

const showShareDialog = ref(false)
const shareToken = ref('')
const shareLoading = ref(false)
const copyText = ref('复制链接')

const timeBarWidth = computed(() => {
  if (!schedule.value?.estimated_minutes || !schedule.value?.actual_minutes) return 0
  return Math.min((schedule.value.actual_minutes / schedule.value.estimated_minutes) * 100, 150)
})

const timeBarClass = computed(() => {
  const w = timeBarWidth.value
  if (w <= 80) return 'under'
  if (w <= 120) return 'good'
  return 'over'
})

async function logTime(mode) {
  if (!logMinutes.value) return
  try {
    schedule.value = await api.logTime(route.params.id, { minutes: logMinutes.value, mode })
    logMinutes.value = null
    ElMessage.success('时间已记录')
  } catch (e) {
    ElMessage.error(e.message)
  }
}

const shareUrl = computed(() => {
  return shareToken.value ? `${window.location.origin}/share/${shareToken.value}` : ''
})

async function openShareDialog() {
  showShareDialog.value = true
  // If schedule already has a share_token cached, use it
  if (schedule.value?.share_token) {
    shareToken.value = schedule.value.share_token
    return
  }
}

async function generateShare() {
  shareLoading.value = true
  try {
    const data = await api.generateShareLink(route.params.id)
    shareToken.value = data.share_token
    if (schedule.value) schedule.value.share_token = data.share_token
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    shareLoading.value = false
  }
}

async function copyShareLink() {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
    copyText.value = '已复制'
    setTimeout(() => { copyText.value = '复制链接' }, 2000)
  } catch {
    ElMessage.error('复制失败')
  }
}

async function revokeShare() {
  try {
    await api.revokeShareLink(route.params.id)
    shareToken.value = ''
    if (schedule.value) schedule.value.share_token = null
    ElMessage.success('分享链接已撤销')
  } catch (e) {
    ElMessage.error(e.message)
  }
}

const statusOptions = [
  { label: '待办', value: 'todo' },
  { label: '进行中', value: 'in_progress' },
  { label: '已完成', value: 'done' },
  { label: '已取消', value: 'cancelled' },
]

onMounted(async () => {
  try {
    schedule.value = await store.fetchSchedule(route.params.id)
    await loadDeps()
    await loadSubtasks()
    await loadRecurringDates()
  } finally {
    loading.value = false
  }
})

async function loadDeps() {
  try {
    deps.value = await api.listDependencies(route.params.id)
  } catch { deps.value = [] }
}

async function loadSubtasks() {
  try {
    subtasks.value = await api.listSubtasks(route.params.id)
  } catch { subtasks.value = [] }
}

async function loadRecurringDates() {
  if (!schedule.value?.recurring) return
  try {
    const data = await api.getRecurringDates(route.params.id)
    recurringDates.value = data.dates || []
  } catch { recurringDates.value = [] }
}

async function addSubtask() {
  const title = newSubtaskTitle.value.trim()
  if (!title) return
  subtaskLoading.value = true
  try {
    await api.createSubtask(route.params.id, { title })
    newSubtaskTitle.value = ''
    await loadSubtasks()
    ElMessage.success('子任务已添加')
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    subtaskLoading.value = false
  }
}

async function toggleSubtask(st) {
  subtaskLoading.value = true
  try {
    await api.updateSubtask(route.params.id, st.subtask_id, { completed: !st.completed })
    st.completed = !st.completed
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    subtaskLoading.value = false
  }
}

async function removeSubtask(id) {
  try {
    await api.deleteSubtask(route.params.id, id)
    subtasks.value = subtasks.value.filter(s => s.subtask_id !== id)
    ElMessage.success('子任务已删除')
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function changeStatus(status) {
  try {
    schedule.value = await store.changeStatus(route.params.id, status)
    ElMessage.success('状态已更新')
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function handleDelete() {
  try {
    await store.deleteSchedule(route.params.id)
    ElMessage.success('日程已删除')
    router.push('/')
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function handleDuplicate() {
  try {
    const dup = await api.duplicateSchedule(route.params.id)
    ElMessage.success('日程已复制')
    router.push(`/schedules/${dup.schedule_id}`)
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function addDep() {
  if (!depForm.value.depends_on_id) return
  depLoading.value = true
  try {
    await api.createDependency(route.params.id, {
      depends_on_id: depForm.value.depends_on_id,
      dep_type: depForm.value.dep_type,
    })
    ElMessage.success('依赖已添加')
    showDepDialog.value = false
    depForm.value = { depends_on_id: null, dep_type: 'blocks' }
    await loadDeps()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    depLoading.value = false
  }
}

async function removeDep(depId) {
  try {
    await api.deleteDependency(route.params.id, depId)
    ElMessage.success('依赖已移除')
    await loadDeps()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function saveAsTemplate() {
  try {
    await api.createTemplate({
      title: schedule.value.title,
      description: schedule.value.description,
      priority: schedule.value.priority,
      estimated_minutes: schedule.value.estimated_minutes,
      category_id: schedule.value.category_id,
      tag_ids: (schedule.value.tags || []).map(t => t.tag_id),
    })
    ElMessage.success('已保存为模板')
  } catch (e) {
    ElMessage.error(e.message)
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
</script>

<style scoped>
.detail-page { max-width: 750px; }
.detail-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}
.badge-row { display: flex; gap: 8px; margin-bottom: 10px; }
.detail-title { font-size: 26px; font-weight: 700; color: var(--text-primary); }
.hero-actions { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.detail-meta { margin-bottom: 24px; }
.section { margin-bottom: 24px; }
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.section h4 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.section-header h4 { margin-bottom: 0; }
.section p { font-size: 14px; color: var(--text-secondary); line-height: 1.7; }
.tag-row { display: flex; gap: 6px; flex-wrap: wrap; }

.dep-list { display: flex; flex-direction: column; gap: 8px; }
.dep-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
}
.dep-type {
  font-size: 12px;
  padding: 1px 8px;
  border-radius: 4px;
  background: rgba(99,102,241,0.15);
  color: #a5b4fc;
}
.dep-id { color: var(--text-secondary); flex: 1; }

.subtask-add-row { display: flex; gap: 6px; }
.subtask-list { display: flex; flex-direction: column; gap: 6px; margin-bottom: 8px; }
.subtask-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
}
.subtask-item.completed .subtask-title {
  text-decoration: line-through;
  color: var(--text-muted);
}
.subtask-title { flex: 1; color: var(--text-secondary); }
.subtask-summary { font-size: 12px; color: var(--text-muted); }
.recurring-date-list { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.muted-text { color: var(--text-muted); font-size: 13px; }
.time-track-row { display: flex; gap: 8px; align-items: center; }
.time-bar-wrap { margin-top: 12px; }
.time-bar { height: 8px; background: var(--el-fill-color); border-radius: 4px; overflow: hidden; margin-bottom: 4px; }
.time-bar-fill { height: 100%; border-radius: 4px; transition: width 0.3s ease; }
.time-bar-fill.under { background: #22c55e; }
.time-bar-fill.good { background: #eab308; }
.time-bar-fill.over { background: #ef4444; }
.time-bar-label { font-size: 11px; color: var(--text-muted); }
.share-link-row { display: flex; gap: 8px; }
.share-link-row .el-input { flex: 1; }
</style>
