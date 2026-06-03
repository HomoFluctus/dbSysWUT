<template>
  <div class="form-page" v-loading="loading">
    <div class="form-head">
      <h2>&#x1f4dd; {{ isEdit ? '编辑日程' : '新建日程' }}</h2>
      <TemplatePicker v-if="!isEdit" ref="templatePickerRef" @apply="onTemplateApply" />
    </div>

    <el-form :model="form" label-position="top" class="schedule-form">
      <el-form-item label="标题" required>
        <el-input v-model="form.title" placeholder="日程标题" />
      </el-form-item>

      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="日程描述" />
      </el-form-item>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="优先级">
            <el-select v-model="form.priority">
              <el-option label="低" value="low" />
              <el-option label="中" value="medium" />
              <el-option label="高" value="high" />
              <el-option label="紧急" value="urgent" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="状态">
            <el-select v-model="form.status">
              <el-option label="待办" value="todo" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已完成" value="done" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="到期时间">
            <el-date-picker
              v-model="form.due_date"
              type="datetime"
              placeholder="选择日期时间"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DDTHH:mm"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="预计时间（分钟）">
            <el-input-number v-model="form.estimated_minutes" :min="0" placeholder="分钟" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="分类">
            <el-select v-model="form.category_id" placeholder="选择分类" clearable>
              <el-option v-for="c in catStore.categories" :key="c.category_id" :label="c.name" :value="c.category_id" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="标签">
            <el-checkbox-group v-model="form.tag_ids">
              <el-checkbox v-for="t in tagStore.tags" :key="t.tag_id" :value="t.tag_id" :label="t.tag_id">
                <el-tag :color="t.color" effect="dark" size="small">{{ t.name }}</el-tag>
              </el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-col>
      </el-row>

      <!-- Recurring -->
      <el-divider />
      <el-form-item>
        <el-checkbox v-model="enableRecurring" label="周期日程" />
      </el-form-item>
      <el-row :gutter="12" v-if="enableRecurring">
        <el-col :span="6">
          <el-form-item label="频率">
            <el-select v-model="recurring.freq">
              <el-option label="每天" value="daily" />
              <el-option label="每周" value="weekly" />
              <el-option label="每月" value="monthly" />
              <el-option label="每年" value="yearly" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="间隔">
            <el-input-number v-model="recurring.interval" :min="1" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="开始日期">
            <el-date-picker v-model="recurring.start_date" type="date" value-format="YYYY-MM-DD" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="结束日期">
            <el-date-picker v-model="recurring.end_date" type="date" value-format="YYYY-MM-DD" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item v-if="enableRecurring && recurring.freq === 'weekly'" label="重复星期">
        <el-checkbox-group v-model="recurringWeekdays">
          <el-checkbox :label="0">周一</el-checkbox>
          <el-checkbox :label="1">周二</el-checkbox>
          <el-checkbox :label="2">周三</el-checkbox>
          <el-checkbox :label="3">周四</el-checkbox>
          <el-checkbox :label="4">周五</el-checkbox>
          <el-checkbox :label="5">周六</el-checkbox>
          <el-checkbox :label="6">周日</el-checkbox>
        </el-checkbox-group>
      </el-form-item>

      <!-- Reminders -->
      <el-divider />
      <el-form-item label="提醒">
        <div class="reminder-presets">
          <el-button size="small" @click="addReminder(15)">提前 15 分钟</el-button>
          <el-button size="small" @click="addReminder(60)">提前 1 小时</el-button>
          <el-button size="small" @click="addReminder(1440)">提前 1 天</el-button>
        </div>
        <div v-for="(r, i) in reminders" :key="i" class="reminder-row">
          <el-date-picker
            v-model="r.remind_at"
            type="datetime"
            placeholder="提醒时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DDTHH:mm"
          />
          <el-button type="danger" :icon="Delete" circle size="small" @click="reminders.splice(i, 1)" />
        </div>
      </el-form-item>

      <div class="form-actions">
        <el-button type="primary" :loading="saving" @click="handleSubmit" size="large">保存</el-button>
        <el-button @click="$router.back()" size="large">取消</el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useScheduleStore } from '../stores/schedules.js'
import { useCategoryStore } from '../stores/categories.js'
import { useTagStore } from '../stores/tags.js'
import { api } from '../utils/api.js'
import { ElMessage } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import TemplatePicker from '../components/TemplatePicker.vue'

const route = useRoute()
const router = useRouter()
const store = useScheduleStore()
const catStore = useCategoryStore()
const tagStore = useTagStore()

const isEdit = ref(!!route.params.id)
const saving = ref(false)
const templatePickerRef = ref(null)

function onTemplateApply(data) {
  Object.assign(form.value, data)
}
const loading = ref(false)

const form = ref({
  title: '', description: '', priority: 'medium', status: 'todo',
  due_date: '', estimated_minutes: null, category_id: null, tag_ids: [],
})

const enableRecurring = ref(false)
const recurring = ref({ freq: 'daily', interval: 1, start_date: '', end_date: '' })
const recurringWeekdays = ref([])
const reminders = ref([])

function addReminder(minutes) {
  if (!form.value.due_date) {
    ElMessage.warning('请先设置到期时间')
    return
  }
  const due = new Date(form.value.due_date)
  due.setMinutes(due.getMinutes() - minutes)
  const str = due.toISOString().slice(0, 16)
  reminders.value.push({ remind_at: str, method: 'push' })
}

onMounted(async () => {
  await catStore.fetchCategories()
  await tagStore.fetchTags()

  if (isEdit.value) {
    loading.value = true
    try {
      const s = await store.fetchSchedule(route.params.id)
      form.value = {
        title: s.title, description: s.description || '', priority: s.priority,
        status: s.status, due_date: s.due_date ? s.due_date.slice(0, 16) : '',
        estimated_minutes: s.estimated_minutes, category_id: s.category_id,
        tag_ids: s.tags?.map(t => t.tag_id) || [],
      }
      if (s.recurring) {
        enableRecurring.value = true
        recurring.value = {
          freq: s.recurring.freq, interval: s.recurring.interval,
          start_date: s.recurring.start_date, end_date: s.recurring.end_date || '',
        }
        if (s.recurring.weekdays) {
          recurringWeekdays.value = s.recurring.weekdays.split(',').map(Number)
        }
      }
      if (s.reminders?.length) {
        reminders.value = s.reminders.map(r => ({
          remind_at: r.remind_at.slice(0, 16), method: r.method, _id: r.reminder_id,
        }))
      }
    } finally {
      loading.value = false
    }
  }
})

async function handleSubmit() {
  saving.value = true
  try {
    const data = { ...form.value }
    if (!data.due_date) data.due_date = null
    if (!data.description) data.description = null
    if (data.estimated_minutes === '' || data.estimated_minutes === null) data.estimated_minutes = null

    let schedule
    if (isEdit.value) {
      schedule = await store.updateSchedule(route.params.id, data)
      const recurringPayload = { ...recurring.value, end_date: recurring.value.end_date || null }
      if (recurring.value.freq === 'weekly' && recurringWeekdays.value.length > 0) {
        recurringPayload.weekdays = recurringWeekdays.value.sort().join(',')
      }
      if (enableRecurring.value) {
        await api.upsertRecurring(schedule.schedule_id, recurringPayload)
      } else {
        await api.deleteRecurring(schedule.schedule_id).catch(() => {})
      }
    } else {
      schedule = await store.createSchedule(data)
      const recurringPayload = { ...recurring.value, end_date: recurring.value.end_date || null }
      if (recurring.value.freq === 'weekly' && recurringWeekdays.value.length > 0) {
        recurringPayload.weekdays = recurringWeekdays.value.sort().join(',')
      }
      if (enableRecurring.value) {
        await api.upsertRecurring(schedule.schedule_id, recurringPayload)
      }
      for (const r of reminders.value) {
        if (r.remind_at) {
          await api.createReminder(schedule.schedule_id, { remind_at: r.remind_at + ':00', method: r.method })
        }
      }
    }

    ElMessage.success(isEdit.value ? '日程已更新' : '日程已创建')
    router.push(`/schedules/${schedule.schedule_id}`)
  } catch (e) {
    ElMessage.error(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.form-page { max-width: 700px; }
.form-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.form-head h2 { font-size: 24px; color: var(--text-primary); margin-bottom: 0; }
.schedule-form .el-select { width: 100%; }
.schedule-form .el-date-editor { width: 100%; }
.reminder-presets { display: flex; gap: 8px; margin-bottom: 12px; }
.reminder-row { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
.reminder-row .el-date-editor { flex: 1; }
.form-actions { display: flex; gap: 12px; margin-top: 28px; }
</style>
