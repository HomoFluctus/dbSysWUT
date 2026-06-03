const BASE = '/api'

async function request(url, options = {}) {
  const token = localStorage.getItem('access_token')
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${url}`, { ...options, headers })
  if (res.status === 401) {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    window.location.href = '/login'
    return
  }
  if (res.status === 204) return null
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Request failed')
  return data
}

export const api = {
  // Auth
  register: (body) => request('/auth/register', { method: 'POST', body: JSON.stringify(body) }),
  login: (body) => request('/auth/login', { method: 'POST', body: JSON.stringify(body) }),
  refresh: (body) => request('/auth/refresh', { method: 'POST', body: JSON.stringify(body) }),
  getMe: () => request('/auth/me'),

  // Schedules
  listSchedules: (params = {}) => {
    const q = new URLSearchParams(params).toString()
    return request(`/schedules${q ? '?' + q : ''}`)
  },
  getSchedule: (id) => request(`/schedules/${id}`),
  createSchedule: (body) => request('/schedules', { method: 'POST', body: JSON.stringify(body) }),
  updateSchedule: (id, body) => request(`/schedules/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
  deleteSchedule: (id) => request(`/schedules/${id}`, { method: 'DELETE' }),
  changeStatus: (id, status) => request(`/schedules/${id}/status`, { method: 'PATCH', body: JSON.stringify({ status }) }),

  // Categories
  listCategories: () => request('/categories'),
  createCategory: (body) => request('/categories', { method: 'POST', body: JSON.stringify(body) }),
  updateCategory: (id, body) => request(`/categories/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
  deleteCategory: (id) => request(`/categories/${id}`, { method: 'DELETE' }),

  // Tags
  listTags: () => request('/tags'),
  createTag: (body) => request('/tags', { method: 'POST', body: JSON.stringify(body) }),
  deleteTag: (id) => request(`/tags/${id}`, { method: 'DELETE' }),

  // Reminders
  listReminders: (scheduleId) => request(`/schedules/${scheduleId}/reminders`),
  createReminder: (scheduleId, body) => request(`/schedules/${scheduleId}/reminders`, { method: 'POST', body: JSON.stringify(body) }),
  updateReminder: (id, body) => request(`/reminders/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
  deleteReminder: (id) => request(`/reminders/${id}`, { method: 'DELETE' }),

  // Recurring
  getRecurring: (scheduleId) => request(`/schedules/${scheduleId}/recurring`),
  getRecurringDates: (scheduleId, limit = 20) => request(`/schedules/${scheduleId}/recurring/dates?limit=${limit}`),
  upsertRecurring: (scheduleId, body) => request(`/schedules/${scheduleId}/recurring`, { method: 'PUT', body: JSON.stringify(body) }),
  deleteRecurring: (scheduleId) => request(`/schedules/${scheduleId}/recurring`, { method: 'DELETE' }),

  // Calendar
  getMonthCalendar: (year, month) => request(`/calendar?year=${year}&month=${month}`),
  getWeekCalendar: (date) => request(`/calendar/week?date=${date}`),
  getDayCalendar: (date) => request(`/calendar/day?date=${date}`),

  // Statistics
  getOverview: () => request('/statistics/overview'),
  getCompletion: (days = 30) => request(`/statistics/completion?days=${days}`),
  getCategoryDist: () => request('/statistics/category-distribution'),
  getPriorityDist: () => request('/statistics/priority-distribution'),
  getOverdue: () => request('/statistics/overdue'),

  // Search
  search: (params = {}) => {
    const q = new URLSearchParams(params).toString()
    return request(`/search${q ? '?' + q : ''}`)
  },

  // Dependencies
  listDependencies: (scheduleId) => request(`/schedules/${scheduleId}/dependencies`),
  createDependency: (scheduleId, body) => request(`/schedules/${scheduleId}/dependencies`, { method: 'POST', body: JSON.stringify(body) }),
  deleteDependency: (scheduleId, depId) => request(`/schedules/${scheduleId}/dependencies/${depId}`, { method: 'DELETE' }),

  // Duplicate
  duplicateSchedule: (id) => request(`/schedules/${id}/duplicate`, { method: 'POST' }),

  // Batch operations
  batchUpdateStatus: (body) => request('/schedules/batch/status', { method: 'POST', body: JSON.stringify(body) }),
  batchDelete: (body) => request('/schedules/batch/delete', { method: 'POST', body: JSON.stringify(body) }),

  // Subtasks
  listSubtasks: (scheduleId) => request(`/schedules/${scheduleId}/subtasks`),
  createSubtask: (scheduleId, body) => request(`/schedules/${scheduleId}/subtasks`, { method: 'POST', body: JSON.stringify(body) }),
  updateSubtask: (scheduleId, subtaskId, body) => request(`/schedules/${scheduleId}/subtasks/${subtaskId}`, { method: 'PATCH', body: JSON.stringify(body) }),
  deleteSubtask: (scheduleId, subtaskId) => request(`/schedules/${scheduleId}/subtasks/${subtaskId}`, { method: 'DELETE' }),

  // Activity heatmap
  getActivityHeatmap: () => request('/statistics/activity-heatmap'),

  // Streaks & Review
  getStreaks: () => request('/statistics/streaks'),
  getReview: (period = 'day') => request(`/statistics/review?period=${period}`),

  // Time tracking
  logTime: (id, body) => request(`/schedules/${id}/log-time`, { method: 'PATCH', body: JSON.stringify(body) }),
  getTimeAccuracy: () => request('/statistics/time-accuracy'),

  // Activity log
  listActivityLogs: (params = {}) => {
    const q = new URLSearchParams(params).toString()
    return request(`/activity-log${q ? '?' + q : ''}`)
  },

  // Templates
  listTemplates: () => request('/templates'),
  createTemplate: (body) => request('/templates', { method: 'POST', body: JSON.stringify(body) }),
  deleteTemplate: (id) => request(`/templates/${id}`, { method: 'DELETE' }),
  applyTemplate: (id) => request(`/templates/${id}/apply`, { method: 'POST' }),

  // iCal
  getIcalToken: () => request('/ical/token'),

  // Sharing
  generateShareLink: (id) => request(`/schedules/${id}/share`, { method: 'POST' }),
  revokeShareLink: (id) => request(`/schedules/${id}/share`, { method: 'DELETE' }),
  getSharedSchedule: (token) => {
    // Public endpoint, no auth header
    return fetch(`${BASE}/schedules/share/${token}`).then(async (res) => {
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || 'Schedule not found')
      }
      return res.json()
    })
  },

  // Export
  async exportCsv() {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`${BASE}/schedules/export/csv`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('导出失败')
    const blob = await res.blob()
    downloadBlob(blob, 'schedules.csv')
  },
  async exportJson() {
    const token = localStorage.getItem('access_token')
    const res = await fetch(`${BASE}/schedules/export/json`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error('导出失败')
    const blob = await res.blob()
    downloadBlob(blob, 'schedules.json')
  },
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
