export function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

export function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN')
}

export function isOverdue(dateStr, status) {
  if (!dateStr || status === 'done' || status === 'cancelled') return false
  return new Date(dateStr) < new Date()
}

export function getPriorityLabel(p) {
  const map = { low: '低', medium: '中', high: '高', urgent: '紧急' }
  return map[p] || p
}

export function getPriorityColor(p) {
  const map = { low: '#22c55e', medium: '#eab308', high: '#f97316', urgent: '#ef4444' }
  return map[p] || '#94a3b8'
}

export function getStatusLabel(s) {
  const map = { todo: '待办', in_progress: '进行中', done: '已完成', cancelled: '已取消' }
  return map[s] || s
}
