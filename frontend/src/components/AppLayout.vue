<template>
  <div class="app-layout" @keydown="onKeydown" tabindex="-1" ref="layoutRef">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="logo-area">
        <el-icon :size="24" color="#818cf8"><Calendar /></el-icon>
        <span class="logo-text">日程管理</span>
      </div>

      <el-menu
        :default-active="activeRoute"
        router
        class="side-menu"
        background-color="transparent"
        text-color="#94a3b8"
        active-text-color="#e2e8f0"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>首页 &#x1f3e0;</span>
        </el-menu-item>
        <el-menu-item index="/focus">
          <el-icon><Aim /></el-icon>
          <span>专注模式 &#x1f3af;</span>
        </el-menu-item>
        <el-menu-item index="/calendar">
          <el-icon><Clock /></el-icon>
          <span>日历 &#x1f4c5;</span>
        </el-menu-item>
        <el-menu-item index="/schedules/new">
          <el-icon><CirclePlus /></el-icon>
          <span>新建日程 &#x2728;</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Folder /></el-icon>
          <span>分类管理 &#x1f4c2;</span>
        </el-menu-item>
        <el-menu-item index="/statistics">
          <el-icon><TrendCharts /></el-icon>
          <span>统计分析 &#x1f4ca;</span>
        </el-menu-item>
        <el-menu-item index="/kanban">
          <el-icon><DataBoard /></el-icon>
          <span>看板视图 &#x1f3af;</span>
        </el-menu-item>
        <el-menu-item index="/review">
          <el-icon><Notebook /></el-icon>
          <span>回顾 &#x1f4dd;</span>
        </el-menu-item>
        <el-menu-item index="/activity-log">
          <el-icon><Bell /></el-icon>
          <span>活动日志 &#x1f4c3;</span>
        </el-menu-item>
      </el-menu>

      <!-- Mascot -->
      <div class="mascot-area">
        <div class="mascot-bubble" :class="{ waving: mascotWave }" @click="mascotWave = !mascotWave">
          <span class="mascot-emoji">&#x1f438;</span>
          <span class="mascot-text">{{ mascotMessages[currentMsg] }}</span>
        </div>
      </div>

      <div class="sidebar-footer">
        <div class="user-info" v-if="auth.user">
          <el-avatar :size="32" :icon="UserFilled" />
          <span class="user-name">{{ auth.user.username }}</span>
        </div>
        <el-button text @click="auth.logout" class="logout-btn">
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-button>
      </div>
    </aside>

    <!-- Main content -->
    <main class="main">
      <header class="top-bar">
        <div class="top-left">
          <div class="quick-capture" ref="quickCaptureRef">
            <el-input
              ref="quickCaptureInputRef"
              v-model="quickCaptureText"
              placeholder="快速捕获... (Ctrl+Enter)"
              :prefix-icon="Plus"
              @keyup.enter="doQuickCapture"
              :disabled="quickCapturing"
              clearable
              size="default"
              class="quick-capture-input"
            />
          </div>
          <div class="search-box" ref="searchRef">
            <el-input
              ref="searchInputRef"
              v-model="searchQuery"
              placeholder="搜索日程... (/)"
              :prefix-icon="Search"
              @keyup.enter="doSearch"
              clearable
              class="search-input"
            />
          </div>
        </div>
        <div class="top-right">
          <el-tooltip :content="isDark ? '切换亮色' : '切换暗色'" placement="bottom">
            <el-button circle @click="toggleTheme" class="theme-btn">
              <el-icon :size="16"><component :is="isDark ? Sunny : Moon" /></el-icon>
            </el-button>
          </el-tooltip>
          <el-button circle @click="showShortcuts = true" class="help-btn">
            <el-icon :size="14"><QuestionFilled /></el-icon>
          </el-button>
        </div>
      </header>
      <div class="content">
        <router-view />
      </div>
    </main>

    <!-- Shortcuts help -->
    <el-dialog v-model="showShortcuts" title="键盘快捷键" width="380px">
      <table class="shortcut-table">
        <tr v-for="s in shortcuts" :key="s.key">
          <td class="shortcut-key"><kbd>{{ s.key }}</kbd></td>
          <td>{{ s.desc }}</td>
        </tr>
      </table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import { api } from '../utils/api.js'
import { ElMessage } from 'element-plus'
import {
  Calendar, HomeFilled, CirclePlus, Folder,
  TrendCharts, Search, SwitchButton, UserFilled, Clock, DataBoard,
  Sunny, Moon, QuestionFilled, Aim, Plus, Notebook, Bell,
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const searchQuery = ref('')
const searchInputRef = ref(null)
const searchRef = ref(null)
const layoutRef = ref(null)
const showShortcuts = ref(false)
const quickCaptureText = ref('')
const quickCaptureInputRef = ref(null)
const quickCapturing = ref(false)

const mascotWave = ref(false)
const currentMsg = ref(0)
const mascotMessages = [
  '今天也要加油哦！',
  '别忘了休息～',
  '你最棒了！',
  '又是元气满满的一天！',
  '记得喝水哦~',
  '今天完成了多少任务呀？',
]

// Cycle mascot messages
setInterval(() => {
  currentMsg.value = (currentMsg.value + 1) % mascotMessages.length
}, 15000)

const isDark = ref(true)
const shortcuts = [
  { key: 'N', desc: '新建日程' },
  { key: 'F', desc: '专注模式' },
  { key: 'K', desc: '看板视图' },
  { key: '/', desc: '聚焦搜索框' },
  { key: 'Ctrl+Enter', desc: '快速捕获' },
  { key: '?', desc: '显示快捷键帮助' },
]

const activeRoute = computed(() => {
  const p = route.path
  if (p.startsWith('/schedules') && p !== '/schedules/new') return '/'
  return ['/', '/focus', '/calendar', '/schedules/new', '/categories', '/statistics', '/kanban', '/review', '/activity-log'].includes(p) ? p : '/'
})

function doSearch() {
  if (searchQuery.value.trim()) {
    router.push({ path: '/', query: { q: searchQuery.value.trim() } })
  }
}

async function doQuickCapture() {
  const title = quickCaptureText.value.trim()
  if (!title || quickCapturing.value) return
  quickCapturing.value = true
  try {
    await api.createSchedule({ title })
    ElMessage.success('日程已创建')
    quickCaptureText.value = ''
  } catch (e) {
    ElMessage.error(e.message || '创建失败')
  } finally {
    quickCapturing.value = false
  }
}

function toggleTheme() {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

function onKeydown(e) {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
    if (e.ctrlKey && e.key === 'Enter') {
      e.preventDefault()
      doQuickCapture()
      return
    }
    if (e.key !== '/') return
    if (!searchInputRef.value) return
    e.preventDefault()
    searchInputRef.value.focus()
    return
  }
  if (e.ctrlKey && e.key === 'Enter') {
    e.preventDefault()
    quickCaptureInputRef.value?.focus()
  } else if (e.key === 'n' || e.key === 'N') {
    e.preventDefault()
    router.push('/schedules/new')
  } else if (e.key === 'f' || e.key === 'F') {
    e.preventDefault()
    router.push('/focus')
  } else if (e.key === 'k' || e.key === 'K') {
    e.preventDefault()
    router.push('/kanban')
  } else if (e.key === '/') {
    e.preventDefault()
    nextTick(() => searchInputRef.value?.focus())
  } else if (e.key === '?') {
    e.preventDefault()
    showShortcuts.value = true
  }
}

onMounted(() => {
  const saved = localStorage.getItem('theme')
  if (saved === 'light') {
    isDark.value = false
    document.documentElement.classList.remove('dark')
  }
  layoutRef.value?.focus()
})
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  outline: none;
}

.sidebar {
  width: 220px;
  background: var(--bg-surface);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 20px 16px;
}
.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #a5b4fc;
  letter-spacing: 1px;
}

.side-menu {
  flex: 1;
  border-right: none !important;
  padding: 0 8px;
}
.side-menu .el-menu-item {
  border-radius: 10px;
  margin-bottom: 2px;
  height: 44px;
  line-height: 44px;
  transition: all var(--transition-fast);
}
.side-menu .el-menu-item:hover {
  background: rgba(99,102,241,0.1) !important;
}
.side-menu .el-menu-item.is-active {
  background: rgba(99,102,241,0.2) !important;
  color: #a5b4fc !important;
}

.mascot-area {
  padding: 8px 12px;
}
.mascot-bubble {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(168,85,247,0.1));
  border-radius: 14px;
  cursor: pointer;
  transition: all var(--transition-fast);
  user-select: none;
}
.mascot-bubble:hover {
  background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(168,85,247,0.2));
  transform: scale(1.02);
}
.mascot-bubble.waving .mascot-emoji { animation: mascotBounce 0.5s ease; }
.mascot-emoji {
  font-size: 28px;
  flex-shrink: 0;
  transition: transform 0.3s ease;
}
@keyframes mascotBounce {
  0%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
  50% { transform: translateY(0); }
  70% { transform: translateY(-4px); }
}
.mascot-text {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.3;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-color);
}
.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.user-name {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}
.logout-btn {
  width: 100%;
  color: var(--text-muted) !important;
  justify-content: flex-start;
}

.main {
  flex: 1;
  margin-left: 220px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.top-bar {
  padding: 14px 28px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-surface);
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.top-left { flex: 1; display: flex; gap: 12px; align-items: center; }
.top-right { display: flex; gap: 8px; align-items: center; }
.quick-capture-input { width: 240px; }
.search-input {
  max-width: 420px;
}

.theme-btn, .help-btn {
  color: var(--text-muted) !important;
  border-color: var(--border-color) !important;
}

.content {
  flex: 1;
  padding: 28px;
}

.shortcut-table { width: 100%; border-collapse: collapse; }
.shortcut-table td { padding: 8px 4px; font-size: 14px; }
.shortcut-table kbd {
  display: inline-block;
  padding: 2px 8px;
  font-size: 12px;
  font-family: monospace;
  background: var(--bg-base);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-secondary);
}
</style>
