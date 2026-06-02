<template>
  <div class="app-layout">
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
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/calendar">
          <el-icon><Clock /></el-icon>
          <span>日历</span>
        </el-menu-item>
        <el-menu-item index="/schedules/new">
          <el-icon><CirclePlus /></el-icon>
          <span>新建日程</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Folder /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/statistics">
          <el-icon><TrendCharts /></el-icon>
          <span>统计分析</span>
        </el-menu-item>
      </el-menu>

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
        <div class="search-box">
          <el-input
            v-model="searchQuery"
            placeholder="搜索日程..."
            :prefix-icon="Search"
            @keyup.enter="doSearch"
            clearable
            class="search-input"
          />
        </div>
      </header>
      <div class="content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import {
  Calendar, HomeFilled, CirclePlus, Folder,
  TrendCharts, Search, SwitchButton, UserFilled, Clock
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const searchQuery = ref('')

const activeRoute = computed(() => {
  const p = route.path
  if (p.startsWith('/schedules') && p !== '/schedules/new') return '/'
  return p === '/' || p === '/calendar' || p === '/schedules/new' || p === '/categories' || p === '/statistics' ? p : '/'
})

function doSearch() {
  if (searchQuery.value.trim()) {
    router.push({ path: '/', query: { q: searchQuery.value.trim() } })
  }
}
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
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
}
.search-input {
  max-width: 420px;
}

.content {
  flex: 1;
  padding: 28px;
}
</style>
