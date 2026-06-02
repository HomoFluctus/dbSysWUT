<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>Register</h1>
      <p class="subtitle">Create a new account</p>
      <form @submit.prevent="handleRegister">
        <input v-model="username" placeholder="Username" required />
        <input v-model="email" type="email" placeholder="Email" required />
        <input v-model="password" type="password" placeholder="Password" required />
        <input v-model="confirmPassword" type="password" placeholder="Confirm Password" required />
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="auth.loading">
          {{ auth.loading ? 'Creating...' : 'Create Account' }}
        </button>
      </form>
      <p class="link">Already have an account? <router-link to="/login">Sign In</router-link></p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth.js'

const auth = useAuthStore()
const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')

async function handleRegister() {
  error.value = ''
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }
  try {
    await auth.register(username.value, email.value, password.value)
  } catch (e) {
    error.value = e.message
  }
}
</script>

<style scoped>
.auth-page {
  display: flex; align-items: center; justify-content: center; min-height: 100vh;
  background: #0f172a;
}
.auth-card {
  background: #1e293b; padding: 40px; border-radius: 16px; width: 400px;
  border: 1px solid #334155;
}
h1 { font-size: 28px; color: #f1f5f9; margin-bottom: 4px; }
.subtitle { color: #64748b; margin-bottom: 28px; font-size: 14px; }
input {
  display: block; width: 100%; padding: 12px; margin-bottom: 14px;
  border-radius: 8px; border: 1px solid #334155; background: #0f172a;
  color: #e2e8f0; font-size: 14px;
}
button {
  width: 100%; padding: 12px; background: #6366f1; color: #fff; border: none;
  border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; margin-top: 8px;
}
button:hover { background: #4f46e5; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: #f87171; font-size: 13px; margin-bottom: 8px; }
.link { margin-top: 20px; text-align: center; font-size: 14px; color: #94a3b8; }
</style>
