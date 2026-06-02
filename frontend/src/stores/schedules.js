import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { api } from '../utils/api.js'

export const useScheduleStore = defineStore('schedules', () => {
  const schedules = ref([])
  const current = ref(null)
  const total = ref(0)
  const loading = ref(false)
  const filters = reactive({ status: '', priority: '', category_id: '', tag_ids: '' })
  const pagination = reactive({ page: 1, per_page: 20 })

  async function fetchSchedules(params = {}) {
    loading.value = true
    try {
      const query = { ...filters, ...pagination, ...params }
      Object.keys(query).forEach(k => { if (!query[k]) delete query[k] })
      const data = await api.listSchedules(query)
      schedules.value = data.items || []
      total.value = data.total || 0
      pagination.page = data.page || 1
    } catch (e) {
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  async function fetchSchedule(id) {
    current.value = await api.getSchedule(id)
    return current.value
  }

  async function createSchedule(data) {
    return await api.createSchedule(data)
  }

  async function updateSchedule(id, data) {
    return await api.updateSchedule(id, data)
  }

  async function deleteSchedule(id) {
    await api.deleteSchedule(id)
  }

  async function changeStatus(id, status) {
    return await api.changeStatus(id, status)
  }

  return { schedules, current, total, loading, filters, pagination,
           fetchSchedules, fetchSchedule, createSchedule, updateSchedule,
           deleteSchedule, changeStatus }
})
