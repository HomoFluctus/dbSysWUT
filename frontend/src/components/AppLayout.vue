<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="logo">Schedule</div>
      <nav>
        <router-link to="/" class="nav-item">Dashboard</router-link>
        <router-link to="/calendar" class="nav-item">Calendar</router-link>
        <router-link to="/schedules/new" class="nav-item">+ New Task</router-link>
        <router-link to="/categories" class="nav-item">Categories</router-link>
        <router-link to="/statistics" class="nav-item">Statistics</router-link>
      </nav>
      <div class="sidebar-footer">
        <span v-if="auth.user" class="user-name">{{ auth.user.username }}</span>
        <button @click="auth.logout" class="btn-logout">Logout</button>
      </div>
    </aside>
    <main class="main">
      <div class="top-bar">
        <div class="search-box">
          <input
            v-model="searchQuery"
            @keyup.enter="doSearch"
            placeholder="Search schedules..."
            class="search-input"
          />
        </div>
      </div>
      <div class="content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const router = useRouter()
const searchQuery = ref('')

function doSearch() {
  if (searchQuery.value.trim()) {
    router.push({ path: '/', query: { q: searchQuery.value.trim() } })
  }
}
</script>

<style scoped>
.layout { display: flex; min-height: 100vh; }
.sidebar {
  width: 220px; background: #1e293b; padding: 20px;
  display: flex; flex-direction: column; border-right: 1px solid #334155;
}
.logo { font-size: 22px; font-weight: 700; color: #818cf8; margin-bottom: 32px; }
nav { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.nav-item {
  display: block; padding: 10px 14px; border-radius: 8px; color: #94a3b8;
  font-size: 14px; transition: all 0.15s;
}
.nav-item:hover, .nav-item.router-link-active { background: #334155; color: #e2e8f0; }
.sidebar-footer { border-top: 1px solid #334155; padding-top: 16px; }
.user-name { display: block; font-size: 13px; color: #94a3b8; margin-bottom: 8px; }
.btn-logout {
  width: 100%; padding: 8px; background: #334155; color: #e2e8f0; border: none;
  border-radius: 6px; cursor: pointer; font-size: 13px;
}
.btn-logout:hover { background: #475569; }

.main { flex: 1; display: flex; flex-direction: column; }
.top-bar { padding: 16px 24px; border-bottom: 1px solid #1e293b; }
.search-input {
  width: 100%; max-width: 480px; padding: 10px 16px; border-radius: 8px;
  border: 1px solid #334155; background: #1e293b; color: #e2e8f0; font-size: 14px;
}
.search-input::placeholder { color: #64748b; }
.content { flex: 1; padding: 24px; overflow-y: auto; }
</style>
