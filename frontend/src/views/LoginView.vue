<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <el-icon :size="40" color="#818cf8"><Calendar /></el-icon>
        <h1>日程管理系统</h1>
        <p>登录您的账户</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin" size="large">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="auth.loading" class="submit-btn">
            {{ auth.loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <p class="switch-link">
        还没有账户？<router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { User, Lock, Calendar } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  try {
    await auth.login(form.username, form.password)
  } catch (e) {
    ElMessage.error(e.message || '登录失败')
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: radial-gradient(ellipse at 50% -20%, rgba(99,102,241,0.15), transparent 70%),
              var(--bg-base);
}
.auth-card {
  width: 400px;
  padding: 44px 40px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.auth-header {
  text-align: center;
  margin-bottom: 32px;
}
.auth-header h1 {
  font-size: 24px;
  color: var(--text-primary);
  margin: 12px 0 4px;
}
.auth-header p {
  color: var(--text-muted);
  font-size: 14px;
}
.submit-btn {
  width: 100%;
}
.switch-link {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: var(--text-muted);
}
</style>
