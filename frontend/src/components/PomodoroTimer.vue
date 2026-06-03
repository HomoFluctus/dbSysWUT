<template>
  <div class="pomodoro-wrap">
    <div class="pomodoro-header" @click="expanded = !expanded">
      <span class="pomo-icon">&#x1f345;</span>
      <span class="pomo-label">番茄钟</span>
      <span class="pomo-toggle">{{ expanded ? '收起' : '展开' }}</span>
    </div>
    <div v-if="expanded" class="pomodoro-body">
      <svg class="pomo-ring" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="42" fill="none" stroke="var(--border-color)" stroke-width="6" />
        <circle
          cx="50" cy="50" r="42"
          fill="none"
          stroke="#ef4444"
          stroke-width="6"
          stroke-linecap="round"
          :stroke-dasharray="dashArray"
          :stroke-dashoffset="0"
          transform="rotate(-90 50 50)"
          style="transition: stroke-dasharray 1s linear"
        />
      </svg>
      <div class="pomo-time">{{ formatTime(timeLeft) }}</div>
      <div class="pomo-mode">{{ isBreak ? '休息' : '专注' }}</div>
      <div class="pomo-controls">
        <el-button v-if="!running" type="primary" size="small" @click="start">开始</el-button>
        <el-button v-else type="warning" size="small" @click="pause">暂停</el-button>
        <el-button size="small" @click="reset">重置</el-button>
      </div>
      <div class="pomo-presets">
        <el-radio-group v-model="workMinutes" size="small" :disabled="running">
          <el-radio-button :value="15">15</el-radio-button>
          <el-radio-button :value="25">25</el-radio-button>
          <el-radio-button :value="45">45</el-radio-button>
        </el-radio-group>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'

const expanded = ref(false)
const running = ref(false)
const workMinutes = ref(25)
const breakMinutes = 5
const isBreak = ref(false)
const timeLeft = ref(25 * 60)
const totalSeconds = computed(() => (isBreak.value ? breakMinutes : workMinutes.value) * 60)
const dashArray = computed(() => {
  const ratio = timeLeft.value / totalSeconds.value
  const circ = 2 * Math.PI * 42
  return `${(ratio * circ).toFixed(1)} ${circ.toFixed(1)}`
})

let timer = null

function formatTime(s) {
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`
}

function start() {
  if (timer) return
  running.value = true
  timer = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) {
      clearInterval(timer)
      timer = null
      running.value = false
      isBreak.value = !isBreak.value
      timeLeft.value = totalSeconds.value
      try {
        new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACAf39/f4B/f3+Af39/gH9/f4B/f3+Af39/gH9/f4B/f3+Af39/gH9/f4B/f3+Af39/gH9/f4AA==').play()
      } catch {}
      if (Notification.permission === 'granted') {
        new Notification(isBreak.value ? '休息时间！' : '番茄钟完成！', { body: isBreak.value ? '休息 5 分钟' : '休息一下' })
      }
    }
  }, 1000)
}

function pause() {
  clearInterval(timer)
  timer = null
  running.value = false
}

function reset() {
  pause()
  isBreak.value = false
  timeLeft.value = workMinutes.value * 60
}

onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.pomodoro-wrap {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  margin-top: 16px;
}
.pomodoro-header {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}
.pomo-icon { font-size: 16px; }
.pomo-label { font-size: 14px; font-weight: 600; color: var(--text-primary); flex: 1; }
.pomo-toggle { font-size: 11px; color: var(--text-muted); }
.pomodoro-body { text-align: center; padding-top: 14px; }
.pomo-ring { width: 160px; height: 160px; display: block; margin: 0 auto 10px; }
.pomo-time { font-size: 36px; font-weight: 700; color: var(--text-primary); font-variant-numeric: tabular-nums; }
.pomo-mode { font-size: 13px; color: var(--text-muted); margin-bottom: 12px; }
.pomo-controls { display: flex; gap: 8px; justify-content: center; margin-bottom: 12px; }
.pomo-presets { display: flex; justify-content: center; }
</style>
