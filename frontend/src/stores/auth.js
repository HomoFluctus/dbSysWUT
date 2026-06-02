import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../utils/api.js'
import router from '../router/index.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!localStorage.getItem('access_token'))

  async function login(username, password) {
    loading.value = true
    try {
      const data = await api.login({ username, password })
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      await fetchMe()
      router.push('/')
    } finally {
      loading.value = false
    }
  }

  async function register(username, email, password) {
    loading.value = true
    try {
      const data = await api.register({ username, email, password })
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      await fetchMe()
      router.push('/')
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    try {
      user.value = await api.getMe()
    } catch {
      logout()
    }
  }

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    user.value = null
    router.push('/login')
  }

  return { user, loading, isLoggedIn, login, register, fetchMe, logout }
})
